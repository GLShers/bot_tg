import asyncio
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from telethon import TelegramClient, events, functions, types
from g4f.client import Client
import app.keyboards as kb
import app.database.requests as rq
from concurrent.futures import ThreadPoolExecutor
import random
import logging
from datetime import datetime, timedelta

executor = ThreadPoolExecutor()
nero_router = Router()
client = None  # Глобальный клиент


def generate_prompt(post_text):
    return (
        f"Ты обычный пользователь Telegram, который пишет живые комментарии. "
        f"Реагируй неформально, с сетевым сленгом, иронией, но без перегибов. "
        f"Твой комментарий должен выглядеть так, будто его написала девушка. "
        f"Максимум одно-два предложения, без вопросов и выводов. "
        f"---\n{post_text}\n---\nНапиши только текст комментария. Если пост содержит что то связанное с наркотой, оружием, насилием, войной, Украиной то ты просто ставишь три точки и все!"
    )



def my_generate_prompt(post_text):
    return (
        f"Ты обычный пользователь Telegram, который пишет живые комментарии. "
        f"Реагируй неформально, с сетевым сленгом, иронией, но без перегибов. "
        f"Твой комментарий должен выглядеть так, будто его написала девушка. "
        f"Максимум одно-два предложения, без вопросов и выводов. "
        f"---\n{post_text}\n---\nНапиши только текст комментария. Если пост содержит что то связанное с наркотой, оружием, насилием, войной, Украиной то ты просто ставишь три точки и все!"
    )


def get_gpt_response(mes_text): 
    print("Отправляем запрос к GPT...")
    gpt_client = Client()
    
    try:
        response = gpt_client.chat.completions.create(
            model="deepseek-v3",
            messages=[{"role": "user", "content": mes_text}],
            web_search=False
        )
        print(f"Ответ от GPT: {response}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при запросе к GPT: {e}")
        return "Ошибка при запросе к GPT"
import logging
async def async_get_gpt_response(mes_text):
    print(f"Запрос GPT: {mes_text}")
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(executor, get_gpt_response, mes_text)
    print(f"Ответ от GPT (асинхронно): {response}")
    return response
# Поиск каналов с открытыми комментариями
async def find_channels_with_comments(client, query):
    print(f"Ищу каналы с открытыми комментариями по запросу: {query}")

    channels_info = []
    result = await client(functions.contacts.SearchRequest(q=query, limit=200))

    for user_or_channel in result.chats:
        try:
            if getattr(user_or_channel, 'broadcast', False):
                participants_count = getattr(user_or_channel, 'participants_count', 0)
                title = getattr(user_or_channel, 'title', 'Без названия')
                invite_link = f"t.me/{user_or_channel.username}" if getattr(user_or_channel, 'username', None) else None
                comments_available = await has_comments(client, user_or_channel)

                # Проверяем, что канал подходит по всем критериям
                if participants_count >= 500 and invite_link and comments_available:
                    # Проверяем, содержится ли ключевое слово в названии или описании
                    if query.lower() in title.lower():
                        channels_info.append(invite_link)  # Сохраняем только ссылку
        except Exception as e:
            print(f"Ошибка при обработке канала: {e}")

    random.shuffle(channels_info)
    return channels_info[:50]  # Возвращаем не более 50 каналов

# Проверка на открытые комментарии
async def has_comments(client, channel):
    try:
        full_channel = await client(functions.channels.GetFullChannelRequest(channel))
        linked_chat_id = getattr(full_channel.full_chat, 'linked_chat_id', None)
        can_comment = getattr(full_channel.full_chat, 'can_view_stats', False)

        # Если есть привязанная группа комментариев, проверяем, открытая ли она
        if linked_chat_id:
            linked_chat = await client.get_entity(linked_chat_id)
            # Проверяем, что группа не требует подачи заявки
            if not getattr(linked_chat, 'restricted', False):
                return True  # Группа открытая, можно комментировать

        # Если нет привязанной группы, но можно комментировать напрямую
        return can_comment
    except Exception as e:
        print(f"Ошибка при проверке комментариев для {channel}: {e}")
        return False

# Обработчик команды /parser
@nero_router.callback_query(F.data.startswith("parser"))
async def start_parser(callback: CallbackQuery):
    user = await rq.get_user_data(callback.from_user.id)
    sub = user.sub_id
    if sub == 1:
        await callback.answer("Извините, но для этого раздела нужна подписка (")
        return
    await callback.message.answer(
        "Введите слово для поиска каналов:",
        reply_markup=kb.main_button()
    )
    await callback.answer()

# Обработчик ввода слова для поиска
@nero_router.message(F.text & ~F.text.startswith("/") & F.text.startswith("#"))
async def handle_search_query(message: Message):
    user_id = message.from_user.id
    query = message.text

    # Получаем данные бота и пользователя
    bot = await rq.get_bot_data(user_id)
    user = await rq.get_user_data(user_id)

    if not user:
        await message.answer("⚠️ Пользователь не найден. Пожалуйста, зарегистрируйтесь.", reply_markup=kb.main_button())
        return

    if not bot:
        await message.answer("⚠️ Данные бота не найдены. Пожалуйста, свяжитесь с администратором.", reply_markup=kb.main_button())
        return

    # Создаем временного клиента для парсера
    try:
        async with TelegramClient(f"session_{user.bot_id}_{bot.link_bot}", bot.api_id, bot.hash_id) as client:
            # Ищем каналы
            channels = await find_channels_with_comments(client, query)

            if channels:
                result_message = "<b>📡 Найденные каналы:</b>\n\n"
                result_message += "\n".join(channels)  # Выводим ссылки через перенос строки
                await message.answer(result_message, parse_mode="HTML", reply_markup=kb.main_button())
            else:
                await message.answer("⚠️ Каналов с открытыми комментариями не найдено.", reply_markup=kb.main_button())
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при поиске каналов: {e}", reply_markup=kb.main_button())

# Заменим глобальную переменную на словарь
clients = {}

@nero_router.callback_query(F.data.startswith("run_bot"))
async def run_bot(callback: CallbackQuery):
    user = await rq.get_user_data(callback.from_user.id)
    sub = user.sub_id
    if sub ==1:
        await callback.answer("Извините, но для этого раздела нужна подписка (")
        return
    
    user_id = callback.from_user.id
    bot = await rq.get_bot_data(user_id)
    user = await rq.get_user_data(user_id)
    new_about = user.my_profile_description
    description = user.my_chanel_description  # Получаем описание канала
    API_ID = bot.api_id  
    API_HASH = bot.hash_id  
    CHANNEL_LINKS = await rq.get_chanels(user_id)

    # Проверяем, есть ли уже клиент для этого пользователя
    if user_id in clients and clients[user_id].is_connected():
        await callback.message.answer("⚠️ Бот уже работает для вашего аккаунта!")
        return
    
    # Создаем нового клиента только для этого пользователя
    client = TelegramClient(f"session_{bot.id}_{bot.link_bot}", API_ID, API_HASH)
    clients[user_id] = client  # Сохраняем клиента в словарь

    async def main():
        await client.start()
        entities = []
        await callback.message.edit_text(
            "<b>🚀 Запускаю процесс нейрокомментинга!</b>\n\n"
            "<i>Здесь тебе делать ничего не надо, просто оставь включенным и всё.</i>\n\n"
            "Как только комментарии будут оставлены, я тебя осведомлю. 🔍\n\n"
            "<b>✨ Ожидай обновлений!</b>\n\n"
            "<b>Если ты хочешь остановить бота или сделать что-то еще, нажми /stop_bot</b>",
            parse_mode="HTML",
        )
        
        await client(functions.account.UpdateProfileRequest(about=new_about))
        for link in CHANNEL_LINKS:
            try:
                entity = await client.get_entity(link)
                entities.append(entity)
                await asyncio.sleep(0.3)
                await callback.message.answer(f"✅ Мониторинг канала: {entity.title}")
            except ValueError:
                await callback.message.answer(f"❌ Ошибка: не удалось найти канал {link}")

        if not entities:
            await callback.message.answer("⚠️ Не удалось подключиться ни к одному каналу.")
            return

        @client.on(events.NewMessage(chats=entities))
        async def new_message_handler(event):
            chat_title = event.chat.title  
            message_id = event.message.id  
            chat_username = event.chat.username  
            mes = event.message
            post_url = f"https://t.me/{chat_username}/{message_id}" if chat_username else "Ссылка недоступна"

            # Сразу уведомляем пользователя о новом посте
            await callback.message.answer(
                f" <b>Новый пост в канале:</b> {chat_title}\n"
                f"🔗 <b>Ссылка на пост:</b> {post_url}\n"
                f"💬 <b>Комментарий оставлен</b>",  # <-- Закрываем тег <b>
                parse_mode="HTML"
            )

            comment_chat_id = None
            try:
                discussion_chat = await client(functions.messages.GetDiscussionMessageRequest(
                    peer=event.chat,
                    msg_id=message_id
                ))
                if discussion_chat.messages:
                    comment_chat_id = discussion_chat.messages[0].peer_id.channel_id
                    message_id = discussion_chat.messages[0].id
            except Exception as e:
                print(f"⚠️ Ошибка получения привязанного чата: {e}")

            if not comment_chat_id:
                try:
                    chat_full = await client(functions.channels.GetFullChannelRequest(event.chat))
                    if chat_full.full_chat.linked_chat_id:
                        comment_chat_id = chat_full.full_chat.linked_chat_id
                except Exception as e:
                    print(f"⚠️ Ошибка поиска привязанного чата через канал: {e}")

            if comment_chat_id:
                delay = random.randint(18, 60)
                print(f"⏳ Ожидание {delay} секунд перед комментарием...")
                await asyncio.sleep(delay)

                if user.sub_id == 3:
                    prompt = my_generate_prompt(mes.text or "Текст отсутствует")
                else:
                    prompt = generate_prompt(mes.text or "Текст отсутствует")

                comment_text = await async_get_gpt_response(prompt)
                print(f"Сгенерированный комментарий: {comment_text}")

                try:
                    await client.send_message(entity=comment_chat_id, message=comment_text, reply_to=message_id)
                    comment_status = "✅ Комментарий оставлен!"
                except Exception as e:
                    comment_status = f"❌ Ошибка отправки комментария: {e}"
            else:
                comment_status = "⚠️ У этого поста нет комментариев."

            # Уведомляем пользователя о результате отправки комментария

        await client.run_until_disconnected()

    await main()

@nero_router.message(Command("stop_bot"))
async def stop_bot(message: Message):
    user_id = message.from_user.id
    if user_id in clients and clients[user_id].is_connected():
        await clients[user_id].disconnect()
        del clients[user_id]  # Удаляем клиента из словаря
        await message.answer("⛔ Бот успешно остановлен!", reply_markup=kb.main_button())
    else:
        await message.answer("⚠️ Бот уже остановлен или не был запущен.", reply_markup=kb.main_button())

@nero_router.callback_query(F.data == "check_channels")
async def handle_check_channels(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Получаем данные пользователя и бота
    user = await rq.get_user_data(user_id)
    bot = await rq.get_bot_data(user_id)
    
    if not user or not bot:
        await callback.message.edit_text(
            "⚠️ Ошибка: не удалось получить данные пользователя или бота",
            reply_markup=kb.main_button()
        )
        return
        
    channels = await rq.get_chanels(user_id)
    if not channels:
        await callback.message.edit_text(
            "📝 У вас пока нет добавленных каналов для мониторинга",
            reply_markup=kb.main_button()
        )
        return
        
    # Отправляем начальное сообщение
    status_message = await callback.message.edit_text(
        "🔍 Начинаю проверку каналов...\n"
        "⏳ Пожалуйста, подождите..."
    )
    
    try:
        # Создаем клиент с данными из БД
        async with TelegramClient(
            f"sessions/session_{bot.id}_{bot.link_bot}",
            bot.api_id,
            bot.hash_id
        ) as client:
            
            results = []
            total = len(channels)
            checked = 0
            
            for channel in channels:
                checked += 1
                try:
                    # Обновляем статус проверки
                    await status_message.edit_text(
                        f"🔍 Проверка каналов...\n"
                        f"✓ Проверено: {checked}/{total}\n"
                        f"📊 Текущий канал: {channel}"
                    )
                    
                    # Проверяем существование канала
                    try:
                        entity = await client.get_entity(channel)
                        channel_title = getattr(entity, 'title', 'Без названия')
                    except ValueError:
                        results.append({
                            'channel': channel,
                            'status': '❌ Канал не найден',
                            'details': 'Возможно канал удален или ссылка неверна'
                        })
                        continue
                        
                    status_details = []
                    can_join = True  # Флаг для отслеживания возможности присоединения
                    
                    # Проверяем доступность комментариев
                    try:
                        full_channel = await client(functions.channels.GetFullChannelRequest(entity))
                        linked_chat_id = getattr(full_channel.full_chat, 'linked_chat_id', None)
                        
                        if linked_chat_id:
                            try:
                                linked_chat = await client.get_entity(linked_chat_id)
                                if getattr(linked_chat, 'restricted', False):
                                    status_details.append('❌ Группа комментариев закрыта')
                                    can_join = False
                                else:
                                    status_details.append('✅ Группа комментариев доступна')
                            except Exception as e:
                                status_details.append('❌ Ошибка доступа к группе комментариев')
                                can_join = False
                        else:
                            status_details.append('❌ Нет группы комментариев')
                            can_join = False
                            
                    except Exception as e:
                        status_details.append('❌ Ошибка проверки канала')
                        can_join = False
                    
                    # Если все проверки пройдены успешно, пробуем присоединиться
                    if can_join:
                        try:
                            # Присоединяемся к каналу
                            await client(functions.channels.JoinChannelRequest(entity))
                            status_details.append('✅ Успешно присоединились к каналу')
                            
                            # Присоединяемся к группе комментариев
                            if linked_chat_id:
                                await client(functions.channels.JoinChannelRequest(linked_chat))
                                status_details.append('✅ Успешно присоединились к группе комментариев')
                                
                        except Exception as e:
                            status_details.append('❌ Не удалось присоединиться к каналу или группе')
                            can_join = False
                    
                    results.append({
                        'channel': channel,
                        'title': channel_title,
                        'status': '✅ Доступен' if can_join else '❌ Недоступен',
                        'details': status_details
                    })
                    
                except Exception as e:
                    results.append({
                        'channel': channel,
                        'status': '❌ Ошибка проверки',
                        'details': str(e)
                    })
            
            # Формируем красивый вывод результатов
            output = "*📊 Результаты проверки каналов:*\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"*{i}. {result['channel']}*\n"
                if 'title' in result:
                    output += f"📢 Название: {result['title']}\n"
                output += f"📌 Статус: {result['status']}\n"
                
                if isinstance(result['details'], list):
                    output += "📋 Детали:\n"
                    for detail in result['details']:
                        output += f"   • {detail}\n"
                else:
                    output += f"📋 Детали: {result['details']}\n"
                output += "\n"
            
            # Добавляем общую статистику
            total_ok = sum(1 for r in results if '✅' in r['status'])
            total_warn = sum(1 for r in results if '⚠️' in r['status'])
            total_error = sum(1 for r in results if '❌' in r['status'])
            
            output += f"\n*📈 Общая статистика:*\n"
            output += f"✅ Полностью доступны: {total_ok}\n"
            output += f"⚠️ Есть проблемы: {total_warn}\n"
            output += f"❌ Недоступны: {total_error}\n"
            
            # Разбиваем сообщение на части, если оно слишком длинное
            max_length = 4096
            messages = [output[i:i+max_length] for i in range(0, len(output), max_length)]
            
            for i, message_part in enumerate(messages):
                if i == 0:
                    await status_message.edit_text(
                        message_part,
                        parse_mode="Markdown",
                        reply_markup=kb.main_button()
                    )
                else:
                    await callback.message.answer(
                        message_part,
                        parse_mode="Markdown"
                    )
                    
    except Exception as e:
        await status_message.edit_text(
            f"❌ Произошла ошибка при проверке каналов:\n{str(e)}",
            reply_markup=kb.main_button()
        )




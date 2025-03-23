import random
import asyncio
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from g4f.client import Client
import app.keyboards as kb
import app.database.requests as rq
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import g4f 

# Инициализация маршрутизатора
nero_test_router = Router()

# Класс состояний для FSM
class Rega(StatesGroup):
    waait = State()

# Функция для генерации промта для нейросети
def generate_prompt(post_text, media_type=None):
    # Добавляем информацию о типе медиа, если пост без текста
    if media_type:
        prompt = (
            f"Ты обычный пользователь Telegram, который пишет живые комментарии. "
            f"Реагируй неформально, с сетевым сленгом, иронией, но без перегибов. "
            f"Твой комментарий должен выглядеть так, будто его написала девушка. "
            f"Максимум одно-два предложения, без вопросов и выводов. Самое главное, чтобы комментарий выглядел так, как будто его написал человек. "
            f"Никогда не представляйся и не пиши в стиле AI. Никаких 'Как женщина, я считаю...' или 'С женской точки зрения'. Пиши сразу естественный комментарий. "
            f"---\n{post_text}\nЭто пост, содержащий {media_type} без текста. Напиши позитивный, дружелюбный комментарий, который уместен для поста с {media_type}.\n---\n"
            f"Напиши только текст комментария. Если пост может содержать что-то связанное с наркотиками, оружием, политикой, насилием, войной, Украиной, то ты просто ставишь три точки и все!"
        )
    else:
        prompt = (
            f"Ты обычный пользователь Telegram, который пишет живые комментарии. "
            f"Реагируй неформально, с сетевым сленгом, иронией, но без перегибов. "
            f"Твой комментарий должен выглядеть так, будто его написала девушка. "
            f"Максимум одно-два предложения, без вопросов и выводов. Самое главное, чтобы комментарий выглядел так, как будто его написал человек. "
            f"Никогда не представляйся и не пиши в стиле AI. Никаких 'Как женщина, я считаю...' или 'С женской точки зрения'. Пиши сразу естественный комментарий. "
            f"---\n{post_text}\n---\nНапиши только текст комментария. Если пост содержит что-то связанное с наркотиками, оружием, политикой, насилием, войной, Украиной, то ты просто ставишь три точки и все!"
        )
    return prompt

# Обработчик команды /run_bot
@nero_test_router.callback_query(F.data.startswith("test"))
async def com_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>🔍 Тестовый режим нейрокомментинга</b>\n\n"
        "Сейчас вы можете увидеть, как работает система генерации умных комментариев.\n\n"
        "<b>📱 Как это работает:</b>\n"
        "1️⃣ Перешлите сюда пост из любого канала\n"
        "2️⃣ Наша нейросеть проанализирует его содержание\n"
        "3️⃣ Вы увидите пример комментария, который генерирует бот\n\n"
        "<i>Просто перешлите сюда любой пост для генерации пробного комментария</i>",
        parse_mode="HTML", 
        reply_markup=kb.main_button()
    )
    await state.set_state(Rega.waait)

# Обработчик сообщений
@nero_test_router.message(Rega.waait)
async def process_link(message: Message, state: FSMContext):
    # Отправляем сообщение о начале обработки
    status_message = await message.answer(
        "<b>⏳ Анализирую сообщение и генерирую комментарий...</b>",
        parse_mode="HTML"
    )
    
    user = await rq.get_user_data(message.from_user.id)

    if not user:
        await status_message.edit_text("❌ Пользователь не найден в базе данных. Убедитесь, что вы зарегистрированы.")
        return
    
    description_chanel = user.my_chanel_description if hasattr(user, 'my_chanel_description') else None
    
    if not description_chanel:
        await status_message.edit_text(
            "❌ Не найдено описание вашего канала!\n\n"
            "Для работы нейрокомментинга необходимо добавить описание канала в вашем профиле."
        )
        return
    
    # Определяем тип содержимого
    post_test = ""
    media_type = None
    
    # Проверяем, если это пересланное сообщение
    if message.forward_from or message.forward_from_chat:
        # Проверка на наличие текста
        if message.text:
            post_test = message.text
        # Проверка на наличие подписи к медиа
        elif message.caption:
            post_test = message.caption
        # Определение типа медиа если нет текста
        elif message.photo:
            media_type = "фото"
            post_test = f"[Пост содержит фотографию без текста]"
        elif message.video:
            media_type = "видео"
            post_test = f"[Пост содержит видео без текста]"
        elif message.voice or message.audio:
            media_type = "аудио"
            post_test = f"[Пост содержит аудиосообщение без текста]"
        elif message.document:
            media_type = "файл"
            post_test = f"[Пост содержит файл без текста]"
        elif message.animation:
            media_type = "GIF/анимация"
            post_test = f"[Пост содержит GIF-анимацию без текста]"
        elif message.sticker:
            media_type = "стикер"
            post_test = f"[Пост содержит стикер]"
        else:
            # Для других типов сообщений
            media_type = "медиа-контент"
            post_test = f"[Пост содержит медиа-контент без текста]"
    else:
        # Если не переслано, просто берем текст или определяем тип медиа
        if message.text:
            post_test = message.text
        elif message.caption:
            post_test = message.caption
        elif message.photo:
            media_type = "фото"
            post_test = f"[Сообщение содержит фотографию без текста]"
        elif message.video:
            media_type = "видео"
            post_test = f"[Сообщение содержит видео без текста]"
        elif message.voice or message.audio:
            media_type = "аудио"
            post_test = f"[Сообщение содержит аудио без текста]"
        else:
            # Для других типов сообщений
            media_type = "медиа-контент"
            post_test = f"[Сообщение содержит медиа-контент без текста]"

    if len(post_test) > 1500:
        await status_message.edit_text(
            "❌ Слишком большой текст!\n\n"
            "В тестовом режиме работаем с текстами до 1500 символов."
        )
        return
    
    # Обновляем статус и указываем тип медиа, если есть
    if media_type:
        await status_message.edit_text(
            f"<b>🧠 Анализирую содержимое поста с {media_type}...</b>\n\n"
            f"Это займет несколько секунд.",
            parse_mode="HTML"
        )
    else:
        await status_message.edit_text(
            "<b>🧠 Нейросеть анализирует содержание...</b>\n\n"
            "Это займет несколько секунд.",
            parse_mode="HTML"
        )
    
    prompt = generate_prompt(post_test, media_type)

    try:
        # Обновляем статус перед запросом к GPT
        await asyncio.sleep(1.5)  # Небольшая задержка для более реалистичного ощущения работы
        await status_message.edit_text(
            "<b>✨ Создаю оптимальный комментарий...</b>",
            parse_mode="HTML"
        )
        
        response = await g4f.ChatCompletion.create_async(
            model="deepseek-v3",
            messages=[
                {"role": "system", "content": "You are a business man."},
                {"role": "user", "content": prompt}
            ]
        )
        
        print("Ответ GPT:", response)

        comment = response if isinstance(response, str) else "Произошла ошибка: неверный формат ответа."

        # Отправляем результат аналитики
        await status_message.edit_text(
            f"<b>✅ Готово! Пример комментария:</b>\n\n"
            f"<i>\"{comment}\"</i>",
            parse_mode="HTML"
        )

        # Информация о полной версии
        await message.answer(
            "🔥 <b>Впечатляет, правда?</b>\n\n"
            "Это лишь демонстрация возможностей нейрокомментинга. С полной версией бот будет:\n\n"
            "• Автоматически отслеживать новые посты 24/7\n"
            "• Составлять релевантные комментарии с учетом тематики\n"
            "• Публиковать их от имени наших аккаунтов с вашей ссылкой на канал\n"
            "• Привлекать новую аудиторию на ваш канал\n\n"
            "<b>💎 Один бот заменяет целую команду комментаторов!</b>",
            parse_mode="HTML",
            reply_markup=kb.subscription_offer_keyboard()
        )

    except Exception as e:
        await status_message.edit_text(f"❌ Произошла ошибка при генерации комментария: {e}")
        
    finally:
        # Сбрасываем состояние
        await state.clear()
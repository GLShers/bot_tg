import random
import asyncio
import time
from collections import defaultdict
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

# Словарь для хранения времени последней обработки для каждого пользователя
# ключ - user_id, значение - время последней обработки в секундах
last_processed_time = defaultdict(float)
# Словарь для хранения последней обработанной медиа-группы
last_media_group = defaultdict(str)
# Словарь для хранения текста медиа-группы
media_group_text = defaultdict(dict)
# Минимальный интервал между обработками сообщений (в секундах)
MIN_PROCESS_INTERVAL = 5  # Увеличиваем интервал для больших альбомов

# Класс состояний для FSM
class Rega(StatesGroup):
    waait = State()

# Функция для генерации промта для нейросети
def generate_prompt(post_text):
    # Всегда работаем только с текстом, игнорируя медиа-контент
    prompt = (
        f"Ты обычная девушка 20-35 лет, которая пишет комментарии в Telegram-каналах. "
        f"ВАЖНО: Комментарий должен быть максимально похожим на те, что пишут реальные люди. "
        f"Вот правила, которым ты должна следовать: "
        f"1. Используй живой и эмоциональный язык. Пиши просто и неформально, как будто быстро печатаешь на телефоне. "
        f"2. Пиши коротко - 1-2 предложения максимум. Длинные комментарии выглядят неестественно. "
        f"3. Добавляй эмоджи, но не слишком много (0-2 эмоджи на комментарий). "
        f"4. Иногда используй многоточия, сокращения (норм, че, спс), восклицательные знаки! "
        f"5. Изредка делай опечатки, но не слишком очевидные и не в каждом сообщении. "
        f"6. Можешь использовать мемные фразы, молодежный сленг. "
        f"7. НЕ пиши стандартных фраз типа 'очень интересно', 'как атмосферно', 'вау, впечатляет'. "
        f"8. НЕ используй фразы 'спасибо за информацию', 'класс', 'супер' - они сразу выдают бота. "
        f"9. НЕ пиши фразы, которые анализируют или оценивают что-то - такие обобщения выдают ИИ. "
        f"10. Никаких приветствий и обращений к автору. "
        f"11. Реагируй на конкретные детали в тексте, если они есть. "
        
        f"Вот примеры хороших, естественных комментариев: "
        f"- блин, реально так и есть( "
        f"- как же захотелось теперь это попробовать... 🙈 "
        f"- ну наконец-то кто-то это сказал "
        f"- у меня точно такая же фигня была в прошлом году "
        f"- вот жеж как бывает... "
        f"- бомба 🔥 "
        f"- чет я ржу)) "
        
        f"Вот примеры ПЛОХИХ, неестественных комментариев (НЕ ИСПОЛЬЗУЙ): "
        f"- 'Очень интересно и познавательно!' "
        f"- 'Какая атмосфера, прям вдохновляет!' "
        f"- 'Ух ты, как классно! Это поднимает настроение!' "
        f"- 'Спасибо за информацию, очень полезно!' "
        
        f"---\n{post_text}\n---\n"
        
        f"Напиши ТОЛЬКО ОДИН комментарий - максимально естественный, короткий, эмоциональный, будто его написала реальная девушка, которая быстро отреагировала на пост. "
        f"НЕ стремись быть вежливой или культурной - пиши так, как пишут люди в интернете. "
        f"ВНИМАНИЕ: если пост содержит что-то связанное с наркотиками, оружием, политикой, насилием, войной, Украиной или другие потенциально спорные/сенситивные темы - НЕ пиши комментарий, "
        f"а вместо этого напиши специальную метку: '[СЕНСИТИВНЫЙ_КОНТЕНТ]'. Эта метка будет распознана системой."
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
    user_id = message.from_user.id
    current_time = time.time()
    has_text = bool(message.text or message.caption)
    
    # Если сообщение является частью медиа-группы
    if message.media_group_id:
        # Если это первое сообщение из группы, которое мы видим
        if message.media_group_id not in media_group_text.get(user_id, {}):
            media_group_text.setdefault(user_id, {})[message.media_group_id] = {
                'has_message_with_text': has_text,
                'text': message.text or message.caption or '',
                'first_message': message,
                'time': current_time
            }
        # Если это не первое сообщение из группы
        else:
            group_data = media_group_text[user_id][message.media_group_id]
            # Если текущее сообщение имеет текст, а предыдущее нет - обновляем информацию
            if has_text and not group_data['has_message_with_text']:
                group_data['has_message_with_text'] = True
                group_data['text'] = message.text or message.caption
                group_data['first_message'] = message  # Обновляем сообщение на то, которое содержит текст
            
            # Если с момента первого сообщения группы прошло достаточно времени и мы нашли сообщение с текстом
            if current_time - group_data['time'] > 2 and group_data['has_message_with_text']:
                # Обрабатываем сохраненное сообщение с текстом, только если оно еще не обрабатывалось
                if message.media_group_id != last_media_group.get(user_id):
                    last_media_group[user_id] = message.media_group_id
                    # Обрабатываем только если прошло достаточно времени с последней обработки
                    if current_time - last_processed_time.get(user_id, 0) > MIN_PROCESS_INTERVAL:
                        last_processed_time[user_id] = current_time
                        # Обрабатываем сообщение с текстом из группы
                        await process_message_content(group_data['first_message'], state, group_data['text'])
                return  # В любом случае выходим, чтобы не обрабатывать другие сообщения из группы
            
            # Продолжаем ждать, может появится сообщение с текстом
            return
    
    # Защита от спама/дублирования для одиночных сообщений
    if current_time - last_processed_time.get(user_id, 0) < MIN_PROCESS_INTERVAL:
        print(f"Игнорирую сообщение от пользователя {user_id} - интервал слишком мал")
        return
    
    # Обрабатываем одиночное сообщение
    last_processed_time[user_id] = current_time
    
    # Отправляем на обработку
    post_text = message.text or message.caption or "Пост без текста"
    await process_message_content(message, state, post_text)

# Функция обработки контента сообщения
async def process_message_content(message, state, post_text):
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

    if len(post_text) > 1500:
        await status_message.edit_text(
            "❌ Слишком большой текст!\n\n"
            "В тестовом режиме работаем с текстами до 1500 символов."
        )
        return
    
    # Обновляем статус - обрабатываем ТОЛЬКО текст
    await status_message.edit_text(
        "<b>🧠 Нейросеть анализирует содержание текста...</b>\n\n"
        "Это займет несколько секунд.",
        parse_mode="HTML"
    )
    
    # Генерируем промпт только для текста
    prompt = generate_prompt(post_text)

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
        
        # Проверяем, содержит ли ответ метку о сенситивном контенте
        if "[СЕНСИТИВНЫЙ_КОНТЕНТ]" in comment or comment == "..." or comment.strip() == "":
            # Отправляем предупреждение о сенситивном контенте
            await status_message.edit_text(
                "<b>⚠️ Внимание!</b>\n\n"
                "Ваш пост содержит <b>сенситивный контент</b> (политика, насилие, оружие и т.п.).\n\n"
                "Согласно нашим правилам сервиса, мы не можем генерировать комментарии для такого контента.\n\n"
                "Пожалуйста, отправьте другой пост или вернитесь в главное меню.",
                parse_mode="HTML",
                reply_markup=kb.sensitive_content_keyboard()  # Здесь нужно создать клавиатуру с соответствующими кнопками
            )
        else:
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
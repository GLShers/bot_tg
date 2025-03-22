from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
from datetime import datetime, timedelta
from aiogram.exceptions import TelegramBadRequest
import os
from aiogram.types import FSInputFile
from typing import Union

from app.database import requests as rq
import app.keyboards as kb

from aiogram.fsm.state import State, StatesGroup

class Reg(StatesGroup):
    home = State()
    name = State()
    phone = State()
    waiting_link = State()
    waiting_add = State()

class EditChannelState(StatesGroup):    
    waiting_for_new_link = State()
    chanel_wait = State()
    des_chanel_wait = State()
    des_profile_wait = State()
    waiting_tg_id = State()
    waiting_for_channel_description = State()
    waiting_for_profile_description = State()
    waiting_for_link_update = State()

class Step(StatesGroup):
    des_profile = State()
    des_chanel = State()   
    link = State()
    wait_style = State()
    style = State()
    all_ready = State()
    add_chanels = State()
    slep = State()
    period_com = State()
    sleep_bot = State()
    sleep_sleep = State()
    launch_bot = State()
    all_ready_go = State() 


    
router = Router()




#⁡⁢⁣⁢----------------------------------------------------------------------------------------СТАРТОВЫЕ-КОМАНДЫ-------------------------------------------------------------------------------------------------⁡
@router.message(CommandStart())
async def com_start(message: Message, state: FSMContext):
    # Проверяем, настроен ли уже профиль пользователя
    await rq.set_user(message.from_user.id)
    await rq.set_login(message.from_user.id, message.from_user.username)
    user = await rq.get_user_data(message.from_user.id)
    
    # Проверяем, заполнен ли профиль пользователя полностью
    is_profile_fully_filled = user.link and user.my_chanel_description and user.my_profile_description
    
    if is_profile_fully_filled:
        # Если профиль уже настроен, показываем домашнюю страницу
        welcome_text = (
            f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
            f"🎯 <b>Ваш центр управления</b>\n\n"
            f"✨ <b>Доступные действия:</b>\n"
            f"👤 Редактировать профиль\n"
            f"⭐ Смотреть отзывы\n"
            f"💎 Управлять подпиской\n"
            f"🚀 Запускать бота\n\n"
            f"💡 <i>Выберите нужный раздел на панели управления</i>"
        )
        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=kb.home_page()
        )
        return

    # Если профиль не настроен, показываем стандартное приветствие
    # Получаем путь к видео
    current_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(current_dir, "..", "video", "first.mp4")

    # Проверяем, существует ли файл
    if os.path.exists(video_path):
        video_msg = await message.answer_video(
            video=FSInputFile(video_path),
            caption="<b>Нейрокомментинг</b>",
            parse_mode="HTML"
        )
        await state.update_data(video_message_id=video_msg.message_id)
    welcome_text = (
        
    )
    
    await message.answer(
        "<b>👋 Добро пожаловать в бота для нейрокомментинга!</b>\n\n"
        "✅ <b>Что умеет бот:</b>\n"
        "• Автоматический анализ постов\n"
        "• Генерация релевантных комментариев\n"
        "• Работа с несколькими каналами\n"
        "• Настройка расписания комментирования\n\n"
        "🚀 <b>Начните прямо сейчас:</b>\n"
        "1. Настройте свой профиль\n"
        "2. Добавьте каналы для мониторинга\n"
        "3. Выберите стиль комментариев\n",
        parse_mode="HTML",
        reply_markup=kb.start()
    )

    
    
@router.callback_query(F.data.startswith("pre_start"))
async def com_start(callback: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    video_message_id = data.get("video_message_id")

    # Удаляем сообщение с видео, если оно существует
    if video_message_id:
        try:
            await callback.bot.delete_message(callback.message.chat.id, video_message_id)
        except Exception as e:
            print(f"Ошибка при удалении видео: {e}")

    await state.clear()
    user = await rq.get_user_data(callback.from_user.id)
    sub = user.sub_id

    await callback.message.edit_text("Главное меню бота. Здесь вы можете редактировать свой профиль",
                                    parse_mode="HTML",
                                    reply_markup=kb.main_keyboard_2())

 #⁡⁢⁣⁢----------------------------------------------------------------------------------------------------------------------------------------------------------------------------⁡
@router.callback_query(F.data.startswith("start"))
async def com_start(callback: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    video_message_id = data.get("video_message_id")

    # Удаляем сообщение с видео, если оно существует
    

    await state.clear()
    user = await rq.get_user_data(callback.from_user.id)

    # Проверяем, заполнен ли профиль пользователя полностью
    is_profile_fully_filled = user.link and user.my_chanel_description and user.my_profile_description
    
    if is_profile_fully_filled:
        await callback.message.answer("Ваш профиль уже настроен", reply_markup=kb.go())
        await state.set_state(Step.all_ready_go)
        return

    # Устанавливаем флаг для проверки заполненности профиля в состояние
    # Поскольку пользователь только начинает настройку, профиль не заполнен
    await state.update_data(is_profile_fully_filled=False)

    # Отправляем новое сообщение
    msg = await callback.message.answer("<b>Введите ссылку на свой канал. </b>\n\n"
                                        " В процессе нейрокомментинга люди будут переходить именно на него!", parse_mode="HTML")
    await state.update_data(last_message_id=msg.message_id)  # Сохраняем ID сообщения для удаления
    await state.set_state(Step.link)
    
    
    
@router.message(Step.link) # Обработчик ввода ссылки на канал
async def process_link(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    
    # Удаляем предыдущее сообщение
    if last_message_id:
        await message.bot.delete_message(message.chat.id, last_message_id)
    
    new_link = message.text

    if len(new_link) > 35:
        msg = await message.answer("Ошибка! Ссылка не должна превышать 35 символов. Попробуйте снова.")
        await state.update_data(last_message_id=msg.message_id)
        return
    
    if not new_link.startswith("t.me/"):
        msg = await message.answer("Ошибка! Ссылка на канал должна начинаться с t.me/. Попробуйте снова.")
        await state.update_data(last_message_id=msg.message_id)
        return

    succeful_add = await rq.add_link(message.from_user.id, new_link)

    if succeful_add:
        msg = await message.answer("✅ Ваша ссылка успешно добавлена!")
    else:
        msg = await message.answer("⚠️ Данная ссылка уже была добавлена ранее.")
    
    await state.update_data(last_message_id=msg.message_id)
    photo_path = os.path.join(os.getcwd(), "photo", "des_chanel.jpg")
        
        # Проверяем, существует ли файл
    if not os.path.exists(photo_path):
        await message.answer("Фото не найдено! Пожалуйста, проверьте путь к файлу.")
        return
        
        # Используем FSInputFile для отправки локального файла
    photo = FSInputFile(photo_path)
    photo_msg = await message.answer_photo(photo=photo)
        
    msg = await message.answer(
        "<b>В этом разделе Вам нужно описать свой канал.</b>\n\n"
        "Необходимо для генерации комментариев в вашем стиле.",
        parse_mode="HTML"
    )
    await state.update_data(last_message_id=msg.message_id)
    await state.update_data(last_photo_id=photo_msg.message_id)
    await state.set_state(Step.des_chanel)



@router.message(Step.des_chanel)  # Обработчик ввода описания канала
async def process_new_des_chanel(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    last_photo_id = data.get("last_photo_id")  # ID последнего отправленного фото
    
    # Удаляем предыдущее сообщение и фото (если они есть)
    if last_message_id:
        await message.bot.delete_message(message.chat.id, last_message_id)
    if last_photo_id:
        await message.bot.delete_message(message.chat.id, last_photo_id)
    
    new_des_chanel = message.text.strip() 
    words_count = len(new_des_chanel.split())  
    
    if len(message.text) > 700:
        msg = await message.answer("Слишком много символов(")
        await state.update_data(last_message_id=msg.message_id)
    else:
        existing_description = await rq.update_chanel_description(message.from_user.id, new_des_chanel)
        msg = await message.answer(f"✅ Успешно добавил в базу твое описание", parse_mode="HTML")
        
        await state.update_data(last_message_id=msg.message_id)
        
        msg = await message.answer(
            "<b>Опиши профиль для бота.</b>\n\n 70 символов + ссылка на ваш канал. Пример как на фото ниже\n"
            "Оно разместится в биографии аккаунта, от имени которого бот будет оставлять комментарии.\n\n",
            parse_mode="HTML"
        )
        
        photo_path = os.path.join(os.getcwd(), "photo", "des_profile.jpg")
        
        # Проверяем, существует ли файл
        if not os.path.exists(photo_path):
            await message.answer("Фото не найдено! Пожалуйста, проверьте путь к файлу.")
            return
        
        # Используем FSInputFile для отправки локального файла
        photo = FSInputFile(photo_path)
        photo_msg = await message.answer_photo(photo=photo)
        
        # Сохраняем ID сообщения с фото
        await state.update_data(last_photo_id=photo_msg.message_id)
        await state.set_state(Step.des_profile)

@router.message(Step.des_profile)  # Обработчик ввода описания профиля
async def process_new_des_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    last_photo_id = data.get("last_photo_id")  # ID последнего отправленного фото
    
    # Удаляем предыдущее сообщение и фото (если они есть)
    if last_message_id:
        await message.bot.delete_message(message.chat.id, last_message_id)
    if last_photo_id:
        await message.bot.delete_message(message.chat.id, last_photo_id)
    
    new_des_profile = message.text.strip()
    
    if len(new_des_profile) > 70:
        msg = await message.answer("Слишком много слов(")
        await state.update_data(last_message_id=msg.message_id)
    else:
        existing_description = await rq.add_profile_description(message.from_user.id, new_des_profile)
        
        if existing_description and existing_description != True:
            msg = await message.answer(f"У тебя уже есть описание профиля:\n\n<b>{existing_description}</b>", parse_mode="HTML")
        else:
            msg = await message.answer(f"✅ Успешно добавил в базу твое описание профиля", parse_mode="HTML")
        
        await state.update_data(last_message_id=msg.message_id)
        
        # Получаем данные пользователя, чтобы проверить заполненность профиля
        user = await rq.get_user_data(message.from_user.id)
        
        # Проверяем, заполнен ли профиль пользователя полностью
        is_profile_fully_filled = user.link and user.my_chanel_description and user.my_profile_description
        
        # Отправляем текстовое сообщение
        msg = await message.answer(
            "<b>Теперь ты в разделе выбора стиля комментариев.</b>\n\n"
            "🔹 <b>Стиль Сета Година (Маркетинг и продажи)</b>\n"
            "Этот стиль идеально подходит для тех, кто хочет привлекать аудиторию и продавать через личный бренд. "
            "Минимум воды, четкое УТП (уникальное торговое предложение), призыв к действию.\n\n"
            "🔹 <b>Стиль Гая Кавасаки (Привлечение внимания)</b>\n"
            "Подходит для блогеров, инфлюенсеров, людей, которым важно удерживать внимание. "
            "Добавляем эмоции, немного провокации, задаем интригу.\n\n"
            "🔹 <b>Стиль Илона Маска (Экспертность и технологии)</b>\n"
            "Если твой канал про технологии, инвестиции или у тебя экспертный контент, лучше придерживаться этого стиля. "
            "Простые слова, но глубокий смысл, намек на будущее и инновации.\n\n"
            "📌 <i>Выбери стиль, который лучше всего подходит твоему каналу.</i>",
            parse_mode="HTML",
            reply_markup=kb.style()
        )
        
        # Сохраняем ID сообщения и флаг заполненности профиля
        await state.update_data(last_message_id=msg.message_id, is_profile_fully_filled=is_profile_fully_filled)
        
        # Важно: используем set_state вместо clear, чтобы сохранить данные
        await state.set_state(None)

@router.callback_query(F.data.startswith("go_style"))
async def com_start(callback: CallbackQuery, state: FSMContext):
    # Удаляем предыдущее сообщение
    await callback.message.delete()
    
    # Отправляем новое сообщение
    msg = await callback.message.answer(
        "✅ <b>Отлично!</b>\n\n"
        "Добавил Ваш стиль в базу данных\n\n"
        "Теперь давайте добавим каналы для мониторинга.\n\n"
        f'Введите ссылки на каналы в виде "t.me/название_канала" без кавычек.\n'
        f'Вы можете ввести несколько каналов сразу, разделяя их пробелами.\n\n'
        f'<i>Если закончили, нажмите кнопку "Достаточно"</i>',
        parse_mode="HTML",
        reply_markup=kb.neiro_chanels()
    )
    # Так как этот обработчик вызывается только при первичной настройке,
    # устанавливаем флаг is_profile_fully_filled=False
    await state.update_data(last_message_id=msg.message_id, is_profile_fully_filled=False)
    await state.set_state(Step.add_chanels)


async def delete_message_safe(bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")


# Обработчик ввода каналов
@router.callback_query(F.data.startswith("add_chanels"))
async def handle_add_channels_callback(callback: CallbackQuery, state: FSMContext):
    # Получаем данные пользователя
    user = await rq.get_user_data(callback.from_user.id)
    
    # Поскольку пользователь нажал на кнопку "Добавить каналы" в меню редактирования профиля,
    # мы точно знаем, что это редактирование профиля, а не первичная настройка
    # Устанавливаем is_profile_fully_filled=True
    
    # Получаем текущие данные пользователя
    max_channels = await rq.get_sub_max(callback.from_user.id)
    current_count = await rq.count_channels_for_user(callback.from_user.id)
    remaining = max_channels - current_count
    
    # Получаем список текущих каналов
    channels = await rq.get_chanels(callback.from_user.id)
    
    # Формируем сообщение с текущими каналами
    channels_text = "📢 <b>Ваши текущие каналы:</b>\n\n"
    for i, channel in enumerate(channels, 1):
        channels_text += f"{i}. {channel}\n"
    
    channels_text += f"\n📊 <b>Статистика:</b>\n"
    channels_text += f"• Добавлено каналов: {current_count}\n"
    channels_text += f"• Осталось слотов: {remaining}\n"
    channels_text += f"• Максимум каналов: {max_channels}\n\n"
    
    # Проверяем, достигнут ли лимит каналов
    if remaining == 0:
        await callback.message.edit_text(
            f"<b>🎯 Вы добавили максимальное количество каналов ({max_channels})!</b>\n\n"
            f"<i>Нажмите 'Достаточно', чтобы вернуться в центр управления.</i>",
            parse_mode="HTML",
            reply_markup=kb.neiro_chanels()
        )
        await state.set_state(Step.add_chanels)
        # Это редактирование профиля
        await state.update_data(is_profile_fully_filled=True)
        return
    else:
        await callback.message.edit_text(
            f"<b>✅ Текущие каналы:</b>\n\n"
            f"{channels_text}\n"
            f"<i>Отправь мне t.me/имя_канала, чтобы добавить новый канал для мониторинга.</i>\n"
            f"<i>Или нажми 'Достаточно', если больше не хочешь добавлять каналы.</i>",
            parse_mode="HTML",
            reply_markup=kb.neiro_chanels()
        )
        await state.set_state(Step.add_chanels)
        # Это редактирование профиля
        await state.update_data(is_profile_fully_filled=True)


@router.message(Step.add_chanels)
async def add_chanels(message: Message, state: FSMContext):
    # Получаем текущие данные пользователя
    user = await rq.get_user_data(message.from_user.id)
    max_channels = await rq.get_sub_max(message.from_user.id)
    current_count = await rq.count_channels_for_user(message.from_user.id)
    remaining = max_channels - current_count
    text = message.text.strip().lower()
    
    # Получаем данные из состояния
    data = await state.get_data()
    is_initial_setup = not data.get("is_profile_fully_filled", True)
    
    # Если пользователь нажал "Достаточно"
    if text == "достаточно":
        if current_count == 0:
            msg = await message.answer("Ты должен ввести хотя бы один канал перед тем, как нажать 'Достаточно'.")
            await state.update_data(last_message_id=msg.message_id)
            return
        else:
            # Если это первичная настройка (на основе флага из состояния)
            if is_initial_setup:
                # Это первичная настройка - показываем сообщение перед анимацией
                msg = await message.answer(
                    "✅ <b>Каналы успешно добавлены!</b>\n\n"
                    "⏳ <i>Сейчас будет создан ваш профиль...</i>",
                    parse_mode="HTML"
                )
                await asyncio.sleep(1)  # Небольшая пауза для улучшения опыта
                # Запускаем анимацию создания профиля
                await state.set_state(Step.all_ready)
                await all_ready(message, state)
            else:
                # Это редактирование профиля - возвращаемся в центр управления
                channels = await rq.get_chanels(message.from_user.id)
                msg = await message.answer(
                    f"✅ <b>Каналы успешно добавлены!</b>\n\n"
                    f"📊 <b>Текущая статистика:</b>\n"
                    f"• Всего каналов для мониторинга: {len(channels)}\n\n"
                    f"<i>Вы можете продолжить работу с основного меню</i>",
                    parse_mode="HTML",
                    reply_markup=kb.main_keyboard_3()
                )
                await state.clear()
            return

    # Разделение введённых каналов
    channels = text.split()

    added_channels = 0
    for channel in channels:
        # Проверка формата ссылки
        if not channel.startswith("t.me/"):
            msg = await message.answer("Ссылка должна начинаться с t.me/ (например, t.me/название_канала). Попробуй снова.", reply_markup=kb.neiro_chanels())
            await state.update_data(last_message_id=msg.message_id)
            return

        # Проверка длины ссылки
        if len(channel) > 35:
            msg = await message.answer("Ссылка не должна превышать 35 символов. Попробуй снова.", reply_markup=kb.neiro_chanels())
            await state.update_data(last_message_id=msg.message_id)
            return

        # Добавление канала, если осталось место
        if remaining > 0:
            added = await rq.add_chanels(message.from_user.id, channel)
            if added:
                remaining -= 1
                added_channels += 1
            else:
                msg = await message.answer(f"Канал {channel} уже добавлен. Введи другой.", reply_markup=kb.neiro_chanels())
                await state.update_data(last_message_id=msg.message_id)
        else:
            break

    # Ответ пользователю
    if added_channels > 0:
        if remaining > 0:
            msg = await message.answer(
                f'✅ Ссылки сохранены! Осталось ещё {remaining} каналов.\n'
                f'Отправь ещё каналы или нажми "Достаточно".', reply_markup=kb.neiro_chanels()
            )
        else:
            # Если лимит каналов достигнут, показываем соответствующее сообщение
            msg = await message.answer(
                "✅ Ссылки сохранены! Вы достигли лимита каналов.\n"
                "Нажмите 'Достаточно' для возврата в центр управления.", 
                reply_markup=kb.neiro_chanels()
            )
    else:
        msg = await message.answer(
            "Ты не добавил новые каналы. Попробуй снова или нажми 'Достаточно'.", reply_markup=kb.neiro_chanels()
        )
    await state.update_data(last_message_id=msg.message_id)

    # Проверяем, нужно ли автоматически перейти к созданию профиля
    # Только для первичной настройки и только при достижении лимита
    if remaining == 0 and is_initial_setup:
        # Сообщаем пользователю о переходе к созданию профиля
        msg = await message.answer(
            f"<b>🎯 Вы добавили максимальное количество каналов ({max_channels})!</b>\n\n"
            f"⏳ <i>Сейчас будет создан ваш профиль...</i>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)  # Небольшая пауза для улучшения опыта
        # Переходим к созданию профиля
        await state.set_state(Step.all_ready)
        await all_ready(message, state)  # Переходим к финальному шагу


# Обработчик завершения ввода каналов
@router.message(Step.all_ready)
async def all_ready(message: Union[Message, CallbackQuery], state: FSMContext):
    # Определяем, откуда пришел запрос
    if isinstance(message, CallbackQuery):
        user_id = message.from_user.id
        # Отправляем стикер
        sticker_msg = await message.message.answer_sticker("CAACAgIAAxkBAAENkmln2Vcs_GBmuQWW5JIQ08wsm-DUeAACMgAD9wLID8IewmWo1Zl6NgQ")
        msg = await message.message.answer("⚡ <b>Создаю ваш профиль...</b>\n\n<i>🔄 Подключаюсь к базе данных</i>", parse_mode="HTML")
        bot = message.bot
        chat_id = message.message.chat.id
    else:
        user_id = message.from_user.id
        # Отправляем стикер
        sticker_msg = await message.answer_sticker("CAACAgIAAxkBAAENkmln2Vcs_GBmuQWW5JIQ08wsm-DUeAACMgAD9wLID8IewmWo1Zl6NgQ")
        msg = await message.answer("⚡ <b>Создаю ваш профиль...</b>\n\n<i>🔄 Подключаюсь к базе данных</i>", parse_mode="HTML")
        bot = message.bot
        chat_id = message.chat.id
    
    # Получаем данные пользователя
    user_data = await rq.get_user_data(user_id)
    channels = await rq.get_chanels(user_id)

    # Анимация "загрузки"
    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>📡 Проверяю подключение к API</i>", parse_mode="HTML")
    await asyncio.sleep(0.8)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>🔗 Добавляю ссылку на канал</i>", parse_mode="HTML")
    await asyncio.sleep(0.7)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>📝 Загружаю описание канала</i>", parse_mode="HTML")
    await asyncio.sleep(0.6)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>👤 Настраиваю профиль бота</i>", parse_mode="HTML")
    await asyncio.sleep(0.9)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>📢 Добавляю каналы для мониторинга</i>", parse_mode="HTML")
    await asyncio.sleep(0.7)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>⚙️ Настраиваю параметры нейросети</i>", parse_mode="HTML")
    await asyncio.sleep(1.1)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>🎯 Оптимизирую настройки</i>", parse_mode="HTML")
    await asyncio.sleep(0.8)

    await msg.edit_text("⚡ <b>Создаю ваш профиль...</b>\n\n<i>✨ Применяю финальные настройки</i>", parse_mode="HTML")
    await asyncio.sleep(1)

    # Финальное сообщение с эффектом печатающегося текста
    final_msg_text = "🎉 <b>Профиль успешно создан!</b>\n\n"
    final_msg_text += f"📌 <b>Ваш канал:</b> {user_data.link}\n"
    final_msg_text += f"ℹ️ <b>Описание канала:</b> {user_data.my_chanel_description}\n"
    final_msg_text += f"👤 <b>Профиль бота:</b> {user_data.my_profile_description}\n"
    final_msg_text += f"🎯 <b>Каналов для мониторинга:</b> {len(channels)}\n\n"
    final_msg_text += "<i>Вы можете изменить описание канала и профиля в любой момент</i> а пока продолжаем настройку бота\n"

    # Очищаем историю сообщений перед выводом финального сообщения
    try:
        # Получаем ID последнего сообщения
        last_message_id = msg.message_id
        
        # Пытаемся удалить предыдущие сообщения, кроме стикера и текущего сообщения
        start_id = max(1, last_message_id - 30)
        for i in range(start_id, last_message_id):
            if i != sticker_msg.message_id and i != last_message_id:
                try:
                    await bot.delete_message(chat_id, i)
                except Exception:
                    continue
    except Exception as e:
        print(f"Ошибка при очистке истории: {e}")
    
    # Отправляем финальное сообщение
    final_msg = await msg.edit_text(final_msg_text, parse_mode="HTML", reply_markup=kb.main_keyboard_go())
    
    # Удаляем стикер после завершения анимации и вывода финального сообщения
    await delete_message_safe(bot, sticker_msg.chat.id, sticker_msg.message_id)
    
    await state.clear()

@router.message(Step.all_ready_go)
async def home(message: Message, state: FSMContext):
    await message.answer(
        f"<b>🚀 {message.from_user.first_name}, Ваша домашняя страница. </b>\n\n"
        f"Здесь вы найдете все небходимое.\n\n",
        parse_mode="HTML",  # Указываем parse_mode один раз
        reply_markup=kb.main_keyboard_3()  # другая клавиатура
    )
    await state.clear()
    
@router.callback_query(F.data.startswith("next"))
async def com_start(callback: CallbackQuery, state: FSMContext):
    # Удаляем сообщение, на котором была нажата кнопка
    await callback.message.delete()

    # Отправляем новое сообщение
    msg = await callback.message.answer(
        "<b>Далее Вам нужно настроить то, как будут оставляться комментарии.</b>\n\n"
        "Выберите период, сколько бот будет ждать после выхода поста, прежде чем оставить комментарий.\n\n"
        "<i>Рекомендация: не меньше чем 200 секунд</i>",
        parse_mode="HTML",
        reply_markup=kb.period_com()
    )
    await state.update_data(last_message_id=msg.message_id)  # Сохраняем ID сообщения
    await state.set_state(Step.period_com)
    
@router.message(Step.period_com)
async def period(message: Message, state: FSMContext):
    # Удаляем предыдущее сообщение (если оно существует)
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await delete_message_safe(message.bot, message.chat.id, last_message_id)

    # Отправляем новое сообщение
    msg = await message.answer("Период записан ✅")
    await state.update_data(last_message_id=msg.message_id)  # Сохраняем ID сообщения

    msg = await message.answer(
        "Укажите, сколько постов подряд бот будет комментировать на одном канале за 1 день.\n\n"
        "<i>Рекомендация: не более 5</i>",
        parse_mode="HTML",
        reply_markup=kb.sleep_bot()
    )
    await state.update_data(last_message_id=msg.message_id)  # Сохраняем ID сообщения
    await state.set_state(Step.sleep_bot)

@router.message(Step.sleep_bot)
async def sleep(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await delete_message_safe(message.bot, message.chat.id, last_message_id)

    # Отправляем новое сообщение
    msg = await message.answer("Посты записаны ✅")
    await state.update_data(last_message_id=msg.message_id)

    msg = await message.answer(
        "Укажите, на сколько бот уйдет в сон после 50 комментариев.\n\n"
        "<i>Рекомендация: по опыту не менее чем на 180 минут</i>",
        parse_mode="HTML",
        reply_markup=kb.sleep_sleep()
    )
    await state.update_data(last_message_id=msg.message_id)
    await state.set_state(Step.launch_bot)

@router.message(Step.launch_bot)
async def all_ready_bot(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    
    if last_message_id:
        await delete_message_safe(message.bot, message.chat.id, last_message_id)

    msg = await message.answer(
        "✅ Настройки сохранены!\n\n"
        "Нажмите 'Скомпилировать', чтобы собрать вашего бота",
        reply_markup=kb.com_bot()
    )

@router.callback_query(F.data.startswith("compile"))
async def compile_bot(callback: CallbackQuery, state: FSMContext):
    # Анимация компиляции
    sticker_msg = await callback.message.answer_sticker("CAACAgIAAxkBAAENkmtn2VdDgotY0DzTEqEfmgeGUOg3VQACLAAD9wLID7xB4Mj74UDTNgQ")
    msg = await callback.message.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>🔄 Инициализация процесса</i>", parse_mode="HTML")
    await asyncio.sleep(1.2)

    await msg.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>📥 Загрузка настроек профиля</i>", parse_mode="HTML")
    await asyncio.sleep(0.8)

    await msg.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>⚙️ Настройка параметров комментирования</i>", parse_mode="HTML")
    await asyncio.sleep(0.9)

    await msg.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>🔗 Подключение к API Telegram</i>", parse_mode="HTML")
    await asyncio.sleep(0.7)

    await msg.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>🤖 Настройка нейромодулей</i>", parse_mode="HTML")
    await asyncio.sleep(1.1)

    await msg.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>📊 Оптимизация параметров</i>", parse_mode="HTML")
    await asyncio.sleep(0.8)

    await msg.edit_text("⚡ <b>Компилирую бота...</b>\n\n<i>✨ Финальная сборка</i>", parse_mode="HTML")
    await asyncio.sleep(1)

    # Очищаем историю сообщений
    try:
        # Получаем ID последнего сообщения
        last_message_id = callback.message.message_id
        chat_id = callback.message.chat.id
        
        # Пытаемся удалить последние 100 сообщений, исключая стикер и текущее сообщение
        for i in range(last_message_id - 100, last_message_id + 1):
            if i != sticker_msg.message_id and i != msg.message_id:
                try:
                    await callback.bot.delete_message(chat_id, i)
                except Exception:
                    continue
    except Exception as e:
        print(f"Ошибка при очистке истории: {e}")

    # Финальное сообщение и переход на домашнюю страницу
    welcome_text = (
        f"🎉 <b>Поздравляем! Ваш бот готов к работе!</b>\n\n"
        f"🚀 <b>Добро пожаловать в центр управления!</b>\n\n"
        f"Здесь вы можете:\n"
        f"📊 Отслеживать статистику комментариев\n"
        f"⚙️ Управлять настройками бота\n"
        f"📈 Анализировать эффективность\n"
        f"🔄 Обновлять параметры в любой момент\n\n"
        f"<i>Используйте панель управления ниже для навигации</i>"
    )

    # Сначала отправляем финальное сообщение
    final_msg = await callback.message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=kb.home_page()
    )
    
    # Только после отправки финального сообщения удаляем стикер и сообщение с анимацией
    await delete_message_safe(callback.bot, sticker_msg.chat.id, sticker_msg.message_id)
    await delete_message_safe(callback.bot, msg.chat.id, msg.message_id)
    
    await state.clear()

#⁡⁢⁣⁢-----------------------------------------------------Подписка оплата---------------------------------------------------------⁡

    
@router.callback_query(F.data.startswith("all_ready_pay"))
async def com_start(callback: CallbackQuery):
    sub = await rq.get_sub(callback.from_user.id)
    if sub.id ==1:
        await callback.message.answer("У вас пробная подписка. Если вы оплатили, но все еще видете эту надпись, напиши в тех поддержку, сразу же решим", reply_markup=kb.main_button())
        return
    # Текущая дата
    current_date = datetime.now()
    # Дата окончания через 20 дней
    end_date = current_date + timedelta(days=sub.date_day)
   
    await rq.set_sub_data(callback.from_user.id, end_date)
    await callback.message.answer("Успешно!", reply_markup= kb.main_button())
    return
    
        

@router.callback_query(F.data.startswith("by_subscriptions"))
async def com_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📊 Тарифы</b>\n\n"
        "🔹 <b>Начальный</b>\n"
        "• 14 каналов\n"
        "• 30 дней работы\n"
        "• 2490₽ <s>4980₽</s>\n"
        "• 15-25 переходов в день\n\n"
        "🔹 <b>Базовый</b>\n"
        "• 20 каналов\n"
        "• 30 дней работы\n"
        "• 2990₽ <s>5980₽</s>\n"
        "• 25-40 переходов в день\n\n"
        "🔹 <b>Про</b>\n"
        "• 35 каналов\n"
        "• 30 дней работы\n"
        "• 4490₽ <s>8980₽</s>\n"
        "• 40-65 переходов в день\n\n"
        "🔹 <b>Эксперт</b>\n"
        "• 50 каналов\n"
        "• 60 дней работы\n"
        "• 7490₽ <s>14980₽</s>\n"
        "• 55+ переходов в день\n\n"
        "💡 Выберите подходящий тариф:\n\n"
        "🎯 <i>Сейчас действует тестовый период бота, поэтому все цены в 2 раза ниже!</i>\n\n"
        "⚠️ <b>Важно:</b> Если вы хотите использовать премиум аккаунты, то к стоимости подписки добавляется +2000₽",
        parse_mode="HTML",
        reply_markup=kb.get_subscription_keyboard()
    )

@router.callback_query(F.data.startswith("subscriptions"))
async def com_start(callback: CallbackQuery):
    user = await rq.get_user_data(callback.from_user.id)
    date_exit = user.date_sub
    sub = await rq.get_sub(callback.from_user.id)
    sub_id = sub.id
    
    if sub_id != 1:
        message_text = (
            "<b>✅ Активная подписка</b>\n\n"
            f"📅 Действует до: {date_exit}\n"
            f"📊 Доступно каналов: {sub.max_chanels}\n\n"
            "💡 Для продления или изменения тарифа\n"
            "перейдите в раздел 'Каталог подписок'"
        )
    else:
        message_text = (
            "<b>🎯 Пробная подписка</b>\n\n"
            "• Тестирование функций бота\n"
            "• Доступно 10 дней\n"
            "• Ограниченный функционал\n\n"
            "💡 Для полного доступа оформите подписку"
        )

    await callback.message.edit_text(
        message_text,
        parse_mode="HTML",
        reply_markup=kb.main_button()
    )

#⁡⁢⁣⁡⁢⁣⁢-------------------------------------------------------------------------------------------------------------------------------⁡









#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------














#----------------------------------------------------------------------------------------КАНАЛЬНЫЕ КОМАНДЫ-------------------------------------------------------------------------------------------------

@router.callback_query(F.data == "list_chanel")
async def com_start(callback: CallbackQuery):
    user = await rq.get_user_data(callback.from_user.id)
    
    await callback.message.edit_text("Твои каналы, выбери что бы удалить или изменить", reply_markup = await kb.inline_chanels(callback.from_user.id))



@router.callback_query(F.data.startswith("query_"))
async def com_start(callback: CallbackQuery):
    old_link = callback.data.replace("query_", "")
    await callback.message.edit_text('Выбери действие', reply_markup= kb.ed_or_del(old_link))



@router.callback_query(F.data.startswith("edit_chanel_"))
async def com_start(callback: CallbackQuery, state: FSMContext):
    old_link = callback.data.replace("edit_chanel_", "")
    await state.update_data(old_link=old_link)
    await state.set_state(EditChannelState.waiting_for_new_link)
    await callback.message.edit_text(f"Введите новую ссылку вместо канала: {old_link}")



@router.message(EditChannelState.waiting_for_new_link)
async def process_new_link(message: Message, state: FSMContext):
    data = await state.get_data()
    old_link = data.get("old_link")  # Получаем старый канал из состояния
    new_link = message.text  # Новая ссылка от пользователя
    
    if not new_link.startswith("t.me/"):  # Простейшая проверка на ссылку
        await message.answer("Пожалуйста, введите корректную ссылку (должна начинаться с t.me/)")
        return

    # Обновляем в БД
    await rq.update_channel(message.from_user.id, old_link, new_link)

    await message.answer(f"Канал обновлён: {old_link} → {new_link}")
    await state.clear()  # Очищаем состояние



@router.callback_query(F.data.startswith("delete_chanel_"))
async def com_start(callback: CallbackQuery):
    old_link = callback.data.replace("delete_chanel_", "")
    await rq.delete_channel(callback.from_user.id, old_link)
    await callback.message.edit_text(f"Удалил канал {old_link} из базы", reply_markup=kb.main_button() )







@router.callback_query(F.data.startswith("my_bot"))
async def com_start(callback: CallbackQuery):
    user = await rq.get_user_data(callback.from_user.id)
    sub = user.sub_id
    if sub ==1:
        await callback.answer("Извините, но для этого раздела нужна подписка (")
        return
    bot = await rq.get_bot_data(callback.from_user.id)
    await callback.message.edit_text(f"Вот ссылка на вашего собранного бота от имени которого будут  оставлться коментарии: {bot.link_bot}")
        
        
    
        
    # Обработчик команды /add_suba
@router.message(Command('add_suba'))
async def get_chanels_other(message: Message, state: FSMContext):
    await message.answer("Давай твой tg_id", reply_markup=kb.main_button())
    await state.set_state(EditChannelState.waiting_tg_id)

# Обработчик для состояния "waiting_tg_id"
@router.message(EditChannelState.waiting_tg_id)
async def process_channel_link(message: Message, state: FSMContext):
    tg_id = message.text.strip()  # Получаем tg_id из введенного текста и убираем пробелы по краям
    if tg_id == "назад":
        await state.clear()
        await message.answer("Возвращаемся в главное меню.", reply_markup=kb.main_button())
        return

    if not tg_id.isdigit():  # Проверка на то, что tg_id состоит только из цифр
        await message.answer("Ты ввел некорректный tg_id. Попробуй снова.")
        return

    tg_id = int(tg_id)  # Преобразуем tg_id в число для дальнейшего использования

    # Сохраняем tg_id в состояние
    await state.update_data(tg_id=tg_id)

    # Получаем каналы по tg_id
    chanels = await rq.get_chanels(tg_id)

    if not chanels:
        await message.answer("Не удалось найти каналы для данного tg_id.")
    else:
        for chanel in chanels:
            await message.answer(chanel)

    # Очистка состояния после выполнения
    await state.clear()

@router.callback_query(F.data.startswith("feedback"))
async def com_start(callback: CallbackQuery):
    await callback.message.answer("Вы попали в раздел с отзывами. Данный раздел не очень велик, так как бот , напоминаю, относительно новый, его жизненный цикл всего месяц на данный момент. Как будет набираться +- 5 отзывов буду сразу пополнять ими данный раздел. Что бы ознакомиться с ними, нажмите 'Показать отзывы'. Напоминаю, что за каждый отзыв я добавляю 14 дней к подписке плюсом)",  reply_markup=kb.feedback())
    
@router.callback_query(F.data.startswith("otziv"))
async def com_start(callback: CallbackQuery):
    folder_path = os.path.join("feedback")  # Путь к папке с фото
    files = sorted(os.listdir(folder_path))  # Получаем список файлов
    
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]  # Фильтруем изображения
    
    if not images:
        await callback.answer("❌ Нет фото в папке 'feedback'", show_alert=True)
        return
    
    await callback.message.answer("📷 Загружаю отзывы...")
    
    for img in images:
        file_path = os.path.join(folder_path, img)
        photo = FSInputFile(file_path)
        await callback.message.answer_photo(photo)
        await asyncio.sleep(1)  # Задержка в 1 секунду

@router.callback_query(F.data.startswith("home_page"))
async def home_page(callback: CallbackQuery, state: FSMContext):
    welcome_text = (
        f"👋 <b>Привет, {callback.from_user.first_name}!</b>\n\n"
        f"🎯 <b>Ваш центр управления</b>\n\n"
        f"✨ <b>Доступные действия:</b>\n"
        f"👤 Редактировать профиль\n"
        f"⭐ Смотреть отзывы\n"
        f"💎 Управлять подпиской\n"
        f"🚀 Запускать бота\n\n"
        f"💡 <i>Выберите нужный раздел на панели управления</i>"
    )
    
    # Обновляем текущее сообщение с главным меню
    await callback.message.edit_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=kb.home_page()
    )
    
    # Сохраняем ID текущего сообщения
    current_message_id = callback.message.message_id
    
    # Создаем и запускаем задачу для удаления сообщений в фоновом режиме
    asyncio.create_task(delete_messages_background(
        callback.bot, 
        callback.message.chat.id, 
        current_message_id
    ))
    
    await state.clear()

# Функция для удаления сообщений в фоновом режиме
async def delete_messages_background(bot, chat_id, current_message_id):
    # Удаляем только последние 10 сообщений перед текущим, чтобы не пытаться удалить весь чат
    start_id = max(1, current_message_id - 10)  # Не пытаемся удалить сообщения с отрицательными ID
    
    # Счетчик ошибок
    error_count = 0
    max_errors = 3  # Максимальное количество ошибок, после которого выводим сообщение в лог
    
    for i in range(current_message_id - 1, start_id - 1, -1):
        try:
            await bot.delete_message(chat_id, i)
            # Небольшая пауза между удалениями, чтобы не перегружать API Telegram
            await asyncio.sleep(0.1)
        except Exception as e:
            error_count += 1
            # Выводим информацию об ошибке только если их мало 
            # или это последнее сообщение с ошибкой
            if error_count <= max_errors:
                print(f"Не удалось удалить сообщение {i}: {str(e)}")
            elif error_count == max_errors + 1:
                print(f"Дальнейшие ошибки удаления не будут показаны для уменьшения вывода")
    
    # Если были ошибки, выводим итоговое количество
    if error_count > max_errors:
        print(f"Всего ошибок при удалении: {error_count}")

@router.callback_query(F.data == "enough_channels")
async def handle_enough_channels(callback: CallbackQuery, state: FSMContext):
    current_count = await rq.count_channels_for_user(callback.from_user.id)
    if current_count == 0:
        await callback.message.edit_text(
            "Вы должны добавить хотя бы один канал перед тем, как продолжить.",
            parse_mode="HTML",
            reply_markup=kb.neiro_chanels()
        )
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    is_initial_setup = not data.get("is_profile_fully_filled", True)
    
    # Определяем действия в зависимости от типа настройки
    if is_initial_setup:
        # Это первичная настройка - запускаем анимацию создания профиля
        await callback.message.edit_text(
            "✅ <b>Каналы успешно добавлены!</b>\n\n"
            "⏳ <i>Сейчас будет создан ваш профиль...</i>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)  # Небольшая пауза для улучшения опыта
        
        # Запускаем анимацию создания профиля
        await state.set_state(Step.all_ready)
        await all_ready(callback, state)
    else:
        # Это редактирование профиля - возвращаемся в центр управления
        channels = await rq.get_chanels(callback.from_user.id)
        await callback.message.edit_text(
            f"✅ <b>Каналы успешно добавлены!</b>\n\n"
            f"📊 <b>Текущая статистика:</b>\n"
            f"• Всего каналов для мониторинга: {len(channels)}\n\n"
            f"<i>Вы можете продолжить работу с основного меню</i>",
            parse_mode="HTML",
            reply_markup=kb.main_keyboard_3()
        )
        await state.clear()

@router.message(Command('clear'))
async def clear_history(message: Message):
    try:
        # Удаляем сообщение с командой
        await message.delete()
        
        # Получаем ID последнего сообщения
        last_message_id = message.message_id
        
        # Пытаемся удалить последние 100 сообщений
        deleted_count = 0
        for i in range(last_message_id - 100, last_message_id):
            try:
                await message.bot.delete_message(message.chat.id, i)
                deleted_count += 1
                if deleted_count % 10 == 0:  # Делаем небольшую задержку каждые 10 сообщений
                    await asyncio.sleep(0.5)
            except Exception:
                continue
        
        # Отправляем сообщение об успешной очистке
        cleanup_msg = await message.answer(f"✨ История очищена")
        # Удаляем сообщение об очистке через 3 секунды
        await asyncio.sleep(3)
        await cleanup_msg.delete()
        
    except Exception as e:
        print(f"Ошибка при очистке истории: {e}")

# Обработчик кнопки "Редактировать профиль" в главном меню
@router.callback_query(F.data == "my_profile")
async def edit_profile_menu(callback: CallbackQuery):
    user = await rq.get_user_data(callback.from_user.id)
    
    profile_text = (
        f"<b>🧑‍💻 Редактирование профиля</b>\n\n"
        f"Текущая информация:\n"
        f"🔗 <b>Ваш канал:</b> {user.link}\n"
        f"ℹ️ <b>Описание канала:</b> {user.my_chanel_description}\n"
        f"👤 <b>Профиль бота:</b> {user.my_profile_description}\n\n"
        f"Выберите, что хотите отредактировать:"
    )
    
    # Создаем клавиатуру с опциями редактирования
    keyboard = [
        [
            InlineKeyboardButton(text="🔗 Редактировать ссылку на канал", callback_data="edit_link"),
        ],
        [
            InlineKeyboardButton(text="📝 Редактировать описание канала", callback_data="description_chanel"),
            InlineKeyboardButton(text="👤 Редактировать описание профиля", callback_data="description_profile")
        ],
        [
            InlineKeyboardButton(text="📢 Добавить каналы", callback_data="add_chanels"),
            InlineKeyboardButton(text="📋 Список каналов", callback_data="list_chanel")
        ],
        [
            InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="home_page")
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(profile_text, parse_mode="HTML", reply_markup=markup)

# Обработчик кнопки "Редактировать описание канала"
@router.callback_query(F.data == "description_chanel")
async def edit_channel_description(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user_data(callback.from_user.id)
    
    text = (
        f"<b>📝 Редактирование описания канала</b>\n\n"
        f"Текущее описание:\n"
        f"<i>{user.my_chanel_description}</i>\n\n"
        f"Введите новое описание канала (до 700 символов).\n"
        f"Это описание будет использоваться для генерации комментариев в вашем стиле."
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb.main_button())
    await state.set_state(EditChannelState.waiting_for_channel_description)

# Обработчик ввода нового описания канала
@router.message(EditChannelState.waiting_for_channel_description)
async def process_channel_description(message: Message, state: FSMContext):
    new_description = message.text.strip()
    
    # Проверка длины описания
    if len(new_description) > 700:
        await message.answer(
            "⚠️ Слишком длинное описание! Максимальная длина - 700 символов.\n"
            "Пожалуйста, сократите текст и отправьте снова."
        )
        return
    
    # Обновляем описание в базе данных
    await rq.update_chanel_description(message.from_user.id, new_description)
    
    # Сообщаем об успешном обновлении
    await message.answer(
        "✅ <b>Описание канала успешно обновлено!</b>\n\n"
        "Вы можете продолжить редактирование профиля или вернуться в главное меню.",
        parse_mode="HTML",
        reply_markup=kb.main_button()
    )
    
    # Очищаем состояние
    await state.clear()

# Обработчик кнопки "Редактировать описание профиля"
@router.callback_query(F.data == "description_profile")
async def edit_profile_description(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user_data(callback.from_user.id)
    
    text = (
        f"<b>👤 Редактирование описания профиля</b>\n\n"
        f"Текущее описание:\n"
        f"<i>{user.my_profile_description}</i>\n\n"
        f"Введите новое описание профиля (до 70 символов).\n"
        f"Оно будет размещено в биографии аккаунта, от имени которого бот будет оставлять комментарии."
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb.main_button())
    await state.set_state(EditChannelState.waiting_for_profile_description)

# Обработчик ввода нового описания профиля
@router.message(EditChannelState.waiting_for_profile_description)
async def process_profile_description(message: Message, state: FSMContext):
    new_description = message.text.strip()
    
    # Проверка длины описания
    if len(new_description) > 70:
        await message.answer(
            "⚠️ Слишком длинное описание! Максимальная длина - 70 символов.\n"
            "Пожалуйста, сократите текст и отправьте снова."
        )
        return
    
    # Обновляем описание в базе данных
    await rq.update_profile_description(message.from_user.id, new_description)
    
    # Сообщаем об успешном обновлении
    await message.answer(
        "✅ <b>Описание профиля успешно обновлено!</b>\n\n"
        "Вы можете продолжить редактирование профиля или вернуться в главное меню.",
        parse_mode="HTML",
        reply_markup=kb.main_button()
    )
    
    # Очищаем состояние
    await state.clear()

# Обработчик кнопки "Редактировать ссылку на канал"
@router.callback_query(F.data == "edit_link")
async def edit_link(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user_data(callback.from_user.id)
    
    text = (
        f"<b>🔗 Редактирование ссылки на канал</b>\n\n"
        f"Текущая ссылка:\n"
        f"<i>{user.link}</i>\n\n"
        f"Введите новую ссылку на канал (формат: t.me/название_канала).\n"
        f"Эта ссылка будет отображаться в комментариях бота,\n"
        f"и пользователи будут переходить по ней на ваш канал."
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb.main_button())
    await state.set_state(EditChannelState.waiting_for_link_update)

# Обработчик ввода новой ссылки на канал
@router.message(EditChannelState.waiting_for_link_update)
async def process_link_update(message: Message, state: FSMContext):
    new_link = message.text.strip()
    
    # Проверки ссылки
    if len(new_link) > 35:
        await message.answer(
            "⚠️ Слишком длинная ссылка! Максимальная длина - 35 символов.\n"
            "Пожалуйста, сократите ссылку и отправьте снова."
        )
        return
    
    if not new_link.startswith("t.me/"):
        await message.answer(
            "⚠️ Неверный формат ссылки! Ссылка должна начинаться с t.me/\n"
            "Пример: t.me/название_канала"
        )
        return
    
    # Обновляем ссылку в базе данных
    success = await rq.add_link(message.from_user.id, new_link)
    
    if success:
        # Сообщаем об успешном обновлении
        await message.answer(
            "✅ <b>Ссылка на канал успешно обновлена!</b>\n\n"
            "Вы можете продолжить редактирование профиля или вернуться в главное меню.",
            parse_mode="HTML",
            reply_markup=kb.main_button()
        )
    else:
        await message.answer(
            "❌ <b>Не удалось обновить ссылку!</b>\n"
            "Возможно, такая ссылка уже используется другим пользователем.",
            parse_mode="HTML",
            reply_markup=kb.main_button()
        )
    
    # Очищаем состояние
    await state.clear()

# Обработчик кнопки "Запустить бота"
@router.callback_query(F.data == "launch_bot")
async def handle_launch_bot(callback: CallbackQuery):
    # Получаем данные пользователя
    user = await rq.get_user_data(callback.from_user.id)
    
    # Проверяем ID подписки (1 = бесплатная/тестовая)
    if user.sub_id == 1:
        # Пользователь без подписки - направляем на тестовый режим
        await callback.message.edit_text(
            "<b>🚀 Тестовый нейрокомментинг</b>\n\n"
            "🔍 <b>Вы можете опробовать, как работает нейрокомментинг:</b>\n\n"
            "• Перешлите любой пост из канала\n"
            "• Бот сгенерирует пример комментария\n"
            "• Вы увидите, как это будет выглядеть при полном запуске\n\n"
            "⚠️ <b>Ограничения тестового режима:</b>\n"
            "• Комментарии не публикуются автоматически\n"
            "• Работает только с пересланными сообщениями\n"
            "• Ограничено количество использований\n\n"
            "🔥 <b>Для полноценной работы приобретите подписку!</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Попробовать тестовый режим", callback_data="test")],
                [InlineKeyboardButton(text="💎 Приобрести подписку", callback_data="by_subscriptions")],
                [InlineKeyboardButton(text="🏠 Вернуться в меню", callback_data="home_page")]
            ])
        )
    else:
        # Пользователь с подпиской - направляем на полный режим
        await callback.message.edit_text(
            "<b>🚀 Запуск нейрокомментинга</b>\n\n"
            "✅ <b>У вас активирована подписка</b> - доступен полный функционал!\n\n"
            "📊 <b>Статистика:</b>\n"
            f"• Подписка: {'Премиум' if user.sub_id == 3 else 'Стандарт'}\n"
            f"• Добавлено каналов: {await rq.count_channels_for_user(callback.from_user.id)}\n\n"
            "🔥 <b>Выберите действие:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="▶️ Запустить комментирование", callback_data="run_bot")],
                [InlineKeyboardButton(text="⏹ Остановить бота", callback_data="stop_bot")],
                [InlineKeyboardButton(text="🏠 Вернуться в меню", callback_data="home_page")]
            ])
        )

# Обработчик кнопки "Остановить бота"
@router.callback_query(F.data == "stop_bot")
async def handle_stop_bot(callback: CallbackQuery):
    # Перенаправляем на команду /stop_bot в модуле neiro_handlers.py
    await callback.message.edit_text(
        "<b>⏹ Остановка бота...</b>\n\n"
        "Останавливаем процесс нейрокомментинга...",
        parse_mode="HTML"
    )
    
    # Имитируем команду /stop_bot
    from app.neiro.neiro_handlers import stop_bot
    message = callback.message
    message.from_user = callback.from_user
    await stop_bot(message)
    
    # Возвращаемся в главное меню
    await callback.message.answer(
        "<b>✅ Бот успешно остановлен!</b>\n\n"
        "Вы можете запустить его снова в любое время.",
        parse_mode="HTML",
        reply_markup=kb.home_page()
    )




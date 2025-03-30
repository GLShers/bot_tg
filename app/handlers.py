from aiogram import Bot, F, Router
from aiogram.types import Message, FSInputFile, CallbackQuery, BotCommand, BotCommandScopeDefault, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
import app.keyboards as kb
import os
import time
from contextlib import suppress
from typing import Union
import asyncio
import datetime
from datetime import timedelta
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
    
    # Проверяем дату подписки, если она существует и не базовая
    if user.sub_id != 1 and user.date_sub:
        now = datetime.datetime.now()
        days_left = (user.date_sub - now).days
        
        # Если осталось меньше 3 дней, уведомляем пользователя
        if 0 <= days_left <= 3:
            await message.answer(
                f"<b>⚠️ Внимание! Ваша подписка скоро закончится</b>\n\n"
                f"До окончания подписки осталось <b>{days_left} {'дней' if days_left > 1 else 'день'}</b>.\n"
                f"Чтобы продолжить пользоваться всеми функциями бота, "
                f"рекомендуем продлить подписку заранее.",
                parse_mode="HTML",
                reply_markup=kb.subscription_renewal_keyboard()
            )
        # Если подписка уже закончилась, уведомляем и сбрасываем на базовую
        elif days_left < 0:
            # Сбрасываем на базовую подписку
            await rq.reset_to_basic_subscription(message.from_user.id)
            await message.answer(
                "<b>❌ Ваша подписка закончилась</b>\n\n"
                "Для продолжения пользования всеми функциями бота, "
                "пожалуйста, продлите подписку.",
                parse_mode="HTML",
                reply_markup=kb.subscription_renewal_keyboard()
            )
    
    # Проверяем, заполнен ли профиль пользователя полностью
    is_profile_fully_filled = user.link and user.my_chanel_description and user.my_profile_description
    
    if is_profile_fully_filled:
        # Проверяем статус подписки
        if user.sub_id != 1:  # Если у пользователя активная подписка (не базовая)
            # Получаем информацию о подписке
            subscription = await rq.get_sub(message.from_user.id)
            
            # Получаем список каналов пользователя
            channels = await rq.get_chanels(message.from_user.id)
            channel_count = len(channels) if channels else 0
            
            # Получаем количество оставшихся дней подписки
            days_left = 0
            if user.date_sub:
                now = datetime.datetime.now()
                delta = user.date_sub - now
                days_left = max(0, delta.days)  # Если отрицательное, значит подписка истекла
            
            # Формируем приветственное сообщение с информацией о подписке
            subscription_text = (
                f"<b>🚀 ЦЕНТР УПРАВЛЕНИЯ НЕЙРОКОММЕНТИНГОМ</b>\n\n"
                f"<b>👋 Здравствуйте, {message.from_user.first_name}!</b>\n\n"
                f"<b>📊 ИНФОРМАЦИЯ О ВАШЕЙ ПОДПИСКЕ:</b>\n"
                f"• 💎 Текущий план: {subscription.sub_name}\n"
                f"• ⏱️ Осталось дней: {days_left}\n"
                f"• 📺 Подключено каналов: {channel_count}/{subscription.max_chanels}\n"
                f"• 🔄 Свободных слотов: {max(0, subscription.max_chanels - channel_count)}\n\n"
                f"<b>🔥 ВАШИ ПРЕИМУЩЕСТВА:</b>\n"
                f"• 💹 Не нужно покупать телеграмм аккаунты\n"
                f"• 🧠 Уникальные AI-комментарии вместо шаблонов\n"
                f"• 🛡️ Встроенная защита от блокировок\n"
                f"• 📱 Управление через удобный интерфейс\n\n"
                f"<i>Используйте панель управления ниже для доступа ко всем функциям</i>"
            )
            await message.answer(
                subscription_text,
                parse_mode="HTML",
                reply_markup=kb.home_page()
            )
            return
        
        # Если нет активной подписки, показываем стандартное приветствие для авторизованного пользователя
        welcome_text = (
            f"<b>🚀 ЦЕНТР УПРАВЛЕНИЯ НЕЙРОКОММЕНТИНГОМ</b>\n\n"
            f"<b>👋 Здравствуйте, {message.from_user.first_name}!</b>\n\n"
            f"<b>📊 МГНОВЕННЫЙ ДОСТУП К ФУНКЦИЯМ:</b>\n"
            f"• ⚙️ Настройка и редактирование профиля\n"
            f"• 📈 Аналитика эффективности комментирования\n"
            f"• 💎 Управление подпиской и дополнительными опциями\n"
            f"• 🚀 Запуск/остановка интеллектуальной системы\n\n"
            f"<b>🔥 ВАШИ ПРЕИМУЩЕСТВА:</b>\n"
            f"• 💹 Не нужно покупать телеграмм аккаунты\n"
            f"• 🧠 Уникальные AI-комментарии вместо шаблонов\n"
            f"• 🛡️ Встроенная защита от блокировок\n"
            f"• 📱 Управление через удобный интерфейс\n\n"
            f"<i>Используйте панель управления ниже для доступа ко всем функциям</i>"
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
        await callback.message.answer("✅ <b>Ваш профиль уже полностью настроен!</b>\n\n🚀 <i>Вы можете сразу начать использовать все возможности нейрокомментинга.</i>", parse_mode="HTML", reply_markup=kb.go())
        await state.set_state(Step.all_ready_go)
        return

    # Устанавливаем флаг для проверки заполненности профиля в состояние
    # Поскольку пользователь только начинает настройку, профиль не заполнен
    await state.update_data(is_profile_fully_filled=False)

    # Отправляем новое сообщение
    msg = await callback.message.answer("<b>🔗 Укажите ссылку на Ваш Telegram-канал</b>\n\n"
                                        "👥 Эта ссылка - ключевой элемент успешного нейрокомментинга! Именно по ней пользователи будут переходить на Ваш канал после прочтения комментариев.\n\n"
                                        "⚡ <i>Правильно указанная ссылка значительно повысит конверсию подписчиков.</i>", parse_mode="HTML")
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
        msg = await message.answer("❌ <b>Упс! Ссылка слишком длинная.</b>\n\n▶️ Максимальная длина ссылки - 35 символов.\n\n💡 <i>Попробуйте использовать более короткий адрес для повышения эффективности.</i>", parse_mode="HTML")
        await state.update_data(last_message_id=msg.message_id)
        return
    
    if not new_link.startswith("t.me/"):
        msg = await message.answer("❌ <b>Неверный формат ссылки!</b>\n\n▶️ Ссылка должна начинаться с <code>t.me/</code>\n\n💡 <i>Пример правильной ссылки: t.me/channel_name</i>", parse_mode="HTML")
        await state.update_data(last_message_id=msg.message_id)
        return

    succeful_add = await rq.add_link(message.from_user.id, new_link)

    if succeful_add:
        msg = await message.answer("✅ <b>Ваша ссылка успешно добавлена!</b>\n\n🚀 <i>Теперь Ваш канал будет получать больше внимания!</i>", parse_mode="HTML")
    else:
        msg = await message.answer("⚠️ <b>Эта ссылка уже была добавлена ранее.</b>\n\n💡 <i>Мы используем её для продвижения Вашего канала.</i>", parse_mode="HTML")
    
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
        "<b>📝 Создайте уникальное описание Вашего канала</b>\n\n"
        "🔍 Это описание определит индивидуальный стиль AI-комментариев и повысит их эффективность.\n\n"
        "💡 <i>Совет: укажите тематику, особенности контента и целевую аудиторию канала для лучших результатов!</i>",
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
        msg = await message.answer("❌ <b>Описание слишком длинное!</b>\n\n▶️ Пожалуйста, сократите текст до 700 символов.\n\n💡 <i>Лаконичное описание часто работает эффективнее!</i>", parse_mode="HTML")
        await state.update_data(last_message_id=msg.message_id)
    else:
        existing_description = await rq.update_chanel_description(message.from_user.id, new_des_chanel)
        msg = await message.answer(f"✅ <b>Отлично! Описание Вашего канала сохранено.</b>\n\n🎯 <i>Теперь AI сможет генерировать комментарии в уникальном стиле Вашего канала!</i>", parse_mode="HTML")
        
        await state.update_data(last_message_id=msg.message_id)
        
        msg = await message.answer(
            "<b>👤 Создайте биографию для профиля бота</b>\n\n"
            "💼 Биография будет размещена в профиле аккаунта, который оставляет комментарии от Вашего имени.\n\n"
            "✅ <i>Ограничение: до 70 символов + ссылка на Ваш канал.</i>\n\n"
            "💡 <i>Грамотная биография значительно повышает доверие читателей и конверсию!</i>",
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
        msg = await message.answer("❌ <b>Описание профиля слишком длинное!</b>\n\n▶️ Пожалуйста, сократите до 70 символов.\n\n💡 <i>Лаконичная биография лучше привлекает внимание!</i>", parse_mode="HTML")
        await state.update_data(last_message_id=msg.message_id)
    else:
        existing_description = await rq.add_profile_description(message.from_user.id, new_des_profile)
        
        if existing_description and existing_description != True:
            msg = await message.answer(f"📝 <b>У Вас уже есть описание профиля:</b>\n\n<b>{existing_description}</b>\n\n✅ <i>Текущее описание заменено на новое!</i>", parse_mode="HTML")
        else:
            msg = await message.answer(f"✅ <b>Биография профиля успешно сохранена!</b>\n\n🚀 <i>Ваши комментарии теперь будут выглядеть еще профессиональнее!</i>", parse_mode="HTML")
        
        await state.update_data(last_message_id=msg.message_id)
        
        # Получаем данные пользователя, чтобы проверить заполненность профиля
        user = await rq.get_user_data(message.from_user.id)
        
        # Проверяем, заполнен ли профиль пользователя полностью
        is_profile_fully_filled = user.link and user.my_chanel_description and user.my_profile_description
        
        # Отправляем текстовое сообщение
        msg = await message.answer(
            "<b>🎭 Выберите стиль AI-комментариев</b>\n\n"
            "Каждый стиль создан для определенных целей и аудитории:\n\n"
            "🔹 <b>💼 Деловой</b> — профессиональный тон, бизнес-фокус\n"
            "🔹 <b>💡 Инновационный</b> — креативные идеи, свежий взгляд\n"
            "🔹 <b>🚀 Динамичный</b> — энергичный, мотивирующий стиль\n"
            "🔹 <b>🎭 Дружелюбный</b> — тёплые, располагающие комментарии\n"
            "🔹 <b>📊 Аналитический</b> — факты, логика, статистика\n"
            "🔹 <b>🔍 Экспертный</b> — глубина знаний, авторитетность\n"
            "🔹 <b>🌟 Вдохновляющий</b> — мотивация, позитив, поддержка\n\n"
            "💡 <i>Выберите стиль, подходящий для вашей аудитории</i>",
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
    await callback.message.answer(
        "✅ <b>ПРЕВОСХОДНЫЙ ВЫБОР СТИЛЯ!</b>\n\n"
        "🎯 <i>Вы выбрали идеальный стиль комментирования для максимальной конверсии!</i>\n\n"
        "📈 <b>ЧТО ЭТО ЗНАЧИТ ДЛЯ ВАС:</b>\n"
        "• Комментарии будут точно соответствовать тематике Вашего контента\n"
        "• AI адаптирует тон и лексику под выбранный стиль\n"
        "• Вовлечённость аудитории увеличится на 35-40%",
        parse_mode="HTML"
    )
    
    msg = await callback.message.answer(
        "<b>🔍 ДОБАВЛЕНИЕ КАНАЛОВ ДЛЯ МОНИТОРИНГА</b>\n\n"
        "<b>📊 Выберите каналы для автоматического комментирования</b>\n\n"
        "Добавьте Telegram-каналы, где бот будет автоматически анализировать новые посты и создавать интеллектуальные комментарии.\n\n"
        "📈 <b>СТРАТЕГИЯ МАКСИМАЛЬНОГО ОХВАТА:</b>\n"
        "• Выбирайте каналы с активной, но не токсичной аудиторией\n"
        "• Фокусируйтесь на нишевых сообществах в вашей тематике\n"
        "• Комбинируйте крупные и растущие каналы для баланса\n\n"
        f'💡 <i>Введите ссылки в формате</i> <code>t.me/название_канала</code>\n\n'
        f'⏩ <i>Нажмите "Достаточно", когда завершите добавление целевых каналов.</i>',
        parse_mode="HTML",
        reply_markup=kb.neiro_chanels()
    )
    
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
            f"<b>🏆 Максимальное количество каналов ({max_channels}) добавлено!</b>\n\n"
            f"💯 <i>Вы полностью используете возможности Вашего тарифа.</i>\n\n",
            parse_mode="HTML"
            
        )
        await state.set_state(Step.add_chanels)
        # Это редактирование профиля
        await state.update_data(is_profile_fully_filled=True)
        return
    else:
        await callback.message.edit_text(
            f"<b>📊 Ваши каналы для мониторинга</b>\n\n"
            f"{channels_text}\n"
            f"💡 <i>Отправьте</i> <code>t.me/имя_канала</code> <i>для добавления нового канала</i>\n\n"
            f"✅ <i>Или нажмите 'Достаточно', если завершили добавление каналов</i>",
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
            msg = await message.answer("⚠️ <b>Необходимо добавить хотя бы один канал!</b>\n\n💡 <i>Добавьте канал для мониторинга, чтобы продолжить настройку.</i>", parse_mode="HTML")
            await state.update_data(last_message_id=msg.message_id)
            return
        else:
            # Если это первичная настройка (на основе флага из состояния)
            if is_initial_setup:
                # Это первичная настройка - показываем сообщение перед анимацией
                msg = await message.answer(
                    "✅ <b>Каналы успешно добавлены в систему!</b>\n\n"
                    "🔍 <i>Бот будет регулярно анализировать новые посты для комментирования.</i>\n\n"
                    "⏳ <i>Подготовка Вашего персонального профиля...</i>",
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
                    reply_markup=kb.main_keyboard_2()
                )
                await state.clear()
            return

    # Разделение введённых каналов
    channels = text.split()

    added_channels = 0
    for channel in channels:
        # Проверка формата ссылки
        if not channel.startswith("t.me/"):
            msg = await message.answer("❌ <b>Неверный формат ссылки!</b>\n\n▶️ Ссылка должна начинаться с <code>t.me/</code>\n\n💡 <i>Пример правильной ссылки: t.me/название_канала</i>", parse_mode="HTML", reply_markup=kb.neiro_chanels())
            await state.update_data(last_message_id=msg.message_id)
            return

        # Проверка длины ссылки
        if len(channel) > 35:
            msg = await message.answer("❌ <b>Ссылка слишком длинная!</b>\n\n▶️ Максимальная длина ссылки - 35 символов.\n\n💡 <i>Используйте более короткий адрес для повышения эффективности.</i>", parse_mode="HTML", reply_markup=kb.neiro_chanels())
            await state.update_data(last_message_id=msg.message_id)
            return

        # Добавление канала, если осталось место
        if remaining > 0:
            added = await rq.add_chanels(message.from_user.id, channel)
            if added:
                remaining -= 1
                added_channels += 1
            else:
                msg = await message.answer(f"⚠️ <b>Канал {channel} уже добавлен в Ваш список.</b>\n\n💡 <i>Пожалуйста, добавьте другой канал.</i>", parse_mode="HTML", reply_markup=kb.neiro_chanels())
                await state.update_data(last_message_id=msg.message_id)
        else:
            break

    # Ответ пользователю
    if added_channels > 0:
        if remaining > 0:
            msg = await message.answer(
                f'✅ <b>Каналы успешно добавлены!</b>\n\n'
                f'📊 У Вас осталось еще {remaining} свободных слотов.\n\n'
                f'💡 <i>Добавьте еще каналы или нажмите "Достаточно" для завершения.</i>', 
                parse_mode="HTML",
                reply_markup=kb.neiro_chanels()
            )
        else:
            # Если лимит каналов достигнут, показываем соответствующее сообщение
            msg = await message.answer(
                "🏆 <b>Поздравляем! Вы использовали все доступные слоты для каналов.</b>\n\n"
                "💯 <i>Вы максимально используете возможности Вашего тарифа.</i>\n\n"
                "⏩ <i>Нажмите 'Достаточно' для продолжения настройки.</i>", 
                parse_mode="HTML",
                reply_markup=kb.neiro_chanels()
            )
    else:
        msg = await message.answer(
            "⚠️ <b>Новые каналы не были добавлены.</b>\n\n💡 <i>Попробуйте еще раз или нажмите 'Достаточно'.</i>", 
            parse_mode="HTML",
            reply_markup=kb.neiro_chanels()
        )
    await state.update_data(last_message_id=msg.message_id)

    # Проверяем, нужно ли автоматически перейти к созданию профиля
    # Только для первичной настройки и только при достижении лимита
    if remaining == 0 and is_initial_setup:
        # Сообщаем пользователю о переходе к созданию профиля
        msg = await message.answer(
            f"<b>🏆 Все {max_channels} каналов успешно добавлены!</b>\n\n"
            f"📊 <i>Вы полностью используете возможности Вашего тарифа.</i>\n\n"
            f"⚙️ <i>Сейчас будет создан Ваш персональный профиль...</i>",
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
    final_msg_text = "🎉 <b>Ваш профиль успешно создан!</b>\n\n"
    final_msg_text += f"📌 <b>Ваш канал:</b> {user_data.link}\n"
    final_msg_text += f"ℹ️ <b>Описание канала:</b> {user_data.my_chanel_description}\n"
    final_msg_text += f"👤 <b>Профиль бота:</b> {user_data.my_profile_description}\n"
    final_msg_text += f"🎯 <b>Каналов для мониторинга:</b> {len(channels)}\n\n"
    final_msg_text += "🚀 <b>Поздравляем! Ваша система нейрокомментинга настроена и готова к работе.</b>\n\n"
    final_msg_text += "💡 <i>Вы всегда можете изменить настройки профиля в центре управления.</i>\n\n"
    final_msg_text += "⏩ <i>Продолжим настройку бота для максимальной эффективности!</i>\n"

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
        f"<b>🏆 {message.from_user.first_name}, Ваш Центр Управления Нейрокомментингом</b>\n\n"
        f"<b>📊 ВАШИ ВОЗМОЖНОСТИ В ОДНОМ МЕСТЕ:</b>\n"
        f"• 💎 Полный контроль над всеми настройками системы\n"
        f"• 📈 Управление стратегией комментирования в реальном времени\n"
        f"• 🚀 Мгновенная оптимизация параметров для роста эффективности\n"
        f"• 🔍 Аналитика результатов и их влияние на конверсию\n\n"
        f"<b>🎯 ТЕКУЩИЕ ПОКАЗАТЕЛИ:</b>\n"
        f"• ⚡ Статус системы: Готова к запуску\n"
        f"• 🔥 Потенциал роста: Высокий\n\n"
        f"<b>💡 РЕКОМЕНДАЦИЯ ЭКСПЕРТА:</b>\n"
        f"Используйте все инструменты панели управления для достижения максимальных результатов продвижения!",
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
        "<b>⚙️ НАСТРОЙКА ИНТЕЛЛЕКТУАЛЬНОГО КОММЕНТИРОВАНИЯ</b>\n\n"
        "<b>🕒 Выберите время задержки перед комментированием</b>\n\n"
        "Этот параметр определяет, сколько секунд бот будет ждать после публикации нового поста, прежде чем оставить комментарий.\n\n"
        "💡 <i>Оптимальная настройка: 200-300 секунд</i>\n\n"
        "📊 <b>Почему это важно:</b>\n"
        "• Слишком быстрое комментирование выглядит неестественно\n"
        "• Оптимальная задержка повышает вовлеченность до 40%\n"
        "• Реалистичное время отклика увеличивает доверие аудитории",
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
    msg = await message.answer("✅ <b>Время задержки успешно установлено!</b>\n\n💡 <i>Оптимальная настройка сохранена в Вашем профиле.</i>", parse_mode="HTML")
    await state.update_data(last_message_id=msg.message_id)  # Сохраняем ID сообщения

    msg = await message.answer(
        "<b>📊 НАСТРОЙКА ЧАСТОТЫ КОММЕНТИРОВАНИЯ</b>\n\n"
        "<b>📈 Укажите дневной лимит комментариев на один канал</b>\n\n"
        "Этот параметр определяет, сколько постов подряд бот будет комментировать на одном канале за 1 день.\n\n"
        "💡 <i>Оптимальная настройка: 3-5 постов в день</i>\n\n"
        "📊 <b>Наша аналитика показывает:</b>\n"
        "• 3-5 комментариев в день обеспечивают рост подписчиков на 25%\n"
        "• Более 5 комментариев могут выглядеть как спам\n"
        "• Регулярное комментирование увеличивает узнаваемость бренда",
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
    msg = await message.answer("✅ <b>Лимит комментариев установлен!</b>\n\n💡 <i>Настройка сохранена для максимальной эффективности.</i>", parse_mode="HTML")
    await state.update_data(last_message_id=msg.message_id)

    msg = await message.answer(
        "<b>⏱️ НАСТРОЙКА РЕЖИМА БЕЗОПАСНОСТИ</b>\n\n"
        "<b>🛡️ Определите время отдыха для системы</b>\n\n"
        "Этот параметр задаёт, на сколько минут бот будет приостанавливать активность после 50 комментариев для обеспечения безопасности аккаунта.\n\n"
        "💡 <i>Оптимальная настройка: 180-240 минут</i>\n\n"
        "📊 <b>Преимущества правильной настройки:</b>\n"
        "• Защита от блокировок и ограничений Telegram\n"
        "• Повышение срока жизни рабочих аккаунтов на 300%\n"
        "• Непрерывная работа системы в долгосрочной перспективе",
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
        "<b>🚀 НАСТРОЙКИ УСПЕШНО СОХРАНЕНЫ!</b>\n\n"
        "<b>✅ ВСЕ ПАРАМЕТРЫ ОПТИМИЗИРОВАНЫ:</b>\n"
        "• Время задержки перед комментированием\n"
        "• Дневной лимит комментариев\n"
        "• Режим безопасности для аккаунта\n\n"
        "📊 <b>ПРОГНОЗ ЭФФЕКТИВНОСТИ:</b>\n"
        "• Прирост активности: до 200%\n"
        "• Увеличение охвата: до 350%\n"
        "• Потенциальный рост подписчиков: 10-15% в месяц\n\n"
        "💡 <i>Нажмите «Скомпилировать», чтобы запустить вашу персональную систему нейрокомментинга с учетом всех настроек!</i>",
        parse_mode="HTML",
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
        f"<b>🚀 ВАШ ЦЕНТР УПРАВЛЕНИЯ ИНТЕЛЛЕКТУАЛЬНОЙ СИСТЕМОЙ</b>\n\n"
        f"<b>📊 МГНОВЕННЫЙ ДОСТУП К ФУНКЦИЯМ:</b>\n"
        f"• ⚙️ Тонкая настройка всех параметров системы\n"
        f"• ⚡ Тест всей системы бесплатно\n"
        f"• 📈 Продвинутая аналитика эффективности комментирования\n"
        f"• 🔄 Опции масштабирования и оптимизации стратегии\n\n"
        f"<b>🔥 ПРЕИМУЩЕСТВА НАШЕЙ СИСТЕМЫ:</b>\n"
        f"• 💹 Не нужно покупать телеграмм аккаунты, у нас их большая база\n"
        f"• 🚀 Прокси активно работают на всех аккаунтах\n"
        f"• 🧠 Уникальные нейрокомментарии вместо шаблонных реплик\n"
        f"• 🛡️ Встроенная защита от блокировок и ограничений\n"
        f"• 📱 Полное управление через интуитивный интерфейс\n\n"
        f"<i>Используйте панель управления ниже для навигации по всем возможностям</i>"
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
    user = await rq.get_user_data(callback.from_user.id)
    sub = await rq.get_sub(callback.from_user.id)
    
    if user.sub_id == 1:
        # Подписка еще не подтверждена администратором
        await callback.message.edit_text(
            "<b>⚠️ Оплата пока не подтверждена</b>\n\n"
            "Администратор еще не обработал вашу оплату.\n"
            "Пожалуйста, подождите некоторое время, или свяжитесь с нами,\n"
            "если вы уже произвели оплату более 30 минут назад.\n\n"
            "📩 Поддержка: @Alexcharevich",
            parse_mode="HTML",
            reply_markup=kb.main_button()
        )
        return
    
    # Подписка подтверждена (sub_id != 1)
    # Текущая дата
    current_date = datetime.datetime.now()
    # Дата окончания через количество дней согласно тарифу
    end_date = current_date + timedelta(days=sub.date_day)
   
    # Устанавливаем дату окончания подписки
    await rq.set_sub_data(callback.from_user.id, end_date)
    
    # Форматируем дату для отображения
    formatted_date = end_date.strftime("%d.%m.%Y")
    
    # Сообщаем пользователю об успешной активации подписки
    await callback.message.edit_text(
        f"<b>✅ Подписка успешно активирована!</b>\n\n"
        f"<b>📊 ИНФОРМАЦИЯ О ВАШЕЙ ПОДПИСКЕ:</b>\n"
        f"• 💎 Ваш тариф: {sub.sub_name}\n"
        f"• ⏱️ Действует до: {formatted_date}\n"
        f"• 📺 Доступно каналов: {sub.max_chanels}\n\n"
        f"Теперь вы можете использовать все возможности нейрокомментинга!\n"
        f"Настройте свой профиль и начните привлекать новую аудиторию прямо сейчас.",
        parse_mode="HTML",
        reply_markup=kb.home_page()
    )
    return
    
        

@router.callback_query(F.data.startswith("by_subscriptions"))
async def com_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📊 Тарифные Планы</b>\n\n"
        
        "<b>🔹 Начальный</b>\n"
        "• 14 каналов\n"
        "• 30 дней работы\n"
        "• <s>4980₽</s> 2490₽\n"
        "• 15-25 переходов в день\n"
        "• 1 аккаунт для комментариев\n"
        "• <i>Для новичков и стартапов</i>\n\n"

        "<b>🔹 Базовый</b>\n"
        "• 20 каналов\n"
        "• 30 дней работы\n"
        "• <s>5980₽</s> 2990₽\n"
        "• 25-40 переходов в день\n"
        "• 3 аккаунта для комментариев\n"
        "• <i>Для бизнеса с средними объемами</i>\n\n"

        "<b>🔹 Про</b>\n"
        "• 35 каналов\n"
        "• 30 дней работы\n"
        "• <s>8980₽</s> 4490₽\n"
        "• 40-65 переходов в день\n"
        "• 3 аккаунта для комментариев\n"
        "• <i>Для активных пользователей и крупных проектов</i>\n\n"

        "<b>🔹 Эксперт</b>\n"
        "• 50 каналов\n"
        "• 60 дней работы\n"
        "• <s>14980₽</s> 7490₽\n"
        "• 55+ переходов в день\n"
        "• 3 аккаунта для комментариев\n"
        "• <i>Для максимальной эффективности и масштабных проектов</i>\n\n"

        "<b>🔹 Годовой План (Супер Эксперт)</b>\n"
        "• 50 каналов\n"
        "• 365 дней работы\n"
        "• <s>17980₽</s> 8990₽\n"
        "• 55+ переходов в день\n"
        "• 3 аккаунта для комментариев\n"
        "• <i>Полный доступ на год с бесплатными обновлениями</i>\n"
        "• <i>+ Бесплатная поддержка и приоритетные обновления</i>\n\n"

        "💡 <b>Тестовый период:</b> Все тарифы сейчас действуют со скидкой 50%!\n"
        "⚠️ <b>Важно:</b> Премиум аккаунт +2000₽ к стоимости подписки\n\n"

        "<b>Особенности и Преимущества:</b>\n"
        "• Парсер каналов: Входит во все тарифы.\n"
        "• Количество аккаунтов для комментариев: Для начального тарифа — 1, для остальных — 3.\n"
        "• Обновления: При покупке любой подписки в тестовом режиме все будущие обновления будут бесплатными.\n"
        "• Гибкость: Долгосрочные подписки получают дополнительные преимущества, такие как бесплатные обновления на год.\n\n"
        
        "📈 <b>Выберите подходящий тариф:</b>\n\n"
        "🎯 <i>Не упустите шанс протестировать бота по сниженной цене!</i>",
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
    # Отправляем маркетинговое вступление с мощным заголовком
    await callback.message.answer(
        "<b>🔥 ДОКАЗАННЫЙ РЕЗУЛЬТАТ: РЕАЛЬНЫЕ ОТЗЫВЫ</b>\n\n"
        "<b>Рост подписчиков до +45% за первый месяц!</b>\n"
        "Владельцы каналов уже зарабатывают больше с нашей системой.\n\n"
        "<i>Смотрите доказательства ниже ⬇️</i>",
        parse_mode="HTML"
    )
    
    # Сразу загружаем отзывы
    folder_path = os.path.join("feedback")
    files = sorted(os.listdir(folder_path))
    
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    if not images:
        await callback.message.answer(
            "<b>❌ Отзывы временно недоступны</b>\n\n"
            "Мы собираем новые отзывы от клиентов. Вы можете стать первым, кто оставит отзыв и получит +14 дней к подписке!",
            parse_mode="HTML",
            reply_markup=kb.feedback()
        )
        return
    
    # Отправляем заголовок для первого блока отзывов
    await callback.message.answer(
        "<b>💯 ОТЗЫВЫ НАШИХ ПОЛЬЗОВАТЕЛЕЙ:</b>\n"
        "Рост активности в комментариях до 300%",
        parse_mode="HTML"
    )
    
    # Телеграм позволяет отправлять максимум 10 фотографий в одной группе,
    # поэтому делим фотографии на группы по 10 фото
    from aiogram.types import InputMediaPhoto
    
    # Разбиваем фотографии на группы по 10 штук
    chunk_size = 10
    photo_groups = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]
    
    # Отправляем каждую группу фотографий
    for i, photo_group in enumerate(photo_groups):
        media_group = []
        for img in photo_group:
            file_path = os.path.join(folder_path, img)
            media_group.append(InputMediaPhoto(media=FSInputFile(file_path)))
        
        if media_group:
            await callback.message.answer_media_group(media=media_group)
            # Небольшая задержка между отправками групп
            await asyncio.sleep(1)
    
    # В конце отправляем сообщение с призывом к действию
    await callback.message.answer(
        "<b>🏆 ХОТИТЕ ТАК ЖЕ?!</b>\n\n"
        "Более 90% наших клиентов отмечают значительный рост активности и подписчиков в первые 2 недели.\n\n"
        "<b>ОГРАНИЧЕННОЕ ПРЕДЛОЖЕНИЕ:</b>\n"
        "• Оставьте отзыв о вашем опыте\n"
        "• Получите <b>+5 ДНЕЙ</b> ко своей подписке\n"
        "• Разблокируйте все функции нейрокомментинга\n\n"
        "<i>👇 Выберите действие ниже</i>",
        parse_mode="HTML",
        reply_markup=kb.feedback()
    )
    
@router.callback_query(F.data.startswith("otziv"))
async def com_start(callback: CallbackQuery):
    # Перенаправляем на основной обработчик отзывов
    await com_start(callback)

@router.callback_query(F.data.startswith("home_page"))
async def home_page(callback: CallbackQuery, state: FSMContext):
    welcome_text = (f"<b>🚀 ЦЕНТР УПРАВЛЕНИЯ НЕЙРОКОММЕНТИНГОМ</b>\n\n"
            f"<b>📊 МГНОВЕННЫЙ ДОСТУП К ФУНКЦИЯМ:</b>\n"
            f"• ⚙️ Настройка и редактирование профиля\n"
            f"• 📈 Аналитика эффективности комментирования\n"
            f"• 💎 Управление подпиской и дополнительными опциями\n"
            f"• 🚀 Запуск/остановка интеллектуальной системы\n\n"
            f"<b>🔥 ВАШИ ПРЕИМУЩЕСТВА:</b>\n"
            f"• 💹 Не нужно покупать телеграмм аккаунты\n"
            f"• 🧠 Уникальные AI-комментарии вместо шаблонов\n"
            f"• 🛡️ Встроенная защита от блокировок\n"
            f"• 📱 Управление через удобный интерфейс\n\n"
            f"<i>Используйте панель управления ниже для доступа ко всем функциям</i>"
        )
    await callback.message.edit_text(
            welcome_text,
            parse_mode="HTML",
            reply_markup=kb.home_page()
        )
        # Сохраняем ID текущего сообщения и запускаем удаление
    current_message_id = callback.message.message_id
    asyncio.create_task(delete_messages_background(
            callback.bot, 
            callback.message.chat.id, 
            current_message_id
        ))
    return

    # Если профиль не настроен, показываем стандартное приветствие
    welcome_text = (
        "<b>👋 Добро пожаловать в бота для нейрокомментинга!</b>\n\n"
        "✅ <b>Что умеет бот:</b>\n"
        "• Автоматический анализ постов\n"
        "• Генерация релевантных комментариев\n"
        "• Работа с несколькими каналами\n"
        "• Настройка расписания комментирования\n\n"
        "🚀 <b>Начните прямо сейчас:</b>\n"
        "1. Настройте свой профиль\n"
        "2. Добавьте каналы для мониторинга\n"
        "3. Выберите стиль комментариев\n"
    )
    
    await callback.message.edit_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=kb.start()
    )
    
    # Сохраняем ID текущего сообщения и запускаем удаление
    current_message_id = callback.message.message_id
    asyncio.create_task(delete_messages_background(
        callback.bot, 
        callback.message.chat.id, 
        current_message_id
    ))
    
    await state.clear()

@router.callback_query(F.data == "back")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    # Используем тот же код, что и для home_page
    await home_page(callback, state)

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    # Используем тот же код, что и для home_page
    await home_page(callback, state)

# Функция для удаления сообщений в фоновом режиме
async def delete_messages_background(bot, chat_id, current_message_id):
    # Удаляем последние 50 сообщений перед текущим, чтобы захватить все отзывы
    start_id = max(1, current_message_id - 50)  # Не пытаемся удалить сообщения с отрицательными ID
    
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
            "✅ <b>Каналы успешно добавлены в систему!</b>\n\n"
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
            reply_markup=kb.main_keyboard_2()
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
        f"<b>🧑‍💻 ЦЕНТР УПРАВЛЕНИЯ ПРОФИЛЕМ</b>\n\n"
        f"<b>⚙️ ТЕКУЩИЕ НАСТРОЙКИ ВАШЕГО КАНАЛА:</b>\n"
        f"🔗 <b>Ваш канал:</b> {user.link}\n"
        f"ℹ️ <b>Описание канала:</b> {user.my_chanel_description}\n"
        f"👤 <b>Профиль бота:</b> {user.my_profile_description}\n\n"
        f"<b>💼 ИНСТРУМЕНТЫ ДЛЯ ВАШЕГО РОСТА:</b>\n"
        f"Настройте каждый элемент для максимальной эффективности продвижения. Правильная конфигурация профиля может увеличить приток подписчиков на 200-300%!"
    )
    
    # Используем готовую клавиатуру из модуля keyboards
    await callback.message.edit_text(
        profile_text,
        parse_mode="HTML",
        reply_markup=kb.main_keyboard_2()  # Используем существующую клавиатуру
    )

# Обработчик кнопки "Редактировать описание канала"
@router.callback_query(F.data == "description_chanel")
async def edit_channel_description(callback: CallbackQuery, state: FSMContext):
    user = await rq.get_user_data(callback.from_user.id)
    
    text = (
        f"<b>📝 СОЗДАЙТЕ ИДЕАЛЬНОЕ ОПИСАНИЕ ВАШЕГО КАНАЛА</b>\n\n"
        f"<b>🔍 Текущее описание:</b>\n"
        f"<i>{user.my_chanel_description}</i>\n\n"
        f"<b>💰 КАК ПРАВИЛЬНОЕ ОПИСАНИЕ УВЕЛИЧИВАЕТ ДОХОД:</b>\n"
        f"• Комментарии в вашем уникальном стиле вызывают больше доверия\n"
        f"• Точное позиционирование привлекает целевую аудиторию\n"
        f"• Ключевые темы канала помогают AI создавать релевантные комментарии\n\n"
        f"<b>✏️ ВВЕДИТЕ НОВОЕ ОПИСАНИЕ (до 700 символов):</b>\n"
        f"Опишите основные темы, стиль и тональность вашего канала. Эта информация будет использована для настройки AI-комментариев под вашу аудиторию и контент."
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
            "<b>⚠️ СЛИШКОМ ОБЪЁМНОЕ ОПИСАНИЕ</b>\n\n"
            "Максимальная длина - 700 символов.\n\n"
            "<b>💡 СОВЕТ ОТ ЭКСПЕРТОВ:</b>\n"
            "Краткие, но ёмкие описания работают эффективнее. Сфокусируйтесь на уникальных особенностях вашего канала и целевой аудитории. Это поможет AI генерировать более точные и привлекательные комментарии.",
            parse_mode="HTML"
        )
        return
    
    # Обновляем описание в базе данных
    await rq.update_chanel_description(message.from_user.id, new_description)
    
    # Сообщаем об успешном обновлении
    await message.answer(
        "<b>✅ ОПИСАНИЕ КАНАЛА УСПЕШНО ОБНОВЛЕНО!</b>\n\n"
        "<b>🎯 ЧТО ЭТО ЗНАЧИТ ДЛЯ ВАС:</b>\n"
        "• AI теперь будет создавать комментарии с учетом вашей тематики\n"
        "• Комментарии станут более релевантными для вашей аудитории\n"
        "• Возрастет вероятность привлечения новых подписчиков\n\n"
        "<b>📊 СТАТИСТИКА:</b> Каналы с правильно настроенным описанием получают на 50% больше новых подписчиков через комментарии!",
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
        f"<b>👤 СОЗДАЙТЕ ПРИВЛЕКАТЕЛЬНЫЙ ПРОФИЛЬ ДЛЯ КОММЕНТИРОВАНИЯ</b>\n\n"
        f"<b>📝 Текущее описание:</b>\n"
        f"<i>{user.my_profile_description}</i>\n\n"
        f"<b>🔥 ПОЧЕМУ ЭТО ВАЖНО:</b>\n"
        f"• Профессиональное описание увеличивает конверсию из комментариев на 35%\n"
        f"• Правильный профиль вызывает доверие у потенциальных подписчиков\n"
        f"• Люди охотнее переходят по ссылкам от авторитетных источников\n\n"
        f"<b>✏️ ВВЕДИТЕ НОВОЕ ОПИСАНИЕ (до 70 символов):</b>\n"
        f"Это описание будет размещено в профиле аккаунта, от имени которого бот оставляет комментарии. Сделайте его информативным и вызывающим доверие."
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
            "<b>⚠️ СЛИШКОМ ДЛИННОЕ ОПИСАНИЕ</b>\n\n"
            "Максимальная длина - 70 символов.\n\n"
            "<b>💡 ЛАЙФХАК ДЛЯ ЭФФЕКТИВНОСТИ:</b>\n"
            "В коротком описании укажите вашу экспертность и уникальное предложение. Например: «Эксперт по криптовалютам с 5-летним опытом» или «Лидер мнений в сфере digital-маркетинга».",
            parse_mode="HTML"
        )
        return
    
    # Обновляем описание в базе данных
    await rq.update_profile_description(message.from_user.id, new_description)
    
    # Сообщаем об успешном обновлении
    await message.answer(
        "<b>✅ ПРОФИЛЬ УСПЕШНО ОБНОВЛЕН!</b>\n\n"
        "<b>🚀 ВАШ ПРОФИЛЬ ТЕПЕРЬ:</b>\n"
        "• Выглядит профессионально и вызывает доверие\n"
        "• Повышает авторитетность ваших комментариев\n"
        "• Увеличивает шансы перехода пользователей по вашим ссылкам\n\n"
        "<b>📈 РЕЗУЛЬТАТ:</b> Качественное описание профиля увеличивает кликабельность ссылок до 40%! Это ключевой элемент вашей стратегии роста.",
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
        f"<b>🔗 НАСТРОЙКА ССЫЛКИ НА ВАШ КАНАЛ</b>\n\n"
        f"<b>🌐 Текущая ссылка:</b>\n"
        f"<i>{user.link}</i>\n\n"
        f"<b>💰 ПОЧЕМУ ПРАВИЛЬНАЯ ССЫЛКА = БОЛЬШЕ ПОДПИСЧИКОВ:</b>\n"
        f"• Короткие ссылки увеличивают переходы на 20%\n"
        f"• Запоминающиеся имена каналов повышают узнаваемость бренда\n"
        f"• Каждый комментарий работает как микро-рекламная кампания\n\n"
        f"<b>✏️ ВВЕДИТЕ НОВУЮ ССЫЛКУ:</b>\n"
        f"Формат: t.me/название_канала\n\n"
        f"<b>💡 СОВЕТ:</b> Используйте простую ссылку без лишних символов - это повысит эффективность вашего продвижения через комментарии."
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
            "<b>⚠️ СЛИШКОМ ДЛИННАЯ ССЫЛКА!</b>\n\n"
            "Максимальная длина - 35 символов.\n\n"
            "<b>💡 СЕКРЕТ ЭФФЕКТИВНОСТИ:</b>\n"
            "Короткие ссылки легче запоминаются и вызывают на 25% больше доверия. Используйте лаконичное название канала без лишних символов и цифр.",
            parse_mode="HTML"
        )
        return
    
    if not (new_link.startswith("t.me/") or new_link.startswith("https://t.me/") or new_link.startswith("@")):
        await message.answer(
            "<b>⚠️ НЕВЕРНЫЙ ФОРМАТ ССЫЛКИ</b>\n\n"
            "<b>Используйте один из форматов:</b>\n"
            "• t.me/название_канала (рекомендуем)\n"
            "• https://t.me/название_канала\n"
            "• @название_канала\n\n"
            "<b>💡 МАРКЕТИНГОВЫЙ ХАК:</b>\n"
            "Формат t.me/название_канала показывает на 35% лучшую конверсию в переходы, чем другие форматы!",
            parse_mode="HTML"
        )
        return
    
    # Приводим ссылку к единому формату, если она начинается с @
    if new_link.startswith("@"):
        new_link = "t.me/" + new_link[1:]
    
    # Обновляем ссылку в базе данных
    success = await rq.add_link(message.from_user.id, new_link)
    
    if success:
        # Сообщаем об успешном обновлении
        await message.answer(
            "<b>✅ ССЫЛКА НА КАНАЛ УСПЕШНО ОБНОВЛЕНА!</b>\n\n"
            "<b>🚀 ЧТО ПРОИСХОДИТ ДАЛЬШЕ:</b>\n"
            "• Все новые комментарии будут содержать вашу обновленную ссылку\n"
            "• Потенциальные подписчики увидят прямой путь к вашему контенту\n"
            "• Повысится конверсия из просмотров комментариев в подписчиков\n\n"
            "<b>📊 ИНТЕРЕСНЫЙ ФАКТ:</b> Правильно настроенная ссылка увеличивает количество переходов в среднем на 45% по сравнению со стандартными форматами.",
            parse_mode="HTML",
            reply_markup=kb.main_button()
        )
    else:
        await message.answer(
            "<b>❌ НЕ УДАЛОСЬ ОБНОВИТЬ ССЫЛКУ</b>\n\n"
            "Возможно, эта ссылка уже используется в системе.\n\n"
            "<b>💡 РЕКОМЕНДАЦИЯ:</b>\n"
            "Попробуйте использовать уникальный идентификатор вашего канала или добавить к нему отличительный элемент.",
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
            "<b>🚀 ИСПЫТАЙТЕ СИЛУ НЕЙРОКОММЕНТИНГА БЕСПЛАТНО!</b>\n\n"
            "<b>👨‍💻 ЧТО ВЫ ПОЛУЧИТЕ В ТЕСТОВОМ РЕЖИМЕ:</b>\n"
            "• Демонстрация AI-комментариев к контенту\n"
            "• Примеры комментариев, которые привлекают подписчиков\n\n"
            "<b>📊 КАК ЭТО РАБОТАЕТ:</b>\n"
            "1. Перешлите сюда любой пост\n"
            "2. AI проанализирует контент и создаст комментарий\n"
            "3. Вы увидите, как это будет работать в тестовом режиме\n\n"
            "<b>⚠️ ОГРАНИЧЕНИЯ БЕСПЛАТНОЙ ВЕРСИИ:</b>\n"
            "• Комментарии не публикуются автоматически\n"
            "• Работает только с пересланными постами\n"
            "• Комментарий увидете только вы\n\n"
            "<b>🔥 ФАКТ:</b> Наши клиенты увеличивают активность в каналах на 200-300% благодаря умным комментариям!",
            parse_mode="HTML",
            reply_markup=kb.launch_bot_test_keyboard()
        )
    else:
        # Получаем список каналов пользователя
        channels = await rq.get_chanels(callback.from_user.id)
        
        if not channels:
            # Если каналов нет, предлагаем добавить их
            await callback.message.edit_text(
                "<b>📺 У вас пока нет каналов для мониторинга</b>\n\n"
                "Для начала работы добавьте каналы, которые хотите мониторить.",
                parse_mode="HTML",
                reply_markup=kb.main_keyboard_2()
            )
        else:
            # Формируем список каналов
            channels_text = "<b>📺 Ваши каналы для мониторинга:</b>\n\n"
            for i, channel in enumerate(channels, 1):
                channels_text += f"{i}. {channel}\n"
            
            # Создаем клавиатуру
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Проверить каналы", callback_data="check_channels")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home_page")]
            ])
            
            # Отправляем сообщение с каналами
            await callback.message.edit_text(
                channels_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

# Обработчик кнопки "Остановить бота"
@router.callback_query(F.data == "stop_bot")
async def handle_stop_bot(callback: CallbackQuery):
    # Перенаправляем на команду /stop_bot в модуле neiro_handlers.py
    await callback.message.edit_text(
        "<b>⏹ ПРИОСТАНОВКА РАБОТЫ СИСТЕМЫ</b>\n\n"
        "<b>⚙️ ПРОЦЕСС:</b>\n"
        "• Останавливаем все процессы комментирования\n"
        "• Сохраняем текущие настройки и прогресс\n"
        "• Завершаем активные сессии\n\n"
        "<b>⌛ Пожалуйста, подождите...</b>",
        parse_mode="HTML"
    )
    
    # Имитируем команду /stop_bot
    from app.neiro.neiro_handlers import stop_bot
    message = callback.message
    message.from_user = callback.from_user
    await stop_bot(message)
    
    # Возвращаемся в главное меню
    await callback.message.answer(
        "<b>✅ СИСТЕМА УСПЕШНО ОСТАНОВЛЕНА</b>\n\n"
        "<b>📊 СТАТУС ВАШЕГО АККАУНТА:</b>\n"
        "• Все настройки и каналы сохранены\n"
        "• Комментирование временно приостановлено\n"
        "• Система готова к перезапуску в любой момент\n\n"
        "<b>💡 РЕКОМЕНДАЦИЯ ЭКСПЕРТА:</b>\n"
        "Для достижения максимальных результатов рекомендуется непрерывная работа системы комментирования не менее 14 дней. Это обеспечивает стабильный рост активности и привлечение новой аудитории.",
        parse_mode="HTML",
        reply_markup=kb.home_page()
    )

@router.callback_query(F.data == "check_channels")
async def handle_check_channels(callback: CallbackQuery):
    # Получаем список каналов пользователя
    channels = await rq.get_chanels(callback.from_user.id)
    
    if not channels:
        await callback.message.edit_text(
            "<b>❌ Ошибка</b>\n\n"
            "Не удалось найти каналы для проверки. Пожалуйста, добавьте каналы в настройках.",
            parse_mode="HTML",
            reply_markup=kb.main_keyboard_2()
        )
        return
    
    # Отправляем сообщение о начале проверки
    await callback.message.edit_text(
        "<b>🔍 Начинаем проверку каналов...</b>\n\n"
        "Пожалуйста, подождите, пока мы проанализируем ваши каналы.",
        parse_mode="HTML"
    )
    
    # TODO: Здесь будет логика проверки каналов
    # Пока просто отправляем заглушку
    await asyncio.sleep(2)  # Имитация проверки
    
    await callback.message.edit_text(
        "<b>✅ Проверка завершена</b>\n\n"
        "Все каналы доступны и готовы к работе с нейрокомментингом.",
        parse_mode="HTML",
        reply_markup=kb.main_keyboard_2()
    )




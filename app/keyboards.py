from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import app.database.requests as rq
from urllib.parse import quote

async def inline_chanels(tg_id):
    keyboard = InlineKeyboardBuilder()
    chanels = await rq.get_chanels(tg_id)
    for chanel in chanels:
        keyboard.add(InlineKeyboardButton(text=f"✏ {chanel}", callback_data=f"query_{chanel}"))
    keyboard.add(InlineKeyboardButton(text="Главное меню", callback_data="home_page"))
    return keyboard.adjust(1).as_markup()


def main_button():
    main_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Главное меню", callback_data="home_page")]],
    )
    return main_button

def ed_or_del(chanel):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Посмотреть список каналов', callback_data='list_chanel')],
        [InlineKeyboardButton(text='Изменить', callback_data=f'edit_chanel_{chanel}'),
         InlineKeyboardButton(text='Удалить', callback_data=f'delete_chanel_{chanel}')]
    ])
    return keyboard


def main_keyboard_1():
    main_keyboard_1= InlineKeyboardMarkup(inline_keyboard=[ 
            [InlineKeyboardButton(text="Составить комментарий ▶️", callback_data='test')]

    ])
    return main_keyboard_1

def main_keyboard_2():
    main_keyboard_2= InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ссылка на ваш канал 🔗", callback_data='add_link')], #+
            [InlineKeyboardButton(text="Описание вашего канала✏️", callback_data='description_chanel')], #+
            [InlineKeyboardButton(text="Добавить каналы в список ☑️", callback_data='add_chanels')], #+
            [InlineKeyboardButton(text="Мои каналы для мониторинга📺", callback_data='list_chanel')], #+
            [InlineKeyboardButton(text="Описание профиля 🧑‍💻", callback_data='description_profile')],
            [InlineKeyboardButton(text="Далее ▶️", callback_data='next')]
    ])
    return main_keyboard_2

def main_keyboard_3():
    keyboard = [
        [
            InlineKeyboardButton(text="📝 Редактировать описание канала", callback_data="description_chanel"),
            InlineKeyboardButton(text="👤 Редактировать описание профиля", callback_data="description_profile")
        ],
        [
            InlineKeyboardButton(text="📢 Добавить каналы", callback_data="add_chanels"),
            InlineKeyboardButton(text="📋 Список каналов", callback_data="list_chanel")
        ],
        [
            InlineKeyboardButton(text="💎 Подписка", callback_data="subscriptions"),
            InlineKeyboardButton(text="⭐ Отзывы", callback_data="feedback")
        ],
        [
            InlineKeyboardButton(text="🚀 Запустить бота", callback_data="my_bot"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="home_page")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def start():
    start = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Начинаем', callback_data='start')]])
    return start

def style():
    style = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Стиль Сета Година', callback_data='go_style')],
         [InlineKeyboardButton(text='Стиль Гая Кавасаки', callback_data='go_style')],
         [InlineKeyboardButton(text='Стиль Илона Маска', callback_data='go_style')]])
    return style



def get_subscription_keyboard():
    keyboard = InlineKeyboardBuilder()

    telegram_username = "Alexcharevich"  # Без "@"
    message_text = "Привет! Хочу купить подписку! 🔥"

    # Кодируем текст в URL (на случай пробелов и спецсимволов)
    encoded_message = quote(message_text)

    # Кнопка для покупки подписки (сразу открывает диалог в Telegram)
    keyboard.button(
        text="💳 Купить подписку [Напрямую у разраба]",
        url=f"tg://resolve?domain={telegram_username}&text={encoded_message}"
    )

    # Кнопка для поддержки
    keyboard.button(
        text="📩 Написать в поддержку",
        url=f"tg://resolve?domain={telegram_username}"
    )
    
    
    keyboard.button(
        text="🆗 Админ подтвердил оплату",
        callback_data="all_ready_pay"
    )

    # Главное меню
    keyboard.button(text="Назад 🏠", callback_data="home_page")

    keyboard.adjust(1)  # Все кнопки в один ряд

    return keyboard.as_markup()


def feedback():
    feedback = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Показать отзывы', callback_data='otziv')],
        [InlineKeyboardButton(text="Главное меню", callback_data="home_page")]])
    return feedback



def subscription_offer_keyboard():
    """
    Клавиатура с предложением подписки после тестового режима.
    """
    buttons = [
        [
            InlineKeyboardButton(text="💎 Приобрести подписку", callback_data="by_subscriptions"),
        ],
        [
            InlineKeyboardButton(text="📈 Посмотреть отзывы", callback_data="feedback"),
        ],
        [
            InlineKeyboardButton(text="🏠 Вернуться на главную", callback_data="home_page"),
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def neiro_chanels():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Достаточно", callback_data="enough_channels")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home_page")]
    ])
    return keyboard


def go():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Перейти к профилю')]],
        resize_keyboard=True
    )
    return keyboard

def edit_des_chanel():
    edit_des_chane = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать описание ', callback_data='edit_chanel_description')],
         [InlineKeyboardButton(text='Главнe меню', callback_data='home_page')]])
    return edit_des_chane


def edit_des_profile():
    edit_des_prof = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать описание ', callback_data='edit_profile_description')],
         [InlineKeyboardButton(text='Главнe меню', callback_data='home_page')]])
    return edit_des_prof


def period_com():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='сразу')],
            [KeyboardButton(text='50-100')],
            [KeyboardButton(text='100-200')],
            [KeyboardButton(text='200-500')]
        ],
        resize_keyboard=True
    )
    return keyboard

def sleep_bot():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='без ограничений')],
            [KeyboardButton(text='1')],
            [KeyboardButton(text='2')],
            [KeyboardButton(text='3')],
            [KeyboardButton(text='4')],
            [KeyboardButton(text='5')],
            [KeyboardButton(text='6')]
        ],
        resize_keyboard=True
    )
    return keyboard

def sleep_sleep():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Не уходить в сон')],
            [KeyboardButton(text='60 минут')],
            [KeyboardButton(text='120 минут')],
            [KeyboardButton(text='180 минут')],
            [KeyboardButton(text='240 минут')]
        ],
        resize_keyboard=True
    )
    return keyboard

def launch():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Запустить бота! 🚀')]
        ],
        resize_keyboard=True
    )
    return keyboard


def compile():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Запустить бота! 🚀')]
        ],
        resize_keyboard=True
    )
    return keyboard



def home_page():
    home_page= InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Редактировать профиль ✏️", callback_data='my_profile')], #+
            [InlineKeyboardButton(text="Наши отзывы 📝", callback_data='feedback')],
            [InlineKeyboardButton(text="Каталог подписок 🛒", callback_data='by_subscriptions')],
            [InlineKeyboardButton(text="🚀 ЗАПУСТИТЬ НЕЙРОКОММЕНТИНГ 🚀", callback_data='launch_bot')]
    ])
    return home_page

def main_keyboard_go():
    main_keyboard_go= InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Далее ▶️", callback_data='next')]])
    return main_keyboard_go


def com_bot():
    com_bot= InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скомпелировать бота", callback_data='compile')]])
    return com_bot

def comment_frequency():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Очень часто", callback_data="freq_very_high")],
        [InlineKeyboardButton(text="Часто", callback_data="freq_high")],
        [InlineKeyboardButton(text="Средне", callback_data="freq_medium")],
        [InlineKeyboardButton(text="Редко", callback_data="freq_low")],
        [InlineKeyboardButton(text="Главное меню", callback_data="home_page")]
    ])
    return keyboard
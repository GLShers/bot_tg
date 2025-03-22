import os
import asyncio
from telethon import TelegramClient
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
import app.keyboards as kb

class Idd(StatesGroup):
    id_bot = State()

ses = Router()

async def create_telegram_client(bot_id):
    """Создаёт и возвращает клиент Telethon, создавая сессию в корневой папке проекта"""
    bot = await rq.get_bot_data_for_id(bot_id)
    
    # Получаем путь к корневой папке (где находится app/)
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  
    
    # Создаем путь к директории sessions
    sessions_dir = os.path.join(base_dir, "sessions")
    os.makedirs(sessions_dir, exist_ok=True)  # Создаем директорию, если её нет
    
    session_name = os.path.join(sessions_dir, f"session_{bot_id}_{bot.link_bot}")

    # Проверяем, есть ли уже сессия
    if os.path.exists(session_name + ".session"):
        print(f"⚡ Сессия {session_name} уже существует.")
    else:
        print(f"✅ Создаём новую сессию: {session_name}")
    
    hapi_hash = bot.hash_id.strip().strip('"')
    
    # Создаём и возвращаем клиент
    client = TelegramClient(session_name, bot.api_id, hapi_hash)
    return client


@ses.message(Command("session"))
async def com_start(message: Message, state: FSMContext):
    """Начинает процесс ввода ID бота"""
    await message.answer("Введите ID бота:", reply_markup=kb.main_button())
    await state.set_state(Idd.id_bot)

@ses.message(Idd.id_bot)
async def process_link(message: Message, state: FSMContext):
    """Обрабатывает введённый ID, создаёт и запускает клиент"""
    bot_id = message.text.strip()

    # Проверяем, что введённое значение – число
    if not bot_id.isdigit():
        await message.answer("❌ Введите корректный числовой ID.")
        return

    await message.answer(f"⚙ Создаём сессию для бота ID {bot_id}...")
    
    client = await create_telegram_client(bot_id)

    try:
        await client.start()  # Запускаем клиент
        await message.answer("✅ Сессия успешно создана и запущена!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при запуске: {e}")

    await state.clear()  # Сбрасываем состояние

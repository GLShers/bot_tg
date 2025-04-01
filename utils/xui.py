import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Импорты для работы с БД
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import requests as rq
from app.database.models import async_session, Bot_data

async def create_session(bot_id):
    # Получаем данные бота из БД
    async with async_session() as session:
        bot_data = await rq.get_bot_data_by_id(bot_id)
        
        if not bot_data:
            print(f"❌ Бот с ID {bot_id} не найден в базе данных")
            return False
            
        print(f"ℹ️ Данные бота получены: API_ID={bot_data.api_id}")
        
        phone = input("📱 Введите номер телефона (с кодом страны, например +7xxxxxxxxxx): ")
        
        # Создаем папку sessions если её нет
        os.makedirs("sessions", exist_ok=True)
        
        # Создаем клиент с данными из БД
        client = TelegramClient(
            f"sessions/session_{bot_id}_{bot_data.api_id}",
            bot_data.api_id,
            bot_data.hash_id
        )
        
        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input("🔑 Введите код из Telegram: ")

            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                password = input("🔐 Введите пароль 2FA: ")
                await client.sign_in(password=password)

        print("✅ Сессия успешно сохранена!")
        await client.disconnect()

def show_usage():
    print("Использование:")
    print(f"python {os.path.basename(__file__)} <bot_id>")
    print("Пример:")
    print(f"python {os.path.basename(__file__)} 123")

async def main():
    if len(sys.argv) != 2:
        show_usage()
        return
        
    try:
        bot_id = int(sys.argv[1])
        await create_session(bot_id)
    except ValueError:
        print("❌ ID бота должен быть числом")
        show_usage()

if __name__ == "__main__":
    asyncio.run(main())

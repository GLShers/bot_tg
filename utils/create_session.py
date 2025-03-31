import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# Импорты для работы с БД
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import requests as rq
from app.database.models import async_session, Bot_data

async def create_bot_session(bot_id):
    """
    Создаёт новую сессию для бота по его ID
    """
    print(f"Создание сессии для бота с ID: {bot_id}")
    
    # Получаем информацию о боте из базы данных
    async with async_session() as session:
        bot_data = await rq.get_bot_data_by_id(bot_id)
        
        if not bot_data:
            print(f"❌ Бот с ID {bot_id} не найден в базе данных")
            return False
        
        print(f"ℹ️ Данные бота получены: API_ID={bot_data.api_id}, ссылка={bot_data.link_bot}")
        
        # Создаем папку для сессий, если она не существует
        sessions_dir = "sessions"
        os.makedirs(sessions_dir, exist_ok=True)
        
        # Формируем имя сессии и путь
        session_name = f"session_{bot_id}_{bot_data.api_id}"
        session_path = os.path.join(sessions_dir, session_name)
        
        print(f"ℹ️ Будет создан файл сессии: {session_name}.session")
        
        # Создаем клиент
        client = TelegramClient(
            session_path,
            bot_data.api_id,
            bot_data.hash_id
        )
        
        try:
            # Подключаемся
            print("ℹ️ Подключение к Telegram...")
            await client.connect()
            
            # Проверяем авторизацию
            if await client.is_user_authorized():
                print(f"✅ Сессия уже авторизована!")
                me = await client.get_me()
                print(f"ℹ️ Пользователь: {me.first_name} (ID: {me.id})")
                return True
            
            print("⚠️ Сессия не авторизована. Начинаем процесс авторизации...")
            
            # Запрашиваем номер телефона
            phone = input("📱 Введите номер телефона (с кодом страны, например +7xxxxxxxxxx): ")
            
            # Отправляем код подтверждения
            await client.send_code_request(phone)
            code = input("🔑 Введите код подтверждения из Telegram: ")
            
            try:
                # Пытаемся авторизоваться с помощью кода
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # Если аккаунт защищен двухфакторной аутентификацией
                password = input("🔐 Введите пароль двухфакторной аутентификации: ")
                await client.sign_in(password=password)
            
            # Проверяем, успешно ли авторизовались
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"✅ Сессия успешно авторизована! Пользователь: {me.first_name} (ID: {me.id})")
                return True
            else:
                print("❌ Не удалось авторизоваться")
                return False
                
        except FloodWaitError as e:
            print(f"❌ Слишком много попыток. Подождите {e.seconds} секунд")
            return False
        except Exception as e:
            print(f"❌ Ошибка при создании сессии: {str(e)}")
            return False
        finally:
            await client.disconnect()
            print("ℹ️ Отключение от Telegram")

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
        await create_bot_session(bot_id)
    except ValueError:
        print("❌ ID бота должен быть числом")
        show_usage()

if __name__ == "__main__":
    asyncio.run(main()) 
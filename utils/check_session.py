import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# Импорты для работы с БД
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import requests as rq
from app.database.models import async_session, Bot_data

async def check_bot_session(bot_id):
    """
    Проверяет сессию бота по его ID
    """
    print(f"Проверка сессии для бота с ID: {bot_id}")
    
    # Получаем информацию о боте из базы данных
    async with async_session() as session:
        bot_data = await rq.get_bot_data_by_id(bot_id)
        
        if not bot_data:
            print(f"❌ Бот с ID {bot_id} не найден в базе данных")
            return False
        
        print(f"ℹ️ Данные бота получены: API_ID={bot_data.api_id}, ссылка={bot_data.link_bot}")
        
        # Ищем файл сессии
        sessions_dir = "sessions"
        if not os.path.exists(sessions_dir):
            print(f"❌ Папка сессий '{sessions_dir}' не найдена")
            return False
            
        session_pattern = f"session_{bot_id}_"
        session_files = [f for f in os.listdir(sessions_dir) if f.startswith(session_pattern) and f.endswith('.session')]
        
        if not session_files:
            print(f"❌ Файл сессии для бота {bot_id} не найден")
            return False
            
        # Берем первый найденный файл сессии
        session_file = session_files[0]
        session_path = os.path.join(sessions_dir, session_file)
        
        print(f"ℹ️ Найден файл сессии: {session_file}")
        
        # Создаем клиент
        client = TelegramClient(
            session_path,
            bot_data.api_id,
            bot_data.hash_id
        )
        
        try:
            # Подключаемся
            print("ℹ️ Подключение к сессии...")
            await client.connect()
            
            # Проверяем авторизацию
            if not await client.is_user_authorized():
                print(f"❌ Сессия {session_file} не авторизована")
                return False
                
            # Проверяем, не заблокирован ли аккаунт
            try:
                me = await client.get_me()
                if not me:
                    print(f"❌ Аккаунт недоступен")
                    return False
                    
                print(f"✅ Сессия активна! Пользователь: {me.first_name} (ID: {me.id})")
                return True
                
            except Exception as e:
                if "USER_DEACTIVATED" in str(e):
                    print(f"❌ Аккаунт заблокирован")
                elif "AUTH_KEY_UNREGISTERED" in str(e):
                    print(f"❌ Сессия недействительна")
                else:
                    print(f"❌ Ошибка при проверке аккаунта: {str(e)}")
                return False
                
        except FloodWaitError as e:
            print(f"❌ Аккаунт временно ограничен. Подождите {e.seconds} секунд")
            return False
        except SessionPasswordNeededError:
            print(f"❌ Требуется двухфакторная аутентификация")
            return False
        except Exception as e:
            print(f"❌ Ошибка при подключении к аккаунту: {str(e)}")
            return False
        finally:
            await client.disconnect()
            print("ℹ️ Отключение от сессии")

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
        await check_bot_session(bot_id)
    except ValueError:
        print("❌ ID бота должен быть числом")
        show_usage()

if __name__ == "__main__":
    asyncio.run(main()) 
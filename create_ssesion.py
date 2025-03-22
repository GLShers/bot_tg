from telethon import TelegramClient
import os

def create_telegram_client(api_id, api_hash, bot_id, bot_link):
    # Формируем имя сессии
    session_name = f"session_{bot_id}_{bot_link}"
    
    # Проверяем, существует ли уже сессия с таким именем
    if os.path.exists(session_name):
        print(f"Сессия с именем {session_name} уже существует.")
    else:
        # Создаем клиента с указанными данными
        client = TelegramClient(session_name, api_id, api_hash)
        print(f"Сессия {session_name} успешно создана.")
    
    return client

# Пример использования:
api_id =  27963624

 # Замените на ваш API ID
api_hash = '61717e5743c024ce795f7c88395b9e18'  # Замените на ваш API HASH (строка)
bot_id = 3  # Замените на id вашего бота
bot_link = 'Ksenia'  # Замените на ссылку вашего бота

# Создаем клиент
client = create_telegram_client(api_id, api_hash, bot_id, bot_link)

# Пример того, как подключить клиента (не забудьте авторизоваться):
client.start()

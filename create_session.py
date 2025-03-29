from telethon import TelegramClient
import asyncio
import app.database.requests as rq
import os

async def create_session(id: int):
    try:
        # Получаем данные бота из базы данных используя правильный метод
        bot_data = await rq.get_bot_data_for_id(id)
        if not bot_data:
            print(f"❌ Бот с ID {id} не найден в базе данных")
            return

        # Проверяем наличие всех необходимых данных
        if not hasattr(bot_data, 'api_id') or not hasattr(bot_data, 'hash_id') or not hasattr(bot_data, 'link_bot'):
            print("❌ В базе данных отсутствуют необходимые данные для бота")
            print(f"Доступные данные: {bot_data}")
            return

        # Создаем папку session, если она не существует
        if not os.path.exists('session'):
            os.makedirs('session')

        # Формируем имя файла сессии с путем к папке session
        session_name = os.path.join('session', f"session_{id}_{bot_data.link_bot}")
        
        print(f"📝 Создание сессии для бота:")
        print(f"• ID бота: {id}")
        print(f"• API ID: {bot_data.api_id}")
        print(f"• Hash ID: {bot_data.hash_id}")
        print(f"• Ссылка: {bot_data.link_bot}")
        
        # Создаем клиент
        client = TelegramClient(
            session_name,
            bot_data.api_id,
            bot_data.hash_id
        )

        # Подключаемся к Telegram
        await client.connect()
        
        # Проверяем подключение
        if client.is_connected():
            print("✅ Успешное подключение к Telegram")
        else:
            print("❌ Ошибка подключения к Telegram")
            return

        print(f"✅ Сессия успешно создана: {session_name}.session")
        print(f"🔗 Ссылка на бота: {bot_data.link_bot}")
        
        # Закрываем соединение
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Произошла ошибка: {str(e)}")
        print("Проверьте, что:")
        print("1. ID бота существует в базе данных")
        print("2. В базе данных есть все необходимые данные (api_id, hash_id, link_bot)")
        print("3. Данные корректны и не пустые")
        print("4. API ID и Hash ID соответствуют данному боту")

async def main():
    # Запрашиваем ID бота у пользователя
    bot_id = input("Введите ID бота: ")
    
    try:
        bot_id = int(bot_id)
    except ValueError:
        print("❌ ID бота должен быть числом")
        return

    # Создаем сессию
    await create_session(bot_id)

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main()) 
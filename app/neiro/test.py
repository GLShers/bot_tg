from telethon import TelegramClient, events
import os

# 🔹 Вставь свои данные
API_ID = 29799282  # Твой API ID
API_HASH = "4a47680d4e1e4a62b4a0fb237e8a2779"  # Твой API Hash
CHANNEL_LINK = "https://t.me/rom2192"  # Ссылка или username канала

# Получаем путь к корневой папке проекта
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sessions_dir = os.path.join(base_dir, "sessions")
os.makedirs(sessions_dir, exist_ok=True)


# Создаем клиент
client = TelegramClient(os.path.join(sessions_dir, f"session_{1}"), API_ID, API_HASH)

async def main():
    await client.start()

    # Получаем entity канала по ссылке или username
    entity = await client.get_entity(CHANNEL_LINK)
    print(f"Мониторинг канала: {entity.title}")

    # Обработчик новых сообщений
    @client.on(events.NewMessage(chats=entity))
    async def new_message_handler(event):
        print(f"\n📩 Новое сообщение в канале {entity.title}:\n{event.message.text}\n")

    # Ждем новых сообщений бесконечно
    await client.run_until_disconnected()

# Запуск
client.loop.run_until_complete(main())


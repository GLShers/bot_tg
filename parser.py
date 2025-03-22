from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import asyncio

# Вставь свои API ID и API HASH сюда
API_ID = 27886981
API_HASH = "823c864cd5fdab8cb471f22f04ae7cda"

async def find_channels_with_comments(keyword):
    async with TelegramClient('session_1_Lera_Travell', API_ID, API_HASH) as client:
        print(f"Ищу каналы по ключевому слову: {keyword}")

        # Поиск каналов по ключевому слову
        result = await client(SearchRequest(
            q=keyword,
            limit=50
        ))

        channels_info = []

        for user_or_channel in result.chats:
            try:
                if getattr(user_or_channel, 'broadcast', False):  # Проверяем только каналы
                    # Получаем полную информацию о канале
                    full_channel = await client(GetFullChannelRequest(user_or_channel))
                    if getattr(full_channel.full_chat, 'linked_chat_id', None):  # Проверка наличия связанного чата
                        title = getattr(user_or_channel, 'title', 'Без названия')
                        participants_count = getattr(full_channel.full_chat, 'participants_count', 'Неизвестно')
                        invite_link = f"https://t.me/{user_or_channel.username}" if getattr(user_or_channel, 'username', None) else "Ссылки нет"

                        channels_info.append({
                            'title': title,
                            'participants_count': participants_count,
                            'invite_link': invite_link
                        })
            except Exception as e:
                print(f"Ошибка при обработке канала: {e}")

        return channels_info


async def main():
    keyword = input("Введите ключевое слово для поиска каналов: ")
    channels = await find_channels_with_comments(keyword)

    if channels:
        print("\nНайденные каналы с открытыми комментариями:")
        for ch in channels:
            print(f"Название: {ch['title']}")
            print(f"Подписчиков: {ch['participants_count']}")
            print(f"Ссылка: {ch['invite_link']}")
            print("-" * 30)
    else:
        print("Каналов с открытыми комментариями не найдено.")


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 23248319  # Замени на свой API_ID
API_HASH = "4897e1c3cfe9c35ae9453ef0f6612585"  # Замени на свой API_HASH

phone = input("Введите номер телефона: ")

async def main():
    client = TelegramClient(phone, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        code = input("Введите код из Telegram: ")

        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input("Введите пароль 2FA: ")
            await client.sign_in(password=password)

    print("✅ Сессия сохранена!")
    await client.disconnect()

asyncio.run(main())

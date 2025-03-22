from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import asyncio
from app.database.models import async_main
import os
from dotenv import load_dotenv
from app.database.requests import check_subscriptions  # Фоновая проверка подписки
import logging
from app.handlers import router
from app.create_ssesion import ses
from app.neiro.neiro_handlers import nero_router
from app.neiro.handlers_test_bot import nero_test_router

load_dotenv()  # Загружаем переменные из .env

BOT_TOKEN = os.getenv("token")  # Получаем токен

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    logging.basicConfig(level=logging.INFO)  # Логирование ставим перед запуском

    await async_main()  # Создаем таблицы в БД (если надо)
    
    dp.include_router(router)
    dp.include_router(nero_router)
    dp.include_router(nero_test_router)
    dp.include_router(ses)

    asyncio.create_task(check_subscriptions())  # ✅ Запускаем проверку подписок до start_polling()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # ⬅️ Теперь бот запустится вместе с проверкой подписки

if __name__ == "__main__":
    try:
        asyncio.run(main())  # ✅ Запускаем event loop
    except KeyboardInterrupt:
        print("\n✅ Упражнение закончено. Бот остановлен.")
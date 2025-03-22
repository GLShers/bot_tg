from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

async def delete_message_safe(message: Message, message_id: int):
    """Безопасное удаление сообщения с обработкой ошибок"""
    try:
        await message.bot.delete_message(message.chat.id, message_id)
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            print(f"Сообщение {message_id} уже удалено или недоступно.")
        else:
            raise e 
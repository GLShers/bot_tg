from app.database.models import async_session
from app.database.models import User, Bot_data, Subscription, UserChannel
from sqlalchemy import select, func, update, delete
from  app.database.models import async_session




async def search_bot_id():
    async with async_session() as session:
        bots = await session.scalar(select(Bot_data))
        return bots.all()

from app.database.models import async_session
from app.database.models import User, Bot_data, Subscription, UserChannel
from sqlalchemy import select, func, update, delete
from  app.database.models import async_session
from datetime import datetime
import logging
import asyncio

#----------------------------------------------------------------------------------------СТАРТОВЫЕ КОМАНДЫ-------------------------------------------------------------------------------------------------

async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        async with session.begin():  # Начинаем транзакцию
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                new_user = User(
                    tg_id=tg_id,
                    link=None,
                    my_chanel_description=None,
                    my_profile_description=None,
                    sub_id=1  # Устанавливаем базовую подписку
                )
                session.add(new_user)
                await session.commit()

            
            
async def set_login(tg_id: int, login: str) -> None: # Запись логина в бд при /start
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user: 
            user.login = login
            await session.commit() 
            
            
            
#----------------------------------------------------------------------------------------ЮЗЕРНЫЕ КОМАНДЫ-------------------------------------------------------------------------------------------------

async def get_user_data(tg_id: int): # Выдать всего юзера из бд
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        return user

async def set_sub_data(tg_id: int, data_sub:str): # Выдать всего юзера из бд
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        user.date_sub=data_sub
        await session.commit()
        return True



async def add_profile_description(tg_id: int, prod_description: str):  
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )
        if not user:
            return None  # Пользователь не найден в базе

        if user.my_profile_description:  
            return user.my_profile_description  # Если уже есть описание, возвращаем его

        user.my_profile_description = prod_description  # Записываем новое описание
        await session.commit()  # Фиксируем изменения
        return True  # Подтверждаем успешное обновление

#----------------------------------------------------------------------------------------КАНАЛЬНЫЕ КОМАНДЫ-------------------------------------------------------------------------------------------------



async def add_link(tg_id: int, channel_link: str): # Добавление ссылки на канал пользователя
    async with async_session() as session:
        # Ищем пользователя по tg_id
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if user:
            existing_user = await session.scalar(
                   select(User).where(User.link == channel_link).where(User.tg_id != tg_id)
               )
            if existing_user:
                   # Если ссылка уже занята другим пользователем
                   return False  # Или верните сообщение
            
            # Если пользователь найден, обновляем его ссылку
            user.link = channel_link
            await session.commit()  # Сохраняем изменения в базе данных
            return True  # Успешно обновили ссылку
        else:
            # Если пользователь с таким tg_id не найден
            return False  # Возвращаем False, так как пользователя нет в базе

            
            
async def get_chanels(tg_id: int): # Список ссылкок всех указанных тг каналов
    async with async_session() as session:
        result = await session.scalars(select(UserChannel.chanel_link).where(UserChannel.user_id == tg_id))
        chanel_links = result.all()  # Получаем список ссылок
        return chanel_links


async def add_chanels(tg_id: int, channels_str: str):
    # Разбиваем строку на отдельные каналы по пробелу
    channels = channels_str.split()

    async with async_session() as session:
        for channel_link in channels:
            # Проверяем, существует ли уже этот канал в базе данных для данного пользователя
            old_user_channel = await session.scalar(
                select(UserChannel).where(
                    UserChannel.user_id == tg_id,
                    UserChannel.chanel_link == channel_link
                )
            )
            if old_user_channel:
                continue  # Если канал уже есть, пропускаем его

            # Добавляем новый канал
            user_channel = UserChannel(user_id=tg_id, chanel_link=channel_link)
            session.add(user_channel)

        await session.commit()
        return True  # Все каналы успешно добавлены


async def count_channels_for_user(user_id):
    async with async_session() as session:
        # Выполняем запрос для подсчёта количества записей в таблице UserChannel для определённого user_id
        result = await session.scalar(
            select(func.count()).where(UserChannel.user_id == user_id)
        )
        return result or 0      

async def update_channel(tg_id, old_link, new_link):
    async with async_session() as session:
        stmt = (
            update(UserChannel)
            .where(UserChannel.user_id == tg_id, UserChannel.chanel_link == old_link)
            .values(chanel_link=new_link)
        )
        await session.execute(stmt)
        await session.commit()


    
async def delete_channel(tg_id, chanel_link):
    async with async_session() as session:
        stmt = delete(UserChannel).where(
            UserChannel.user_id == tg_id,
            UserChannel.chanel_link == chanel_link
        )
        await session.execute(stmt)
        await session.commit()    
    
    
    
    
#----------------------------------------------------------------------------------------ПОДПИСКА КОМАНДЫ-------------------------------------------------------------------------------------------------    
    
    
    
    

async def get_sub_max(tg_id):
    async with async_session() as session:
        result = await session.scalar(select(User.sub_id).where(User.tg_id == tg_id))
        user_sub = await session.scalar(select(Subscription).where(Subscription.id==result))
        return user_sub.max_chanels

    
async def get_sub(tg_id):
    async with async_session() as session:
        result = await session.scalar(select(User.sub_id).where(User.tg_id == tg_id))
        user_sub = await session.scalar(select(Subscription).where(Subscription.id==result))
        return user_sub
    
    
    
    
    
    
    
#----------------------------------------------------------------------------------------БОТА КОМАНДЫ-------------------------------------------------------------------------------------------------
    
    
async def get_bot_id(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        bot_id = user.bot_id
        return bot_id
        
async def get_bot_data(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        bot_id = user.bot_id
        bot = await session.scalar(select(Bot_data).where(Bot_data.id==bot_id))
        
        return bot

async def get_bot_data_for_id(id):
    async with async_session() as session:
        # Преобразуем ID в целое число, если он был передан как строка
        bot_id = int(id)
        bot = await session.scalar(select(Bot_data).where(Bot_data.id == bot_id))
        
        return bot

#---------------------------------------------------------------------------------------- КОМАНДЫ-------------------------------------------------------------------------------------------------

# Пример с сессией, получаем сессию с помощью async_session
from app.database.models import async_session

async def close_db_connection():
    """
    Закрывает соединение с базой данных, если оно открыто.
    """
    try:
        # Создаем сессию с использованием async_session
        async with async_session() as session:
            # Здесь можно выполнять операции с БД
            # Когда блок async with завершится, сессия автоматически закроется
            pass  # Нет необходимости вручную закрывать сессию
        print("Соединение с базой данных закрыто.")
    except Exception as e:
        print(f"Ошибка при закрытии соединения с БД: {e}")



logging.basicConfig(level=logging.INFO)

async def check_subscriptions():
    while True:
        async with async_session() as session:
            current_time = datetime.now()
            query = select(User).where(User.date_sub <= current_time)
            result = await session.execute(query)
            expired_users = result.scalars().all()

            for user in expired_users:
                logging.info(f"❌ Подписка истекла у пользователя {user.tg_id}, меняем на бесплатную")

                # Меняем sub_id на 1 (например, бесплатная подписка)
                user.sub_id = 1  
                await session.commit()  # Фиксируем изменения в БД

            await asyncio.sleep(18000)  # Проверяем каждые 10 минут (600 секунд)



#⁡⁢⁢⁢описание канала ⁡


async def update_chanel_description(tg_id: int, description: str):
    async with async_session() as session:
        # Обновляем описание канала
        stmt = (
            update(User)
            .where(User.tg_id == tg_id)
            .values(my_chanel_description=description)
        )
        await session.execute(stmt)
        await session.commit()
        return True  # Подтверждаем успешное обновление
    
    
async def update_profile_description(tg_id: int, description: str):
    async with async_session() as session:
        # Обновляем описание канала
        stmt = (
            update(User)
            .where(User.tg_id == tg_id)
            .values(my_profile_description=description)
        )
        await session.execute(stmt)
        await session.commit()
        return True  # Подтверждаем успешное обновление
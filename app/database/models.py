from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, Boolean, DateTime, String, ForeignKey, Integer
from datetime import datetime
import asyncio

# Создание движка для SQLite
DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3'  # Файл базы данных будет создан в текущей директории

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Таблица пользователей
class User(Base):
    __tablename__ = 'user_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String, nullable=True)
    date_sub: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Дата подписки
    my_chanel_description: Mapped[str] = mapped_column(String, nullable=True)  # Описание канала
    my_profile_description: Mapped[str] = mapped_column(String, nullable=True)  # БИО профиля
    bot_id: Mapped[int] = mapped_column(ForeignKey('bot_data.id'), nullable=True)
    sub_id: Mapped[int] = mapped_column(ForeignKey('subscription.id'), default=1)
    link: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id})>"

# Таблица подписок
class Subscription(Base):
    __tablename__ = 'subscription'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    max_chanels: Mapped[int] = mapped_column(Integer, nullable=True)  # Максимальное кол-во каналов
    date_day: Mapped[int] = mapped_column(Integer, nullable=True)
    sub_name: Mapped[str] = mapped_column(String, nullable=False)  # Название подписки

    def __repr__(self):
        return f"<Subscription(id={self.id}, max_chanels={self.max_chanels})>"

# Таблица ботов
class Bot_data(Base):
    __tablename__ = 'bot_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    hash_id: Mapped[str] = mapped_column(String, nullable=False)
    api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    link_bot: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"<Bot_data(id={self.id}, api_id={self.api_id})>"

# Таблица каналов пользователя
class UserChannel(Base):
    __tablename__ = 'user_channels'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_data.tg_id"))  # Связь с юзером
    chanel_link: Mapped[str] = mapped_column(String, nullable=True)  # Ссылка на канал

# Функция создания базы
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных успешно создана!")

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(async_main())
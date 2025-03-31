from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import asyncio
from typing import List, Dict, Tuple
import re
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from app.database import requests as rq

def extract_username(channel_link: str) -> str:
    """
    Извлекает username канала из ссылки
    """
    # Убираем http:// или https:// если есть
    channel_link = channel_link.replace('https://', '').replace('http://', '')
    
    # Убираем t.me/ если есть
    if 't.me/' in channel_link:
        channel_link = channel_link.split('t.me/')[-1]
    
    # Убираем @ если есть
    if channel_link.startswith('@'):
        channel_link = channel_link[1:]
    
    return channel_link

async def get_user_session(bot_id: int) -> Tuple[TelegramClient, str]:
    """
    Получает сессию пользователя по bot_id
    Возвращает (клиент, сообщение об ошибке)
    """
    try:
        # Получаем информацию о боте из базы данных
        bot_data = await rq.get_bot_data_by_id(bot_id)
        if not bot_data:
            return None, "Бот не найден в базе данных"
            
        # Ищем файл сессии
        sessions_dir = "sessions"
        session_pattern = f"session_{bot_id}_"
        session_files = [f for f in os.listdir(sessions_dir) if f.startswith(session_pattern) and f.endswith('.session')]
        
        if not session_files:
            return None, "Файл сессии не найден"
            
        # Берем первый найденный файл сессии
        session_file = session_files[0]
        session_path = os.path.join(sessions_dir, session_file)
        
        # Создаем клиент
        client = TelegramClient(
            session_path,
            bot_data.api_id,
            bot_data.hash_id
        )
        
        try:
            # Подключаемся
            await client.connect()
            
            # Проверяем авторизацию
            if not await client.is_user_authorized():
                return None, "Сессия не авторизована"
                
            # Проверяем, не заблокирован ли аккаунт
            try:
                me = await client.get_me()
                if not me:
                    return None, "Аккаунт недоступен"
            except Exception as e:
                if "USER_DEACTIVATED" in str(e):
                    return None, "Аккаунт заблокирован"
                elif "AUTH_KEY_UNREGISTERED" in str(e):
                    return None, "Сессия недействительна"
                raise e
                
            return client, None
            
        except FloodWaitError as e:
            return None, f"Аккаунт временно ограничен. Подождите {e.seconds} секунд"
        except SessionPasswordNeededError:
            return None, "Требуется двухфакторная аутентификация"
        except Exception as e:
            return None, f"Ошибка при подключении к аккаунту: {str(e)}"
            
    except Exception as e:
        return None, f"Ошибка при получении сессии: {str(e)}"

async def check_channel(client: TelegramClient, channel_link: str) -> Tuple[bool, str]:
    """
    Проверяет канал на доступность
    Возвращает (успех проверки, сообщение об ошибке)
    """
    try:
        # Извлекаем username из ссылки
        username = extract_username(channel_link)
        
        # Проверяем, что username не пустой и содержит только допустимые символы
        if not username or not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Некорректная ссылка на канал"
        
        # Пробуем получить информацию о канале
        try:
            print(f"DEBUG: Проверка канала @{username}")
            entity = await client.get_entity(f"@{username}")
            
            # Проверяем тип канала (канал или супергруппа)
            channel_type = type(entity).__name__
            print(f"DEBUG: Тип канала @{username}: {channel_type}")
            
            # Базовая проверка доступности
            if channel_type in ['Channel', 'Chat', 'Supergroup']:
                return True, f"Канал успешно проверен (тип: {channel_type})"
            else:
                return False, f"Неподдерживаемый тип канала: {channel_type}"
                
        except Exception as e:
            print(f"DEBUG: Ошибка при проверке канала @{username}: {str(e)}")
            if "not found" in str(e).lower() or "CHAT_NOT_FOUND" in str(e):
                return False, "Канал не найден или недоступен"
            elif "private" in str(e).lower() or "CHAT_PRIVATE" in str(e):
                return False, "Канал является приватным"
            elif "flood wait" in str(e).lower() or "FLOOD_WAIT" in str(e):
                return False, "Превышен лимит запросов. Попробуйте позже"
            return False, f"Ошибка при доступе к каналу: {str(e)}"
            
    except Exception as e:
        print(f"DEBUG: Неизвестная ошибка при проверке канала: {str(e)}")
        return False, f"Неизвестная ошибка: {str(e)}"

async def check_channels(user_id: int, channels: List[str]) -> Dict[str, Tuple[bool, str]]:
    """
    Проверяет список каналов и возвращает результаты проверки
    """
    try:
        # Получаем данные пользователя
        user = await rq.get_user_data(user_id)
        
        # Проверка на None
        if user is None:
            print(f"DEBUG: get_user_data вернул None для пользователя {user_id}")
            return {channel: (False, "Не удалось получить информацию о пользователе") for channel in channels}
        
        # Проверка наличия bot_id
        if not hasattr(user, 'bot_id') or user.bot_id is None:
            print(f"DEBUG: У пользователя {user_id} отсутствует bot_id")
            return {channel: (False, "У пользователя не настроен бот для комментирования") for channel in channels}
        
        print(f"DEBUG: Получен bot_id: {user.bot_id} для пользователя {user_id}")
            
        # Получаем сессию пользователя
        client, error = await get_user_session(user.bot_id)
        if error:
            print(f"DEBUG: Ошибка при получении сессии для bot_id {user.bot_id}: {error}")
            return {channel: (False, error) for channel in channels}
            
        try:
            # Проверяем каждый канал
            results = {}
            for channel in channels:
                try:
                    success, message = await check_channel(client, channel)
                    results[channel] = (success, message)
                except FloodWaitError as e:
                    # Если получили FloodWaitError, прекращаем проверку остальных каналов
                    results[channel] = (False, f"Превышен лимит запросов. Подождите {e.seconds} секунд")
                    # Добавляем сообщение об ошибке для остальных каналов
                    for remaining_channel in channels[channels.index(channel) + 1:]:
                        results[remaining_channel] = (False, "Проверка прервана из-за превышения лимита запросов")
                    break
                except Exception as e:
                    results[channel] = (False, f"Ошибка при проверке канала: {str(e)}")
            return results
            
        finally:
            # Закрываем клиент
            if client:
                await client.disconnect()
            
    except Exception as e:
        print(f"DEBUG: Общая ошибка при проверке каналов: {str(e)}")
        return {channel: (False, f"Ошибка при проверке каналов: {str(e)}") for channel in channels}
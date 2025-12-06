import logging
import re
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from typing import Optional

def escape_html(text: str) -> str:
    """Экранирует специальные символы HTML"""
    if not text:
        return text
    
    # Символы, которые нужно экранировать в HTML
    special_chars = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }
    
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    
    return text

logger = logging.getLogger(__name__)

class ChatLogger:
    """Сервис для логирования всех сообщений в группу"""
    
    def __init__(self, bot: Bot, log_chat_id: int):
        self.bot = bot
        self.log_chat_id = log_chat_id
    
    async def log_user_message(self, message: Message, user_name: str = None) -> None:
        """Логирует сообщение пользователя"""
        try:
            user_name = user_name or message.from_user.first_name or "Пользователь"
            user_id = message.from_user.id
            
            # Формируем текст для логирования
            log_text = f"🧑 <b>{user_name}</b> (ID: <code>{user_id}</code>):\n"
            
            if message.text:
                log_text += f"💬 {escape_html(message.text)}"
            elif message.photo:
                log_text += f"📷 Фото + подпись: {escape_html(message.caption or 'Без подписи')}"
            elif message.document:
                log_text += f"📄 Документ: {escape_html(message.document.file_name)}"
            elif message.voice:
                log_text += f"🎤 Голосовое сообщение"
            elif message.video:
                log_text += f"🎥 Видео + подпись: {escape_html(message.caption or 'Без подписи')}"
            else:
                log_text += f"📎 Другой тип сообщения"
            
            await self.bot.send_message(
                chat_id=self.log_chat_id,
                text=log_text,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при логировании сообщения пользователя: {e}")
    
    async def log_bot_response(self, response_text: str, user_name: str = None, user_id: int = None) -> None:
        """Логирует ответ бота"""
        try:
            user_name = user_name or "Пользователь"
            user_id_text = f" (ID: <code>{user_id}</code>)" if user_id else ""
            
            log_text = f"🤖 <b>Бот отвечает {user_name}</b>{user_id_text}:\n"
            log_text += f"💬 {escape_html(response_text)}"
            
            await self.bot.send_message(
                chat_id=self.log_chat_id,
                text=log_text,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при логировании ответа бота: {e}")
    
    async def log_callback_query(self, callback: CallbackQuery, action: str) -> None:
        """Логирует нажатие кнопок"""
        try:
            user_name = callback.from_user.first_name or "Пользователь"
            user_id = callback.from_user.id
            
            log_text = f"🔘 <b>{user_name}</b> (ID: <code>{user_id}</code>) нажал кнопку:\n"
            log_text += f"📱 {escape_html(action)} (data: {escape_html(callback.data)})"
            
            await self.bot.send_message(
                chat_id=self.log_chat_id,
                text=log_text,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при логировании нажатия кнопки: {e}")
    
    async def log_state_change(self, user_id: int, user_name: str, old_state: str, new_state: str) -> None:
        """Логирует изменение состояния пользователя"""
        try:
            log_text = f"🔄 <b>Изменение состояния</b> для {user_name} (ID: <code>{user_id}</code>):\n"
            log_text += f"📊 {escape_html(old_state)} → {escape_html(new_state)}"
            
            await self.bot.send_message(
                chat_id=self.log_chat_id,
                text=log_text,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при логировании изменения состояния: {e}")
    
    async def log_error(self, error: str, user_id: int = None, user_name: str = None) -> None:
        """Логирует ошибки"""
        try:
            user_info = f" для {user_name} (ID: <code>{user_id}</code>)" if user_id and user_name else ""
            log_text = f"❌ <b>Ошибка</b>{user_info}:\n"
            log_text += f"🚨 {escape_html(error)}"
            
            await self.bot.send_message(
                chat_id=self.log_chat_id,
                text=log_text,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при логировании ошибки: {e}")


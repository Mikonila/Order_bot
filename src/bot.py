import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .config import BOT_TOKEN, LOG_CHAT_ID
from .handlers import user_info
from .services.chat_logger import ChatLogger

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Запуск бота...")
        logger.info(f"Токен: {BOT_TOKEN[:10]}...")
        
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Инициализируем ChatLogger
        chat_logger = ChatLogger(bot, LOG_CHAT_ID)
        
        # Передаем chat_logger в хендлеры
        user_info.set_chat_logger(chat_logger)
        dp.include_router(user_info.router)
        
        logger.info("Бот запущен, начинаю polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
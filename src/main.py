from src.config.settings import get_settings
from src.config.logger import setup_loggers
from src.core.rss_reader import RssReader
from src.core.ai_processor import AIProcessor
from src.core.telegram_poster import TelegramPoster
from src.db.crud import DBCrud
import asyncio
import logging

async def main():
    # Инициализация
    config = get_settings()
    setup_loggers(config)
    
    logger = logging.getLogger('app')
    data_logger = logging.getLogger('data')
    
    logger.info("Starting application")
    
    # Компоненты
    db = DBCrud(config.DATABASE_URL)
    reader = RssReader(config.SOURCES_PATH)
    ai = AIProcessor(config.DEEPSEEK_API_KEY)
    poster = TelegramPoster(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHANNEL_ID)
    
    # Обработка
    entries = reader.get_entries()
    logger.info(f"Found {len(entries)} new articles")
    
    for entry in entries:
        if db.is_processed(entry["id"]):
            continue
            
        summary = ai.generate_summary(entry["content"], entry["categories"])
        if summary:
            if await poster.send_message(summary, entry["url"]):
                db.save_article({
                    "id": entry["id"],
                    "source_url": entry["url"]
                })

if __name__ == "__main__":
    asyncio.run(main())

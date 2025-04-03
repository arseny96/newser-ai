from src.config.settings import get_settings
from src.config.logger import setup_loggers
from src.core.json_reader import JsonReader
from src.core.telegram_poster import TelegramPoster
from src.db.crud import DBCrud
import asyncio
import logging

from src.core.providers.deepseek import DeepSeekProcessor
from src.core.providers.openai import OpenAIProcessor

async def main():
    config = get_settings()
    setup_loggers(config)
    logger = logging.getLogger('app')
    
    # Validate AI provider
    allowed_providers = ["deepseek", "openai"]
    if config.WORKING_MODEL_AI_PROVIDER not in allowed_providers:
        raise ValueError(f"Unsupported AI provider: {config.WORKING_MODEL_AI_PROVIDER}")

    # Initialize components
    db = DBCrud(config.DATABASE_URL)
    reader = JsonReader(config.ARTICLES_DIR)
    
    # AI Provider selection
    if config.WORKING_MODEL_AI_PROVIDER == "deepseek":
        ai = DeepSeekProcessor(
            api_key=config.DEEPSEEK_API_KEY,
            model_name=config.WORKING_MODEL_AI_NAME,
            timeout=config.AI_API_TIMEOUT
        )
    else:
        ai = OpenAIProcessor(
            api_key=config.OPENAI_API_KEY,
            model_name=config.WORKING_MODEL_AI_NAME,
            timeout=config.AI_API_TIMEOUT
        )

    poster = TelegramPoster(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHANNEL_ID)
    
    # Processing pipeline
    entries = reader.get_entries()
    logger.info(f"Processing {len(entries)} articles")
    
    for entry in entries:
        if not entry:
            continue
            
        if db.is_processed(entry["id"]):
            logger.debug(f"Skipping processed article: {entry['id']}")
            continue
            
        summary = ai.generate_summary(entry["content"])  # Убрали параметр categories
        if summary:
            if await poster.send_message(summary, entry["url"]):
                db.save_article({
                    "id": entry["id"],
                    "source_url": entry["url"]
                })
                logger.info(f"Processed article: {entry['id']}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger('app').info("Application stopped by user")
    except Exception as e:
        logging.getLogger('app').error(f"Fatal error: {str(e)}", exc_info=True)
        raise

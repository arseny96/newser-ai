import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

def get_feed_list():
    rss_feeds = os.getenv('RSS_FEEDS', '')
    return [url.strip() for url in rss_feeds.split(',') if url.strip()]

def setup_loggers():
    app_logger = logging.getLogger('app')
    app_logger.setLevel(os.getenv('APP_LOG_LEVEL', 'INFO').upper())

    data_logger = logging.getLogger('data')
    data_logger.setLevel(os.getenv('DATA_LOG_LEVEL', 'DEBUG').upper())
    data_logger.propagate = False

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # App Log Handlers
    app_file_handler = RotatingFileHandler(
        filename=os.getenv('APP_LOG_FILE', 'app.log'),
        maxBytes=int(os.getenv('APP_LOG_MAX_SIZE', 1048576)),
        backupCount=int(os.getenv('APP_LOG_BACKUP_COUNT', 3)),
        encoding='utf-8'
    )
    app_file_handler.setFormatter(formatter)
    app_logger.addHandler(app_file_handler)

    # Data Log Handlers
    data_file_handler = RotatingFileHandler(
        filename=os.getenv('DATA_LOG_FILE', 'data.log'),
        maxBytes=int(os.getenv('DATA_LOG_MAX_SIZE', 5242880)),
        backupCount=int(os.getenv('DATA_LOG_BACKUP_COUNT', 5)),
        encoding='utf-8'
    )
    data_file_handler.setFormatter(formatter)
    data_logger.addHandler(data_file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)

    # Third-party logging
    for lib in ['urllib3', 'httpcore', 'httpx']:
        logging.getLogger(lib).addHandler(data_file_handler)

    return app_logger, data_logger

app_logger, data_logger = setup_loggers()

CONFIG = {
    'telegram': {
        'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'channel_id': os.getenv('TELEGRAM_CHANNEL_ID')
    },
    'deepseek': {
        'api_key': os.getenv('DEEPSEEK_API_KEY'),
        'api_url': "https://api.deepseek.com/v1/chat/completions",
        'model': "deepseek-chat"
    },
    'database': 'processed_articles.db',
    'check_interval': int(os.getenv('CHECK_INTERVAL', 3600)),
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) NewsBot/1.0',
    'timeouts': {
        'telegram': 30,
        'http': 15,
        'ai_api': 30
    },
    'max_message_length': 4096
}

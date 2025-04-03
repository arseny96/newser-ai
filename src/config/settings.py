from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # AI Configuration
    WORKING_MODEL_AI_PROVIDER: str = Field(..., env="WORKING_MODEL_AI_PROVIDER")
    WORKING_MODEL_AI_NAME: str = Field(..., env="WORKING_MODEL_AI_NAME")
    AI_API_TIMEOUT: int = Field(..., env="AI_API_TIMEOUT")
    AI_MAX_TEXT_LENGTH: int = 5000

    # API Keys
    DEEPSEEK_API_KEY: str = Field(..., env="DEEPSEEK_API_KEY")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL_ID: str = Field(..., env="TELEGRAM_CHANNEL_ID")

    # Data Configuration
    ARTICLES_DIR: str = "data/new_articles"
    DATABASE_URL: str = "sqlite:///processed.db"

    # Logging
    APP_LOG_LEVEL: str = "INFO"
    DATA_LOG_LEVEL: str = "DEBUG"
    APP_LOG_FILE: str = "app.log"
    DATA_LOG_FILE: str = "data.log"
    LOG_MAX_SIZE: int = 1048576  # 1MB
    LOG_BACKUP_COUNT: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

def get_settings():
    return Settings()

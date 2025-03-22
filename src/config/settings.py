from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # Обязательные настройки
    DEEPSEEK_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHANNEL_ID: str
    SOURCES_PATH: str = "data/sources.yml"
    DATABASE_URL: str = "sqlite:///processed.db"

    # Логирование
    APP_LOG_LEVEL: str = "INFO"
    DATA_LOG_LEVEL: str = "DEBUG"
    APP_LOG_FILE: str = "app.log"
    DATA_LOG_FILE: str = "data.log"
    LOG_MAX_SIZE: int = 1048576  # 1MB
    LOG_BACKUP_COUNT: int = 3

    # Таймауты (добавьте эти поля)
    CHECK_INTERVAL: int = Field(3600, alias="CHECK_INTERVAL")
    HTTP_TIMEOUT: int = Field(15, alias="HTTP_TIMEOUT")
    TELEGRAM_TIMEOUT: int = Field(30, alias="TELEGRAM_TIMEOUT")
    AI_API_TIMEOUT: int = Field(30, alias="AI_API_TIMEOUT")
    MAX_MESSAGE_LENGTH: int = Field(4096, alias="MAX_MESSAGE_LENGTH")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорировать лишние переменные

def get_settings() -> Settings:
    return Settings()

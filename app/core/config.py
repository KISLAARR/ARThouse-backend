"""
Настройки приложения из .env файла.
Pydantic Settings автоматически читает переменные окружения.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator


class Settings(BaseSettings):
    """Все настройки приложения в одном месте"""
    
    # --- Настройки приложения ---
    APP_NAME: str = "ARThouse API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # --- Настройки сервера ---
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # --- Настройки базы данных ---
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "arthouse_db"
    POSTGRES_PORT: str = "5432"
    
    @property
    def DATABASE_URL(self) -> str:
        """Формируем строку подключения к БД"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # --- Настройки безопасности ---
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        """Говорим Pydantic читать из .env файла"""
        env_file = ".env"
        case_sensitive = True


# Создаём глобальный экземпляр настроек
settings = Settings()
"""
Настройки приложения. app/core/config.py
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pydantic_core import MultiHostUrl
from typing_extensions import Self


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    Загружает переменные из .env файла.
    """
    # Проект
    PROJECT_NAME: str = "ARThouse API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    API_V1_PREFIX: str = "/api/v1"  # Добавлено для совместимости с security.py
    DEBUG: bool = False

    # База данных - отдельные компоненты
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "arthouse_db"
    POSTGRES_PORT: str = "5432"
    
    # Собираем DATABASE_URL из компонентов, если он не задан явно
    DATABASE_URL: Optional[str] = None

    # Безопасность
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://localhost:8833",
        "http://127.0.0.1:8833"
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    def model_post_init(self, __context) -> None:
        """Собираем DATABASE_URL из компонентов, если он не задан явно."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = str(
                MultiHostUrl.build(
                    scheme="postgresql",
                    username=self.POSTGRES_USER,
                    password=self.POSTGRES_PASSWORD,
                    host=self.POSTGRES_SERVER,
                    port=int(self.POSTGRES_PORT),
                    path=self.POSTGRES_DB,
                )
            )

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Разрешаем лишние поля, если они вдруг появятся, но лучше их явно описать
        extra = "ignore"


settings = Settings()
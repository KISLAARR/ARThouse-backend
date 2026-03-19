"""
Настройка подключения к PostgreSQL через SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Создаём движок SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG,
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для FastAPI.
    Создаёт новую сессию БД для каждого запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
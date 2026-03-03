"""
Настройка подключения к базе данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Создаём движок SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Сессия для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии БД.
    Автоматически закрывает сессию после запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

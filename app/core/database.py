"""
<<<<<<< HEAD
Настройка подключения к PostgreSQL через SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
=======
Настройка подключения к базе данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511

from app.core.config import settings

# Создаём движок SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
<<<<<<< HEAD
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
=======
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
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
    """
    db = SessionLocal()
    try:
        yield db
    finally:
<<<<<<< HEAD
        db.close()
=======
        db.close()
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511

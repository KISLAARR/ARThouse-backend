"""
Базовый репозиторий с общими CRUD операциями.
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый класс для всех репозиториев"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить несколько записей"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, **kwargs) -> ModelType:
        """Создать новую запись"""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, db_obj: ModelType, **kwargs) -> ModelType:
        """Обновить запись"""
        for field, value in kwargs.items():
            if value is not None:
                setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, db_obj: ModelType) -> None:
        """Удалить запись"""
        self.db.delete(db_obj)
        self.db.commit()
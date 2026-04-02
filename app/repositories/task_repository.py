"""
Репозиторий для работы с задачами.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Репозиторий для работы с задачами."""

    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_apartment(self, apartment_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Получить задачи по ID квартиры."""
        return self.db.query(Task).filter(
            Task.apartment_id == apartment_id
        ).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Получить задачи, назначенные конкретному пользователю."""
        return self.db.query(Task).join(Apartment).filter(
            Apartment.user_id == user_id
        ).offset(skip).limit(limit).all()

    def get_by_room(self, room_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Получить задачи по комнате."""
        return self.db.query(Task).filter(
            Task.room_id == room_id
        ).offset(skip).limit(limit).all()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Получить задачи по статусу."""
        return self.db.query(Task).filter(
            Task.status == status
        ).offset(skip).limit(limit).all()

    def update_status(self, task_id: int, status: str) -> Optional[Task]:
        """Обновить статус задачи."""
        db_task = self.get(task_id)
        if not db_task:
            return None
        
        db_task.status = status
        if status == "completed":
            from datetime import datetime
            db_task.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

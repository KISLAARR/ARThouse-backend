"""
Репозиторий для работы с задачами.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    def get_by_apartment(self, apartment_id: int) -> List[Task]:
        return self.db.query(Task).filter(
            Task.apartment_id == apartment_id
        ).all()
    
    def get_by_user(self, user_id: int) -> List[Task]:
        return self.db.query(Task).filter(
            Task.assigned_to == user_id
        ).all()
    
    def get_by_room(self, room_id: int) -> List[Task]:
        return self.db.query(Task).filter(
            Task.room_id == room_id
        ).all()
    
    def get_by_status(self, status: str) -> List[Task]:
        return self.db.query(Task).filter(
            Task.status == status
        ).all()
    
    def update_status(self, task_id: int, status: str) -> Optional[Task]:
        task = self.get(task_id)
        
        if not task:
            return None
        
        task.status = status
        
        if status == "completed":
            from datetime import datetime
            task.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        return task

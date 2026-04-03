"""
Сервис для работы с задачами.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.task_repository import TaskRepository
from app.repositories.apartment_repository import ApartmentRepository
from app.repositories.user_repository import UserRepository
from app.models.room import Room
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.apartment_repo = ApartmentRepository(db)
        self.user_repo = UserRepository(db)
    
    
    def _check_apartment_access(self, user_id: int, apartment_id: int):
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )
        return apartment
    
    def _check_user_exists(self, user_id: int):
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return user
    
    def _check_room_in_apartment(self, room_id: int, apartment_id: int):
        room = self.db.query(Room).filter(
            Room.id == room_id,
            Room.apartment_id == apartment_id
        ).first()
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Комната не принадлежит квартире"
            )
        return room
    
    
    def get_tasks_by_apartment(self, user_id: int, apartment_id: int) -> List[Task]:
        self._check_apartment_access(user_id, apartment_id)
        return self.task_repo.get_by_apartment(apartment_id)
    
    def get_task(self, user_id: int, task_id: int) -> Task:
        task = self.task_repo.get(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        
        self._check_apartment_access(user_id, task.apartment_id)
        return task
    
    def get_my_tasks(self, user_id: int) -> List[Task]:
        return self.task_repo.get_by_user(user_id)
    
    def create_task(self, user_id: int, task_data: TaskCreate) -> Task:
        self._check_apartment_access(user_id, task_data.apartment_id)
        
        if task_data.assigned_to:
            self._check_user_exists(task_data.assigned_to)
        
        if task_data.room_id:
            self._check_room_in_apartment(task_data.room_id, task_data.apartment_id)
        
        return self.task_repo.create(
            **task_data.dict(exclude_unset=True)
        )
    
    def update_task(self, user_id: int, task_id: int, task_data: TaskUpdate) -> Task:
        task = self.get_task(user_id, task_id)
        
        update_data = task_data.dict(exclude_unset=True)
        
        if "assigned_to" in update_data and update_data["assigned_to"]:
            self._check_user_exists(update_data["assigned_to"])
        
        if "room_id" in update_data and update_data["room_id"]:
            self._check_room_in_apartment(update_data["room_id"], task.apartment_id)
        
        return self.task_repo.update(task, **update_data)
    
    def update_task_status(self, user_id: int, task_id: int, status_value: str) -> Task:
        task = self.get_task(user_id, task_id)
        
        updated = self.task_repo.update_status(task_id, status_value)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        
        return updated
    
    def delete_task(self, user_id: int, task_id: int) -> bool:
        task = self.get_task(user_id, task_id)
        self.task_repo.delete(task)
        return True

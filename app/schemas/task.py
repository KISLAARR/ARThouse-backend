"""
Pydantic схемы для задач.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """Общая схема задачи"""
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    status: str = Field(default="pending")
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None


# --- Схемы для запросов ---
class TaskCreate(TaskBase):
    """Создание новой задачи"""
    apartment_id: int = Field(..., gt=0)


class TaskUpdate(BaseModel):
    """Обновление существующей задачи (все поля опциональны)"""
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    priority: Optional[str] = Field(None)
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    """Обновление только статуса задачи"""
    status: str = Field(...)


# --- Схемы для ответов ---
class TaskResponse(TaskBase):
    """Ответ с данными задачи"""
    id: int
    apartment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

"""
Pydantic схемы для задач (Task).
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.task import TaskPriority

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    status: Optional[str] = Field(
        default="pending",
        description="Статус задачи: pending, in_progress, completed"
    )
    
    priority: Optional[TaskPriority] = Field(
        default=TaskPriority.MEDIUM,
        description="low, medium, high, urgent"
    )
    
    due_date: Optional[datetime] = None
    
    room_id: Optional[int] = Field(None, description="ID комнаты")
    assigned_to: Optional[int] = Field(None, description="ID пользователя или робота")


class TaskCreate(TaskBase):
    apartment_id: int = Field(..., description="ID квартиры")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    status: Optional[str] = Field(
        None,
        description="Статус задачи"
    )
    
    priority: Optional[int] = Field(
        None,
        ge=1,
        le=5
    )
    
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="Новый статус задачи"
    )


class TaskResponse(TaskBase):
    id: int
    apartment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

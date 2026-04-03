"""
Pydantic схемы для задач (Task).
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.task import TaskPriority


ALLOWED_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled']


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    status: Optional[str] = Field(
        default="pending",
        description="Статус задачи: pending, in_progress, completed, cancelled"
    )
    
    priority: Optional[TaskPriority] = Field(
        default=TaskPriority.MEDIUM,
        description="low, medium, high, urgent"
    )
    
    due_date: Optional[datetime] = None
    
    room_id: Optional[int] = Field(None, description="ID комнаты")
    assigned_to: Optional[int] = Field(None, description="ID пользователя или робота")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        if v not in ALLOWED_STATUSES:
            raise ValueError(f'Статус должен быть одним из: {ALLOWED_STATUSES}')
        return v


class TaskCreate(TaskBase):
    apartment_id: int = Field(..., description="ID квартиры")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    
    status: Optional[str] = Field(
        None,
        description="Статус задачи"
    )
    
    priority: Optional[TaskPriority] = Field(
        None,
        description="low, medium, high, urgent"
    )
    
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        if v not in ALLOWED_STATUSES:
            raise ValueError(f'Статус должен быть одним из: {ALLOWED_STATUSES}')
        return v


class TaskStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="Новый статус задачи"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ALLOWED_STATUSES:
            raise ValueError(f'Статус должен быть одним из: {ALLOWED_STATUSES}')
        return v


class TaskResponse(TaskBase):
    id: int
    apartment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

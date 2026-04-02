from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    status: str = Field("pending", description="Статус: pending, in_progress, completed, cancelled")
    priority: str = Field("medium", description="Приоритет: low, medium, high")
    due_date: Optional[datetime] = Field(None, description="Дедлайн выполнения")
    room_id: Optional[int] = Field(None, description="ID комнаты")
    assigned_to: Optional[int] = Field(None, description="ID пользователя-исполнителя")

class TaskCreate(TaskBase):
    apartment_id: int = Field(..., description="ID квартиры, к которой привязана задача")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None

class TaskStatusUpdate(BaseModel):
    status: str = Field(..., description="Новый статус задачи")

class TaskResponse(TaskBase):
    id: int
    apartment_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

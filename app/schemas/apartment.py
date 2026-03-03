"""
Pydantic схемы для помещений, комнат и задач
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# === Комнаты ===

class RoomBase(BaseModel):
    name: str
    room_type: str
    floor: int = 1
    area: Optional[float] = None
    position_x: float = 0
    position_y: float = 0
    width: float = 100
    height: float = 100


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    apartment_id: int
    
    class Config:
        from_attributes = True


# === Предметы ===

class ItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    tags: Optional[List[str]] = None


class ItemCreate(ItemBase):
    room_id: int


class ItemResponse(ItemBase):
    id: int
    room_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# === Задачи ===

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1
    due_date: Optional[datetime] = None
    is_recurring: Optional[str] = None


class TaskCreate(TaskBase):
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    apartment_id: int
    room_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# === Помещения ===

class ApartmentBase(BaseModel):
    name: str = "Мой дом"
    address: Optional[str] = None
    apartment_type: str = "apartment"
    total_area: Optional[float] = None
    rooms_count: Optional[int] = None
    floors_count: int = 1
    wall_height: float = 2.7


class ApartmentCreate(ApartmentBase):
    pass


class ApartmentUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    total_area: Optional[float] = None
    rooms_count: Optional[int] = None
    floors_count: Optional[int] = None
    wall_height: Optional[float] = None
    floor_plan: Optional[Any] = None


class ApartmentResponse(ApartmentBase):
    id: int
    owner_id: int
    floor_plan: Optional[Any] = None
    created_at: datetime
    rooms: List[RoomResponse] = []
    
    class Config:
        from_attributes = True


class ApartmentListResponse(ApartmentBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

"""
Pydantic схемы для квартиры/помещения.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- Базовые схемы ---
class ApartmentBase(BaseModel):
    """Общая схема квартиры"""
    name: str = Field(..., min_length=1, max_length=100)
    ceiling_height: Optional[float] = Field(None, ge=1.0, le=10.0)
    square_meters: Optional[float] = Field(None, ge=1.0, le=1000.0)
    floors: Optional[int] = Field(None, ge=1, le=3)
    rooms_count: Optional[int] = Field(None, ge=1, le=20)
    address: Optional[str] = Field(None, max_length=200)


# --- Схемы для запросов ---
class ApartmentCreate(ApartmentBase):
    """Создание новой квартиры"""
    pass


class ApartmentUpdate(BaseModel):
    """Обновление существующей квартиры (все поля опциональны)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ceiling_height: Optional[float] = Field(None, ge=1.0, le=10.0)
    square_meters: Optional[float] = Field(None, ge=1.0, le=1000.0)
    floors: Optional[int] = Field(None, ge=1, le=3)
    rooms_count: Optional[int] = Field(None, ge=1, le=20)
    address: Optional[str] = Field(None, max_length=200)


# --- Схемы для ответов ---
class ApartmentResponse(ApartmentBase):
    """Ответ с данными квартиры"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
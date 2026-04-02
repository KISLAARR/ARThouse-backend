"""
Pydantic схемы для комнаты.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    room_type: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = Field(None, ge=0, le=100)
    area: Optional[float] = Field(None, ge=0.0, le=1000.0)

    position_x: Optional[float] = None
    position_y: Optional[float] = None
    width: Optional[float] = Field(None, ge=0.0)
    height: Optional[float] = Field(None, ge=0.0)


class RoomCreate(RoomBase):
    apartment_id: int


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    room_type: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = Field(None, ge=0, le=100)
    area: Optional[float] = Field(None, ge=0.0, le=1000.0)

    position_x: Optional[float] = None
    position_y: Optional[float] = None
    width: Optional[float] = Field(None, ge=0.0)
    height: Optional[float] = Field(None, ge=0.0)


class RoomResponse(RoomBase):
    id: int
    apartment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    # Индексы
    __table_args__ = (
        Index('idx_rooms_apartment', 'apartment_id'),
    )

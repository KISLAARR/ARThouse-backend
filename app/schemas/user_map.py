"""
Pydantic схемы для карты пользователя.
"""
from typing import Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class UserMapSaveRequest(BaseModel):
    map_json: Dict[str, Any] = Field(..., description="JSON карты пользователя")


class UserMapResponse(BaseModel):
    user_id: int
    map_json: Dict[str, Any]
    revision: int
    updated_at: datetime

    class Config:
        from_attributes = True
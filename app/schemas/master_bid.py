"""
Pydantic схемы для откликов мастеров.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.master_bid import MasterBidStatus


class MasterBidCreate(BaseModel):
    price_offer: Optional[str] = Field(None, max_length=120)
    duration_offer: Optional[str] = Field(None, max_length=120)
    message: Optional[str] = None


class MasterBidResponse(BaseModel):
    id: int
    project_id: int
    master_user_id: int

    price_offer: Optional[str] = None
    duration_offer: Optional[str] = None
    message: Optional[str] = None

    status: MasterBidStatus

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

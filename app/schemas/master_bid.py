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


class SelectMasterRequest(BaseModel):
    """Тело запроса выбора мастера (POST /projects/{id}/select-master)."""
    bid_id: int


class MasterBidResponse(BaseModel):
    id: int
    project_id: int

    # Данные мастера-автора отклика (фронт показывает их в карточке отклика).
    master_id: int
    master_name: Optional[str] = None
    specialty: Optional[str] = None
    rating: Optional[float] = None
    completed_jobs: Optional[int] = None

    price_offer: Optional[str] = None
    duration_offer: Optional[str] = None
    message: Optional[str] = None

    status: MasterBidStatus

    created_at: datetime
    updated_at: Optional[datetime] = None

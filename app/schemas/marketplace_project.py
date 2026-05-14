"""
Pydantic схемы для проектов маркетплейса.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.marketplace_project import MarketplaceProjectStatus


class MarketplaceProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    work_type: Optional[str] = Field(None, max_length=80)

    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    budget_label: Optional[str] = Field(None, max_length=80)

    district: Optional[str] = Field(None, max_length=120)
    address_short: Optional[str] = Field(None, max_length=160)

    full_spec: Optional[str] = None
    teaser: Optional[str] = Field(None, max_length=280)

    has_3d: bool = False


class MarketplaceProjectCreate(MarketplaceProjectBase):
    pass


class MarketplaceProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=160)
    work_type: Optional[str] = Field(None, max_length=80)

    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    budget_label: Optional[str] = Field(None, max_length=80)

    district: Optional[str] = Field(None, max_length=120)
    address_short: Optional[str] = Field(None, max_length=160)

    full_spec: Optional[str] = None
    teaser: Optional[str] = Field(None, max_length=280)

    has_3d: Optional[bool] = None


class MarketplaceProjectResponse(MarketplaceProjectBase):
    id: int
    customer_user_id: int

    status: MarketplaceProjectStatus

    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True

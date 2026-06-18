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


class MarketplaceProjectPublishRequest(BaseModel):
    """Тело запроса публикации (POST /projects/{id}/publish)."""
    district: Optional[str] = Field(None, max_length=120)
    address: Optional[str] = Field(None, max_length=160)


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

    # Реальное число откликов (сервер — единый источник правды, фронт не доверяет
    # захардкоженным числам). Проставляется сервисом.
    responses_count: int = 0

    selected_master_id: Optional[int] = None
    selected_master_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderFeedItemResponse(BaseModel):
    """Карточка заказа в ленте мастера (GET /orders).

    Поля совпадают с колонками проекта, поэтому читаются напрямую из ORM.
    `work_type` показывается мастеру как заголовок заказа.
    """
    id: int
    work_type: Optional[str] = None
    budget_label: Optional[str] = None
    district: Optional[str] = None
    address_short: Optional[str] = None
    teaser: Optional[str] = None
    has_3d: bool = False
    full_spec: Optional[str] = None

    class Config:
        from_attributes = True

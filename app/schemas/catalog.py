"""
Pydantic схемы для каталогов.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CatalogItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    region: Optional[str] = None
    price_range: Optional[str] = None
    extra_json: Optional[Dict[str, Any]] = None
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True

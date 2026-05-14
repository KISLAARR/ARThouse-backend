"""
Модель элементов каталогов.
"""
import enum

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class CatalogKind(str, enum.Enum):
    SERVICE_COMPANIES = "service_companies"
    FURNITURE_ITEMS = "furniture_items"
    MATERIAL_ITEMS = "material_items"
    RENTAL_ITEMS = "rental_items"


class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(Enum(CatalogKind), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    region = Column(String, nullable=True)
    price_range = Column(String, nullable=True)
    extra_json = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_catalog_items_kind_active", "kind", "is_active"),
    )

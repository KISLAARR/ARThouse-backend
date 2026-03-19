"""
Модель для сохранения состояния карты/схемы помещения.
"""
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApartmentSnapshot(Base):
    """Модель снимка состояния квартиры"""
    __tablename__ = "apartment_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id", ondelete="CASCADE"), nullable=False)
    
    snapshot_json = Column(JSON, nullable=False)  # Полное состояние карты
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    apartment = relationship("Apartment", back_populates="snapshots")
    
    # Индексы
    __table_args__ = (
        Index('idx_snapshots_apartment', 'apartment_id'),
    )
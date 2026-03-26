from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB  # ← импортируем JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApartmentSnapshot(Base):
    """Модель снимка состояния квартиры"""
    __tablename__ = "apartment_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id", ondelete="CASCADE"), nullable=False)
    
    # Используем JSONB вместо JSON
    snapshot_json = Column(JSONB, nullable=False)  # ← JSONB
    
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    apartment = relationship("Apartment", back_populates="snapshots")
    
    # Индекс для быстрого поиска внутри JSONB
    __table_args__ = (
        Index('idx_snapshots_apartment', 'apartment_id'),
        # GIN индекс для быстрого поиска внутри JSONB
        Index('idx_snapshot_json', 'snapshot_json', postgresql_using='gin'),
    )
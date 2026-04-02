"""
Модель комнаты/помещения внутри квартиры.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Room(Base):
    """Модель комнаты"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)  # "Кухня", "Спальня" и т.д.
    room_type = Column(String, nullable=True)  # kitchen, bedroom, bathroom, living и т.д.
    floor = Column(Integer, nullable=True)  # Этаж (если многоэтажная квартира)
    area = Column(Float, nullable=True)  # Площадь комнаты
    
    # Координаты на карте (для визуализации)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    apartment = relationship("Apartment", back_populates="rooms")
    tasks = relationship("Task", back_populates="room", cascade="all, delete-orphan")
    
    # Индексы
    __table_args__ = (
        Index('idx_rooms_apartment', 'apartment_id'),
    )

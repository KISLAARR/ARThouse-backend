"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """Модель пользователя в БД"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Тип пользователя: b2c (дом), b2b (офис), service (услуги)
    user_type = Column(String(20), default="b2c")
    
    # Статус
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Данные первичного опроса
    survey_completed = Column(Boolean, default=False)
    rooms_count = Column(Integer, nullable=True)
    floors_count = Column(Integer, nullable=True)
    wall_height = Column(Integer, nullable=True)  # в см
    total_area = Column(Integer, nullable=True)   # м²
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    apartments = relationship("Apartment", back_populates="owner")

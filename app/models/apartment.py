"""
Модель квартиры/помещения в базе данных.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Apartment(Base):
    """Модель квартиры/помещения"""
    __tablename__ = "apartments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    ceiling_height = Column(Float, nullable=True)
    square_meters = Column(Float, nullable=True)
    floors = Column(Integer, nullable=True)
    rooms_count = Column(Integer, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="apartments")
    surveys = relationship("Survey", back_populates="apartment", cascade="all, delete-orphan")
    rooms = relationship("Room", back_populates="apartment", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="apartment", cascade="all, delete-orphan")
    members = relationship("HouseholdMember", back_populates="apartment", cascade="all, delete-orphan")
    snapshots = relationship("ApartmentSnapshot", back_populates="apartment", cascade="all, delete-orphan")
"""
Модель помещения (квартира, офис и т.д.)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Apartment(Base):
    """Модель помещения"""
    __tablename__ = "apartments"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Основные данные
    name = Column(String(255), nullable=False, default="Мой дом")
    address = Column(String(500), nullable=True)
    apartment_type = Column(String(50), default="apartment")  # apartment, house, office, etc.
    
    # Размеры
    total_area = Column(Float, nullable=True)
    rooms_count = Column(Integer, nullable=True)
    floors_count = Column(Integer, default=1)
    wall_height = Column(Float, default=2.7)  # метры
    
    # Карта помещения (JSON с данными комнат)
    floor_plan = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    owner = relationship("User", back_populates="apartments")
    rooms = relationship("Room", back_populates="apartment", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="apartment", cascade="all, delete-orphan")


class Room(Base):
    """Модель комнаты"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    room_type = Column(String(50), nullable=False)  # living, bedroom, kitchen, bathroom, etc.
    floor = Column(Integer, default=1)
    area = Column(Float, nullable=True)
    
    # Позиция на карте
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    width = Column(Float, default=100)
    height = Column(Float, default=100)
    
    # Связи
    apartment = relationship("Apartment", back_populates="rooms")
    items = relationship("Item", back_populates="room", cascade="all, delete-orphan")


class Item(Base):
    """Модель предмета в комнате"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Позиция в комнате
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    
    # Метаданные
    tags = Column(JSON, nullable=True)  # Для поиска
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    room = relationship("Room", back_populates="items")


class Task(Base):
    """Модель задачи"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Статус и приоритет
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    priority = Column(Integer, default=1)  # 1-низкий, 2-средний, 3-высокий
    
    # Время
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Повторение
    is_recurring = Column(String(20), nullable=True)  # daily, weekly, monthly
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    apartment = relationship("Apartment", back_populates="tasks")

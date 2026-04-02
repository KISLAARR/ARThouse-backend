"""
Модель для хранения опросов о помещении.
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean, JSON, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Survey(Base):
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    apartment_id = Column(Integer, ForeignKey("apartments.id", ondelete="CASCADE"), nullable=True)
    
    floors = Column(Integer, nullable=True)
    rooms_count = Column(Integer, nullable=True)
    square_meters = Column(Float, nullable=True)
    ceiling_height = Column(Float, nullable=True)
    
    additional_info = Column(JSON, nullable=True)
    
    property_type = Column(String, nullable=True)

    total_area = Column(Float, nullable=True)
    total_area_unit = Column(String, nullable=True) 

    ceiling_height_unit = Column(String, nullable=True)

    floors_count = Column(Integer, nullable=True)

    rooms_details = Column(JSON, nullable=True)  

    residents = Column(JSON, nullable=True)

    activities = Column(JSON, nullable=True) 
    priorities = Column(JSON, nullable=True) 
    problem_areas = Column(JSON, nullable=True)  
    style_preferences = Column(JSON, nullable=True)  

    photos_paths = Column(JSON, nullable=True)
    floor_plan_path = Column(String, nullable=True)
    
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="surveys")
    apartment = relationship("Apartment", back_populates="surveys")

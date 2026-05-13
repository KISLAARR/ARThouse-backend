"""
Модель профиля мастера.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MasterProfile(Base):
    """Профиль мастера"""
    __tablename__ = "master_profiles"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    specialty = Column(String(120), nullable=True)
    about = Column(Text, nullable=True)
    status_label = Column(String(60), nullable=True)

    rating = Column(Numeric(3, 2), default=0.00, nullable=False)
    reviews_count = Column(Integer, default=0, nullable=False)
    completed_jobs = Column(Integer, default=0, nullable=False)

    city = Column(String, nullable=True)
    district = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="master_profile")

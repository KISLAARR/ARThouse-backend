"""
Модель члена семьи/участника квартиры.
"""
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class HouseholdMember(Base):
    """Модель члена семьи"""
    __tablename__ = "household_members"
    
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    apartment = relationship("Apartment", back_populates="members")
    user = relationship("User", back_populates="household_memberships")
    
    # Уникальность пары (квартира + пользователь)
    __table_args__ = (
        UniqueConstraint('apartment_id', 'user_id', name='unique_apartment_member'),
    )
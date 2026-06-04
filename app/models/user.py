"""
Модель пользователя в базе данных.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserType(str, enum.Enum):
    """Типы пользователей в системе"""
    B2C = "b2c"
    B2B = "b2b"
    SERVICE = "service"


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    CUSTOMER = "customer"
    MASTER = "master"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)

    user_type = Column(Enum(UserType), default=UserType.B2C, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    apartments = relationship("Apartment", back_populates="user", cascade="all, delete-orphan")
    surveys = relationship("Survey", back_populates="user", cascade="all, delete-orphan")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    household_memberships = relationship("HouseholdMember", back_populates="user")

    master_profile = relationship(
    "MasterProfile",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan"
    )   

    portfolio_photos = relationship(
        "MasterPortfolioPhoto",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    master_certificates = relationship(
        "MasterCertificate",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    master_reviews = relationship(
        "MasterReview",
        foreign_keys="MasterReview.master_user_id",
        back_populates="master",
        cascade="all, delete-orphan"
    )
    
    written_master_reviews = relationship(
        "MasterReview",
        foreign_keys="MasterReview.author_user_id",
        back_populates="author"
    )

    marketplace_projects = relationship(
        "MarketplaceProject",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    master_bids = relationship(
        "MasterBid",
        back_populates="master",
        cascade="all, delete-orphan"
    )

    customer_chat_threads = relationship(
        "DirectChatThread",
        foreign_keys="DirectChatThread.customer_user_id",
        back_populates="customer"
    )
    
    master_chat_threads = relationship(
        "DirectChatThread",
        foreign_keys="DirectChatThread.master_user_id",
        back_populates="master"
    )
    
    sent_direct_messages = relationship(
        "DirectChatMessage",
        back_populates="sender"
    )

    ai_foreman_threads = relationship(
    "AIForemanThread",
    back_populates="user",
    cascade="all, delete-orphan"
    )

    customer_contracts = relationship(
        "Contract",
        foreign_keys="Contract.customer_user_id",
        back_populates="customer"
    )
    
    master_contracts = relationship(
        "Contract",
        foreign_keys="Contract.master_user_id",
        back_populates="master"
    )

    user_map = relationship(
    "UserMap",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan"
    )

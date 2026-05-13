"""
Модель сделки / договора между заказчиком и мастером.
"""
import enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ContractStatus(str, enum.Enum):
    PENDING = "pending"
    SIGNED = "signed"
    CANCELLED = "cancelled"
    DONE = "done"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("marketplace_projects.id", ondelete="CASCADE"), nullable=False)
    customer_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    master_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    price = Column(String, nullable=True)
    duration = Column(String, nullable=True)

    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING, nullable=False)

    signed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("MarketplaceProject", back_populates="contracts")
    customer = relationship("User", foreign_keys=[customer_user_id], back_populates="customer_contracts")
    master = relationship("User", foreign_keys=[master_user_id], back_populates="master_contracts")

    __table_args__ = (
        Index("idx_contracts_project_id", "project_id"),
        Index("idx_contracts_customer_user_id", "customer_user_id"),
        Index("idx_contracts_master_user_id", "master_user_id"),
    )

"""
Модель откликов мастеров на проекты.
"""
import enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MasterBidStatus(str, enum.Enum):
    SENT = "sent"
    # SELECTED — отклик, который заказчик выбрал в сделке (POST select-master).
    # Фронт ждёт ровно строку "selected" (см. marketplace-backend-spec.md).
    SELECTED = "selected"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class MasterBid(Base):
    __tablename__ = "master_bids"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("marketplace_projects.id", ondelete="CASCADE"), nullable=False)
    master_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    price_offer = Column(String, nullable=True)
    duration_offer = Column(String, nullable=True)
    message = Column(Text, nullable=True)

    status = Column(Enum(MasterBidStatus), default=MasterBidStatus.SENT, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("MarketplaceProject", back_populates="bids")
    master = relationship("User", back_populates="master_bids")

    __table_args__ = (
        UniqueConstraint("project_id", "master_user_id", name="uq_master_bid_project_master"),
        Index("idx_master_bids_project_id", "project_id"),
        Index("idx_master_bids_master_user_id", "master_user_id"),
    )

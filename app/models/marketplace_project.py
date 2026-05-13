"""
Модель проектов маркетплейса.
"""
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MarketplaceProjectStatus(str, enum.Enum):
    """Статусы проекта на маркетплейсе"""
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_WORK = "in_work"
    CLOSED = "closed"
    ARCHIVED = "archived"


class MarketplaceProject(Base):
    """Проект заказчика / заказ в ленте мастера"""
    __tablename__ = "marketplace_projects"

    id = Column(Integer, primary_key=True, index=True)

    customer_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(160), nullable=False)
    work_type = Column(String(80), nullable=True)

    status = Column(
        Enum(MarketplaceProjectStatus),
        default=MarketplaceProjectStatus.DRAFT,
        nullable=False
    )

    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)
    budget_label = Column(String(80), nullable=True)

    district = Column(String(120), nullable=True)
    address_short = Column(String(160), nullable=True)

    full_spec = Column(Text, nullable=True)
    teaser = Column(String(280), nullable=True)

    has_3d = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship(
        "User",
        back_populates="marketplace_projects"
    )

    bids = relationship(
    "MasterBid",
    back_populates="project",
    cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "idx_marketplace_projects_status_created_at",
            "status",
            "created_at"
        ),
        Index(
            "idx_marketplace_projects_customer_status",
            "customer_user_id",
            "status"
        ),
    )

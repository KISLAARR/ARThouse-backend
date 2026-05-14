"""
Модель отзывов о мастерах.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MasterReview(Base):
    """Отзыв о мастере"""
    __tablename__ = "master_reviews"

    id = Column(Integer, primary_key=True, index=True)

    master_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    author_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    author_display_name = Column(String, nullable=True)

    rating = Column(Numeric(2, 1), nullable=False)
    text = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    master = relationship(
        "User",
        foreign_keys=[master_user_id],
        back_populates="master_reviews"
    )

    author = relationship(
        "User",
        foreign_keys=[author_user_id],
        back_populates="written_master_reviews"
    )

    __table_args__ = (
        Index("idx_master_reviews_master_user_id", "master_user_id"),
    )

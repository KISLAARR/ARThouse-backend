"""
Модель карты пользователя.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserMap(Base):
    __tablename__ = "user_maps"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    map_json = Column(JSONB, nullable=False)

    revision = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="user_map"
    )

    __table_args__ = (
        Index("idx_user_maps_user_id", "user_id"),
        Index("idx_user_maps_json", "map_json", postgresql_using="gin"),
    )
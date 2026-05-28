from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApartmentSnapshot(Base):
    """Модель снимка состояния карты квартиры / проекта"""
    __tablename__ = "apartment_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)

    # Старое поле: привязка к квартире
    apartment_id = Column(
        Integer,
        ForeignKey("apartments.id", ondelete="CASCADE"),
        nullable=True
    )

    # Новое поле: привязка к проекту маркетплейса
    project_id = Column(
        Integer,
        ForeignKey("marketplace_projects.id", ondelete="CASCADE"),
        nullable=True
    )

    # Кто сохранил состояние карты
    saved_by_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Роль редактора: customer / master / admin
    editor_role = Column(String(30), nullable=True)

    # JSONB: комнаты, стены, двери, окна, объекты, позиции предметов
    snapshot_json = Column(JSONB, nullable=False)
    
    # Версия карты внутри проекта / квартиры
    version = Column(Integer, default=1, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    apartment = relationship(
        "Apartment",
        back_populates="snapshots"
    )

    project = relationship(
        "MarketplaceProject",
        back_populates="snapshots"
    )

    saved_by = relationship("User")
    
    __table_args__ = (
        Index("idx_snapshots_apartment", "apartment_id"),
        Index("idx_snapshots_project", "project_id"),
        Index("idx_snapshots_project_version", "project_id", "version"),
        Index("idx_snapshot_json", "snapshot_json", postgresql_using="gin"),
    )
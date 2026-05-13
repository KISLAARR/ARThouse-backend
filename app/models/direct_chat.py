"""
Модели прямых чатов между заказчиком и мастером.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class DirectChatThread(Base):
    __tablename__ = "direct_chat_threads"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("marketplace_projects.id", ondelete="SET NULL"), nullable=True)
    customer_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    master_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    last_message_preview = Column(String(280), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("MarketplaceProject", back_populates="chat_threads")
    customer = relationship("User", foreign_keys=[customer_user_id], back_populates="customer_chat_threads")
    master = relationship("User", foreign_keys=[master_user_id], back_populates="master_chat_threads")

    messages = relationship(
        "DirectChatMessage",
        back_populates="thread",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "customer_user_id",
            "master_user_id",
            "project_id",
            name="uq_direct_chat_customer_master_project"
        ),
    )


class DirectChatMessage(Base):
    __tablename__ = "direct_chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    thread_id = Column(Integer, ForeignKey("direct_chat_threads.id", ondelete="CASCADE"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    body = Column(Text, nullable=False)
    attachments_json = Column(JSONB, nullable=True)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("DirectChatThread", back_populates="messages")
    sender = relationship("User", back_populates="sent_direct_messages")

    __table_args__ = (
        Index("idx_direct_chat_messages_thread_sent_at", "thread_id", "sent_at"),
    )

"""
Модели чата с ИИ-прорабом.
"""
import enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIForemanMessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class AIForemanThread(Base):
    __tablename__ = "ai_foreman_threads"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True)

    # Состояние диалога ИИ-прораба: {object_card, stage, history}.
    # Единый артефакт object_card отсюда идёт в карту, на биржу и в ТЗ мастеру.
    context_json = Column(JSONB, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="ai_foreman_threads")
    messages = relationship(
        "AIForemanMessage",
        back_populates="thread",
        cascade="all, delete-orphan"
    )


class AIForemanMessage(Base):
    __tablename__ = "ai_foreman_messages"

    id = Column(Integer, primary_key=True, index=True)

    thread_id = Column(Integer, ForeignKey("ai_foreman_threads.id", ondelete="CASCADE"), nullable=False)

    role = Column(Enum(AIForemanMessageRole), nullable=False)
    body = Column(Text, nullable=False)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("AIForemanThread", back_populates="messages")

    __table_args__ = (
        Index("idx_ai_foreman_messages_thread_sent_at", "thread_id", "sent_at"),
    )

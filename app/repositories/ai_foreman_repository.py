"""
Репозиторий для ИИ-прораба.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.ai_foreman import (
    AIForemanThread,
    AIForemanMessage,
    AIForemanMessageRole
)


class AIForemanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_threads(self, user_id: int) -> List[AIForemanThread]:
        return self.db.query(AIForemanThread).filter(
            AIForemanThread.user_id == user_id
        ).order_by(desc(AIForemanThread.updated_at)).all()

    def get_thread(self, thread_id: int) -> Optional[AIForemanThread]:
        return self.db.query(AIForemanThread).filter(
            AIForemanThread.id == thread_id
        ).first()

    def create_thread(self, user_id: int, title: Optional[str] = None) -> AIForemanThread:
        thread = AIForemanThread(
            user_id=user_id,
            title=title or "ИИ-прораб"
        )

        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)

        return thread

    def get_messages(self, thread_id: int) -> List[AIForemanMessage]:
        return self.db.query(AIForemanMessage).filter(
            AIForemanMessage.thread_id == thread_id
        ).order_by(AIForemanMessage.sent_at.asc()).all()

    def create_message(
        self,
        thread_id: int,
        role: AIForemanMessageRole,
        body: str
    ) -> AIForemanMessage:
        message = AIForemanMessage(
            thread_id=thread_id,
            role=role,
            body=body
        )

        self.db.add(message)

        thread = self.get_thread(thread_id)
        if thread:
            # updated_at обновится через onupdate при commit
            pass

        self.db.commit()
        self.db.refresh(message)

        return message

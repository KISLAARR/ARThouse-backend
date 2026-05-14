"""
Сервис ИИ-прораба.
"""
import os
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ai_foreman import AIForemanMessageRole
from app.repositories.ai_foreman_repository import AIForemanRepository
from app.schemas.ai_foreman import AIForemanThreadCreate, AIForemanMessageCreate


class AIProvider(ABC):
    @abstractmethod
    def generate_reply(self, user_message: str) -> str:
        pass


class StubAIProvider(AIProvider):
    def generate_reply(self, user_message: str) -> str:
        text = user_message.lower()

        if "ремонт" in text:
            return (
                "Я бы начал с описания объёма работ: помещение, площадь, "
                "тип ремонта, желаемые сроки и примерный бюджет."
            )

        if "бюджет" in text:
            return (
                "Для оценки бюджета лучше разделить расходы на материалы, "
                "работу мастера и резерв 10–15% на непредвиденные траты."
            )

        if "мастер" in text:
            return (
                "При выборе мастера смотрите рейтинг, отзывы, портфолио "
                "и уточняйте сроки, гарантию и финальную стоимость заранее."
            )

        return (
            "Я ИИ-прораб. Могу помочь сформулировать задачу для мастера, "
            "оценить этапы ремонта и подготовить описание проекта."
        )


class OpenAIAIProvider(AIProvider):
    def generate_reply(self, user_message: str) -> str:
        raise NotImplementedError(
            "OpenAI provider пока не подключён. Используйте AI_PROVIDER=stub."
        )


def get_ai_provider() -> AIProvider:
    provider = os.getenv("AI_PROVIDER", "stub")

    if provider == "stub":
        return StubAIProvider()

    if provider == "openai":
        return OpenAIAIProvider()

    return StubAIProvider()


class AIForemanService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AIForemanRepository(db)
        self.provider = get_ai_provider()

    def _check_thread_access(self, user_id: int, thread_id: int):
        thread = self.repo.get_thread(thread_id)

        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тред ИИ-прораба не найден"
            )

        if thread.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому треду"
            )

        return thread

    def get_threads(self, user_id: int):
        return self.repo.get_user_threads(user_id)

    def create_thread(self, user_id: int, data: AIForemanThreadCreate):
        return self.repo.create_thread(
            user_id=user_id,
            title=data.title
        )

    def get_messages(self, user_id: int, thread_id: int):
        self._check_thread_access(user_id, thread_id)
        return self.repo.get_messages(thread_id)

    def send_message(self, user_id: int, thread_id: int, data: AIForemanMessageCreate):
        self._check_thread_access(user_id, thread_id)

        user_message = self.repo.create_message(
            thread_id=thread_id,
            role=AIForemanMessageRole.USER,
            body=data.body
        )

        reply_text = self.provider.generate_reply(data.body)

        assistant_message = self.repo.create_message(
            thread_id=thread_id,
            role=AIForemanMessageRole.ASSISTANT,
            body=reply_text
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message
        }

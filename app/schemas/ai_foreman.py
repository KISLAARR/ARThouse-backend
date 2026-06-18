"""
Pydantic схемы для ИИ-прораба.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.ai_foreman import AIForemanMessageRole


class AIForemanThreadCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=160)


class AIForemanThreadResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class AIForemanMessageCreate(BaseModel):
    body: str = Field(..., min_length=1)
    # Фото помещения: data URL (data:image/...;base64,...) или https-ссылка.
    image: Optional[str] = None


class AIForemanMessageResponse(BaseModel):
    id: int
    thread_id: int
    role: AIForemanMessageRole
    body: str
    sent_at: datetime

    class Config:
        from_attributes = True


class AIForemanSendMessageResponse(BaseModel):
    user_message: AIForemanMessageResponse
    assistant_message: AIForemanMessageResponse

    # Контракт ИИ-прораба (бриф §5). object_card — единый артефакт
    # для карты, биржи и ТЗ мастеру.
    reply_text: str
    emotion: str = "обычный"
    stage: str = "goal"
    object_card: Dict[str, Any] = Field(default_factory=dict)
    estimate_ready: bool = False


class AIForemanChatRequest(BaseModel):
    """Запрос фронта на POST /ai-foreman/chat (один вызов = один ход диалога)."""
    message: str = Field("", description="Текст пользователя")
    thread_id: Optional[int] = None
    project_id: Optional[int] = None
    image: Optional[str] = None
    # Фронт может прислать своё состояние карточки/карты, опросов, комнат.
    object_card: Optional[Dict[str, Any]] = None
    current_map: Optional[Dict[str, Any]] = None
    premise_rooms: Optional[List[Dict[str, Any]]] = None
    survey: Optional[Dict[str, Any]] = None
    approved: bool = False


class AIForemanChatResponse(BaseModel):
    text: str
    reply_text: str
    emotion: str = "обычный"
    stage: str = "goal"
    object_card: Dict[str, Any] = Field(default_factory=dict)
    estimate_ready: bool = False
    thread_id: Optional[int] = None
    # Данные для редактора карты: комнаты с размерами из object_card.
    project_map_data: Optional[Dict[str, Any]] = None
    source: str = "ai_foreman"

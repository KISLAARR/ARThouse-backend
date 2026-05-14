"""
Эндпоинты ИИ-прораба.
"""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.schemas.ai_foreman import (
    AIForemanThreadCreate,
    AIForemanThreadResponse,
    AIForemanMessageCreate,
    AIForemanMessageResponse,
    AIForemanSendMessageResponse
)
from app.services.ai_foreman_service import AIForemanService

router = APIRouter()


@router.get(
    "/ai-foreman/threads",
    response_model=List[AIForemanThreadResponse]
)
async def get_ai_foreman_threads(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AIForemanService(db)
    return service.get_threads(current_user.id)


@router.post(
    "/ai-foreman/threads",
    response_model=AIForemanThreadResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_ai_foreman_thread(
    thread_data: AIForemanThreadCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AIForemanService(db)

    return service.create_thread(
        user_id=current_user.id,
        data=thread_data
    )


@router.get(
    "/ai-foreman/threads/{thread_id}/messages",
    response_model=List[AIForemanMessageResponse]
)
async def get_ai_foreman_messages(
    thread_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AIForemanService(db)

    return service.get_messages(
        user_id=current_user.id,
        thread_id=thread_id
    )


@router.post(
    "/ai-foreman/threads/{thread_id}/messages",
    response_model=AIForemanSendMessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def send_ai_foreman_message(
    thread_id: int,
    message_data: AIForemanMessageCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AIForemanService(db)

    return service.send_message(
        user_id=current_user.id,
        thread_id=thread_id,
        data=message_data
    )

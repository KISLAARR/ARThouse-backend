"""
Эндпоинты чатов.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.schemas.direct_chat import (
    DirectChatOpenCreate,
    DirectChatThreadResponse,
    DirectChatMessageCreate,
    DirectChatMessageResponse
)
from app.services.direct_chat_service import DirectChatService

router = APIRouter()


@router.get("/chats", response_model=List[DirectChatThreadResponse])
async def get_chats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DirectChatService(db)
    return service.get_my_threads(current_user.id)


@router.post(
    "/chats",
    response_model=DirectChatThreadResponse,
    status_code=status.HTTP_201_CREATED
)
async def open_chat(
    chat_data: DirectChatOpenCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DirectChatService(db)
    return service.open_thread(current_user.id, chat_data)


@router.get(
    "/chats/{thread_id}/messages",
    response_model=List[DirectChatMessageResponse]
)
async def get_chat_messages(
    thread_id: int,
    before: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DirectChatService(db)

    return service.get_messages(
        user_id=current_user.id,
        thread_id=thread_id,
        before=before,
        limit=limit
    )


@router.post(
    "/chats/{thread_id}/messages",
    response_model=DirectChatMessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def send_chat_message(
    thread_id: int,
    message_data: DirectChatMessageCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DirectChatService(db)

    return service.send_message(
        user_id=current_user.id,
        thread_id=thread_id,
        data=message_data
    )

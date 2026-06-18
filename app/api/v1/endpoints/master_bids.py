"""
Эндпоинты для откликов мастеров.
"""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.schemas.master_bid import (
    MasterBidCreate,
    MasterBidResponse,
    SelectMasterRequest
)
from app.schemas.direct_chat import DirectChatThreadResponse
from app.services.master_bid_service import MasterBidService

router = APIRouter()


@router.post(
    "/projects/{project_id}/bids",
    response_model=MasterBidResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_bid(
    project_id: int,
    bid_data: MasterBidCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterBidService(db)

    return service.create_bid(
        project_id=project_id,
        master_user_id=current_user.id,
        data=bid_data
    )


@router.get(
    "/projects/{project_id}/bids",
    response_model=List[MasterBidResponse]
)
async def get_project_bids(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterBidService(db)

    return service.get_project_bids(
        project_id=project_id,
        customer_user_id=current_user.id
    )


@router.get("/bids/my", response_model=List[MasterBidResponse])
async def get_my_bids(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterBidService(db)

    return service.get_my_bids(
        master_user_id=current_user.id
    )


@router.post(
    "/projects/{project_id}/select-master",
    response_model=DirectChatThreadResponse
)
async def select_master(
    project_id: int,
    payload: SelectMasterRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """⭐ Заказчик выбирает мастера. Возвращает чат с выбранным мастером."""
    service = MasterBidService(db)

    return service.select_master(
        customer_user_id=current_user.id,
        project_id=project_id,
        bid_id=payload.bid_id
    )


@router.post("/bids/{bid_id}/accept", response_model=MasterBidResponse)
async def accept_bid(
    bid_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterBidService(db)

    return service.accept_bid(
        bid_id=bid_id,
        customer_user_id=current_user.id
    )


@router.post("/bids/{bid_id}/decline", response_model=MasterBidResponse)
async def decline_bid(
    bid_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterBidService(db)

    return service.decline_bid(
        bid_id=bid_id,
        customer_user_id=current_user.id
    )


@router.post("/bids/{bid_id}/withdraw", response_model=MasterBidResponse)
async def withdraw_bid(
    bid_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterBidService(db)

    return service.withdraw_bid(
        bid_id=bid_id,
        master_user_id=current_user.id
    )

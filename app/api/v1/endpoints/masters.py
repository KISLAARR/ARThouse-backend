"""
Эндпоинты мастеров.
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.services.master_service import MasterService

from app.schemas.master import (
    MasterListItem,
    MasterPublicProfile,
    MasterProfileUpdate,
    MasterProfileResponse,

    PortfolioPhotoCreate,
    PortfolioPhotoResponse,

    CertificateCreate,
    CertificateResponse,

    ReviewCreate,
    ReviewResponse
)

router = APIRouter()


@router.get("/masters", response_model=List[MasterListItem])
async def list_masters(
    city: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    q: Optional[str] = Query(None),

    sort: str = Query("rating"),

    limit: int = Query(20),
    offset: int = Query(0),

    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.list_masters(
        city=city,
        specialty=specialty,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset
    )


@router.get("/masters/{user_id}", response_model=MasterPublicProfile)
async def get_master_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.get_public_profile(user_id)


@router.put("/masters/me", response_model=MasterProfileResponse)
async def update_my_profile(
    profile_data: MasterProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.update_my_profile(
        current_user.id,
        profile_data
    )


@router.get("/masters/me/portfolio", response_model=List[PortfolioPhotoResponse])
async def get_my_portfolio(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.get_my_portfolio(current_user.id)


@router.post(
    "/masters/me/portfolio",
    response_model=PortfolioPhotoResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_portfolio_photo(
    photo_data: PortfolioPhotoCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.add_portfolio_photo(
        current_user.id,
        photo_data
    )


@router.delete("/masters/me/portfolio/{photo_id}")
async def delete_portfolio_photo(
    photo_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    service.delete_portfolio_photo(
        current_user.id,
        photo_id
    )

    return {"success": True}


@router.get("/masters/me/certificates", response_model=List[CertificateResponse])
async def get_my_certificates(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.get_my_certificates(current_user.id)


@router.post(
    "/masters/me/certificates",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_certificate(
    certificate_data: CertificateCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.add_certificate(
        current_user.id,
        certificate_data
    )


@router.delete("/masters/me/certificates/{certificate_id}")
async def delete_certificate(
    certificate_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    service.delete_certificate(
        current_user.id,
        certificate_id
    )

    return {"success": True}


@router.get("/masters/{user_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    user_id: int,
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.get_reviews(user_id)


@router.post(
    "/masters/{user_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_review(
    user_id: int,
    review_data: ReviewCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MasterService(db)

    return service.add_review(
        master_user_id=user_id,
        author_user_id=current_user.id,
        data=review_data
    )

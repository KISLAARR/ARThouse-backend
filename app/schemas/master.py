"""
Pydantic схемы для мастеров.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class MasterProfileUpdate(BaseModel):
    specialty: Optional[str] = Field(None, max_length=120)
    about: Optional[str] = None
    status_label: Optional[str] = Field(None, max_length=60)
    city: Optional[str] = Field(None, max_length=120)
    district: Optional[str] = Field(None, max_length=120)


class MasterProfileResponse(BaseModel):
    user_id: int

    specialty: Optional[str] = None
    about: Optional[str] = None
    status_label: Optional[str] = None

    rating: Decimal
    reviews_count: int
    completed_jobs: int

    city: Optional[str] = None
    district: Optional[str] = None

    class Config:
        from_attributes = True


class MasterListItem(BaseModel):
    user_id: int

    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    specialty: Optional[str] = None
    about: Optional[str] = None
    status_label: Optional[str] = None

    rating: Decimal
    reviews_count: int
    completed_jobs: int

    city: Optional[str] = None
    district: Optional[str] = None


class PortfolioPhotoCreate(BaseModel):
    file_url: str
    sort_order: int = 0


class PortfolioPhotoResponse(BaseModel):
    id: int
    user_id: int

    file_url: str
    sort_order: int

    created_at: datetime

    class Config:
        from_attributes = True


class CertificateCreate(BaseModel):
    title: str
    file_url: str


class CertificateResponse(BaseModel):
    id: int
    user_id: int

    title: str
    file_url: str

    created_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0)
    text: Optional[str] = None
    author_display_name: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int

    master_user_id: int
    author_user_id: Optional[int] = None

    author_display_name: Optional[str] = None

    rating: float
    text: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class MasterPublicProfile(BaseModel):
    profile: MasterProfileResponse
    portfolio: List[PortfolioPhotoResponse]
    certificates: List[CertificateResponse]
    reviews: List[ReviewResponse]

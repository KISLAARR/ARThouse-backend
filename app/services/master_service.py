"""
Сервис для мастеров.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.models.master_portfolio_photo import MasterPortfolioPhoto
from app.models.master_certificate import MasterCertificate
from app.models.master_review import MasterReview

from app.repositories.master_repository import MasterRepository
from app.repositories.user_repository import UserRepository

from app.schemas.master import (
    MasterProfileUpdate,
    PortfolioPhotoCreate,
    CertificateCreate,
    ReviewCreate
)


class MasterService:

    def __init__(self, db: Session):
        self.db = db
        self.master_repo = MasterRepository(db)
        self.user_repo = UserRepository(db)

    def _check_master(self, user_id: int):
        user = self.user_repo.get(user_id)

        if not user or user.role != UserRole.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не является мастером"
            )

        return user

    def list_masters(
        self,
        city=None,
        specialty=None,
        q=None,
        sort="rating",
        limit=20,
        offset=0
    ):
        rows = self.master_repo.list_masters(
            city=city,
            specialty=specialty,
            q=q,
            sort=sort,
            limit=limit,
            offset=offset
        )

        result = []

        for user, profile in rows:
            result.append({
                "user_id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,

                "specialty": profile.specialty,
                "about": profile.about,
                "status_label": profile.status_label,

                "rating": profile.rating,
                "reviews_count": profile.reviews_count,
                "completed_jobs": profile.completed_jobs,

                "city": profile.city,
                "district": profile.district
            })

        return result

    def get_public_profile(self, user_id: int):
        profile = self.master_repo.get_profile(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль мастера не найден"
            )

        return {
            "profile": profile,
            "portfolio": self.master_repo.get_portfolio(user_id),
            "certificates": self.master_repo.get_certificates(user_id),
            "reviews": self.master_repo.get_reviews(user_id)
        }

    def update_my_profile(self, user_id: int, data: MasterProfileUpdate):
        self._check_master(user_id)

        profile = self.master_repo.get_profile(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль мастера не найден"
            )

        update_data = data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(profile, key, value)

        self.db.commit()
        self.db.refresh(profile)

        return profile

    def get_my_portfolio(self, user_id: int):
        self._check_master(user_id)

        return self.master_repo.get_portfolio(user_id)

    def add_portfolio_photo(self, user_id: int, data: PortfolioPhotoCreate):
        self._check_master(user_id)

        photo = MasterPortfolioPhoto(
            user_id=user_id,
            file_url=data.file_url,
            sort_order=data.sort_order
        )

        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)

        return photo

    def delete_portfolio_photo(self, user_id: int, photo_id: int):
        self._check_master(user_id)

        photo = self.db.query(MasterPortfolioPhoto).filter(
            MasterPortfolioPhoto.id == photo_id,
            MasterPortfolioPhoto.user_id == user_id
        ).first()

        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Фото не найдено"
            )

        self.db.delete(photo)
        self.db.commit()

        return True

    def get_my_certificates(self, user_id: int):
        self._check_master(user_id)

        return self.master_repo.get_certificates(user_id)

    def add_certificate(self, user_id: int, data: CertificateCreate):
        self._check_master(user_id)

        certificate = MasterCertificate(
            user_id=user_id,
            title=data.title,
            file_url=data.file_url
        )

        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)

        return certificate

    def delete_certificate(self, user_id: int, certificate_id: int):
        self._check_master(user_id)

        certificate = self.db.query(MasterCertificate).filter(
            MasterCertificate.id == certificate_id,
            MasterCertificate.user_id == user_id
        ).first()

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сертификат не найден"
            )

        self.db.delete(certificate)
        self.db.commit()

        return True

    def get_reviews(self, user_id: int):
        return self.master_repo.get_reviews(user_id)

    def add_review(self, master_user_id: int, author_user_id: int, data: ReviewCreate):
        review = MasterReview(
            master_user_id=master_user_id,
            author_user_id=author_user_id,
            author_display_name=data.author_display_name,
            rating=data.rating,
            text=data.text
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return review

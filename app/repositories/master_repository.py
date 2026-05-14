"""
Репозиторий для мастеров.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.models.user import User, UserRole
from app.models.master_profile import MasterProfile
from app.models.master_portfolio_photo import MasterPortfolioPhoto
from app.models.master_certificate import MasterCertificate
from app.models.master_review import MasterReview


class MasterRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_masters(
        self,
        city: Optional[str] = None,
        specialty: Optional[str] = None,
        q: Optional[str] = None,
        sort: str = "rating",
        limit: int = 20,
        offset: int = 0
    ):
        query = (
            self.db.query(User, MasterProfile)
            .join(MasterProfile, MasterProfile.user_id == User.id)
            .filter(User.role == UserRole.MASTER)
        )

        if city:
            query = query.filter(MasterProfile.city.ilike(f"%{city}%"))

        if specialty:
            query = query.filter(
                MasterProfile.specialty.ilike(f"%{specialty}%")
            )

        if q:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{q}%"),
                    User.display_name.ilike(f"%{q}%"),
                    MasterProfile.specialty.ilike(f"%{q}%"),
                    MasterProfile.about.ilike(f"%{q}%")
                )
            )

        if sort == "rating":
            query = query.order_by(desc(MasterProfile.rating))
        else:
            query = query.order_by(desc(MasterProfile.created_at))

        return query.offset(offset).limit(limit).all()

    def get_profile(self, user_id: int):
        return self.db.query(MasterProfile).filter(
            MasterProfile.user_id == user_id
        ).first()

    def get_portfolio(self, user_id: int):
        return self.db.query(MasterPortfolioPhoto).filter(
            MasterPortfolioPhoto.user_id == user_id
        ).order_by(MasterPortfolioPhoto.sort_order.asc()).all()

    def get_certificates(self, user_id: int):
        return self.db.query(MasterCertificate).filter(
            MasterCertificate.user_id == user_id
        ).all()

    def get_reviews(self, user_id: int):
        return self.db.query(MasterReview).filter(
            MasterReview.master_user_id == user_id
        ).order_by(desc(MasterReview.created_at)).all()

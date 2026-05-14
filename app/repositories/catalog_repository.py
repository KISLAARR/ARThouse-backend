"""
Репозиторий для каталогов.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.catalog_item import CatalogItem, CatalogKind


class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_items(
        self,
        kind: CatalogKind,
        region: Optional[str] = None,
        price_range: Optional[str] = None,
        q: Optional[str] = None
    ):
        query = self.db.query(CatalogItem).filter(
            CatalogItem.kind == kind,
            CatalogItem.is_active == True
        )

        if region:
            query = query.filter(CatalogItem.region.ilike(f"%{region}%"))

        if price_range:
            query = query.filter(CatalogItem.price_range == price_range)

        if q:
            query = query.filter(
                or_(
                    CatalogItem.title.ilike(f"%{q}%"),
                    CatalogItem.description.ilike(f"%{q}%")
                )
            )

        return query.order_by(
            CatalogItem.sort_order.asc(),
            CatalogItem.id.asc()
        ).all()

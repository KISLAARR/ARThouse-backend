"""
Сервис для каталогов.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.catalog_item import CatalogKind
from app.repositories.catalog_repository import CatalogRepository


class CatalogService:
    def __init__(self, db: Session):
        self.db = db
        self.catalog_repo = CatalogRepository(db)

    def _map_kind(self, kind: str) -> CatalogKind:
        mapping = {
            "services": CatalogKind.SERVICE_COMPANIES,
            "furniture": CatalogKind.FURNITURE_ITEMS,
            "materials": CatalogKind.MATERIAL_ITEMS,
            "rentals": CatalogKind.RENTAL_ITEMS,
        }

        if kind not in mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Каталог не найден"
            )

        return mapping[kind]

    def get_catalog(
        self,
        kind: str,
        region=None,
        price_range=None,
        q=None
    ):
        catalog_kind = self._map_kind(kind)

        return self.catalog_repo.list_items(
            kind=catalog_kind,
            region=region,
            price_range=price_range,
            q=q
        )

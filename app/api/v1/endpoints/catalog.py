"""
Эндпоинты каталогов.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.catalog import CatalogItemResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/catalog/services", response_model=List[CatalogItemResponse])
async def get_services_catalog(
    region: Optional[str] = Query(None),
    price_range: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = CatalogService(db)
    return service.get_catalog("services", region, price_range, q)


@router.get("/catalog/furniture", response_model=List[CatalogItemResponse])
async def get_furniture_catalog(
    region: Optional[str] = Query(None),
    price_range: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = CatalogService(db)
    return service.get_catalog("furniture", region, price_range, q)


@router.get("/catalog/materials", response_model=List[CatalogItemResponse])
async def get_materials_catalog(
    region: Optional[str] = Query(None),
    price_range: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = CatalogService(db)
    return service.get_catalog("materials", region, price_range, q)


@router.get("/catalog/rentals", response_model=List[CatalogItemResponse])
async def get_rentals_catalog(
    region: Optional[str] = Query(None),
    price_range: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = CatalogService(db)
    return service.get_catalog("rentals", region, price_range, q)

"""
Kosts router - API endpoints.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.kosts.model import Kost
from app.features.kosts.schemas import (
    KostCreate,
    KostUpdate,
    KostResponse,
    KostListResponse,
)
from app.features.kosts.service import KostsService

router = APIRouter()


from app.features.common.dependencies import get_current_user_region


def _enforce_region_scope(kost_id: UUID, region_id: Optional[UUID], db: Session) -> None:
    if not region_id:
        return
    kost = db.query(Kost).filter(Kost.id == kost_id).first()
    if not kost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kost not found")
    if kost.region_id != region_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this kost")


@router.get("", response_model=KostListResponse)
async def get_kosts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Get paginated list of kosts, filtered by user's region."""
    service = KostsService(db)
    items, total = service.get_all(page=page, page_size=page_size, region_id=region_id)
    return KostListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{kost_id}", response_model=KostResponse)
async def get_kost(
    kost_id: UUID,
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Get a single kost by ID."""
    _enforce_region_scope(kost_id, region_id, db)
    service = KostsService(db)
    return service.get_by_id(kost_id)


@router.post("", response_model=KostResponse, status_code=status.HTTP_201_CREATED)
async def create_kost(
    data: KostCreate,
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Create a new kost."""
    if region_id:
        data = KostCreate(**{**data.model_dump(), "region_id": region_id})
    service = KostsService(db)
    return service.create(data)


@router.put("/{kost_id}", response_model=KostResponse)
async def update_kost(
    kost_id: UUID,
    data: KostUpdate,
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Update an existing kost."""
    _enforce_region_scope(kost_id, region_id, db)
    service = KostsService(db)
    return service.update(kost_id, data)


@router.delete("/{kost_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kost(
    kost_id: UUID,
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Delete a kost."""
    _enforce_region_scope(kost_id, region_id, db)
    service = KostsService(db)
    service.delete(kost_id)

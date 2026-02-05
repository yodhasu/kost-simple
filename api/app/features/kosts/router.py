"""
Kosts router - API endpoints.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_firebase_uid
from app.features.users.service import UserProfileService
from app.features.kosts.schemas import (
    KostCreate,
    KostUpdate,
    KostResponse,
    KostListResponse,
)
from app.features.kosts.service import KostsService

router = APIRouter()


async def get_current_user_region(
    firebase_uid: str = Depends(get_current_firebase_uid),
    db: Session = Depends(get_db),
) -> Optional[UUID]:
    """Helper dependency to get current user's region ID."""
    user_service = UserProfileService(db)
    profile = user_service.get_by_firebase_uid(firebase_uid)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found."
        )
    
    return profile.region_id


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
async def get_kost(kost_id: UUID, db: Session = Depends(get_db)):
    """Get a single kost by ID."""
    service = KostsService(db)
    return service.get_by_id(kost_id)


@router.post("", response_model=KostResponse, status_code=status.HTTP_201_CREATED)
async def create_kost(data: KostCreate, db: Session = Depends(get_db)):
    """Create a new kost."""
    service = KostsService(db)
    return service.create(data)


@router.put("/{kost_id}", response_model=KostResponse)
async def update_kost(kost_id: UUID, data: KostUpdate, db: Session = Depends(get_db)):
    """Update an existing kost."""
    service = KostsService(db)
    return service.update(kost_id, data)


@router.delete("/{kost_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kost(kost_id: UUID, db: Session = Depends(get_db)):
    """Delete a kost."""
    service = KostsService(db)
    service.delete(kost_id)

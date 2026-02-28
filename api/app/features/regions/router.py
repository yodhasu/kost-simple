"""
Regions router - API endpoints.
"""

from fastapi import APIRouter, status, Depends
from uuid import UUID

from app.features.regions.schemas import (
    RegionsResponse, RegionsListResponse, RegionsCreate, RegionsUpdate,
)
from app.features.regions.service import RegionsService
from app.db.session import get_db
from app.core.auth import get_current_firebase_uid
from app.features.users.service import UserProfileService
from sqlalchemy.orm import Session

router = APIRouter()

async def get_current_user_profile(db: Session = Depends(get_db), firebase_uid: str = Depends(get_current_firebase_uid)):
    user_service = UserProfileService(db)
    profile = user_service.get_by_firebase_uid(firebase_uid)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found."
        )
    return profile

@router.get("", response_model=RegionsListResponse)
async def get_regions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_profile),
):
    """Get list of regions."""
    service = RegionsService(db)
    items = service.get_all()
    return RegionsListResponse(items=items)

@router.post("", response_model=RegionsResponse, status_code=status.HTTP_201_CREATED)
async def create_region(data: RegionsCreate, db: Session = Depends(get_db)):
    """Create a new regions."""
    service = RegionsService(db)
    return service.create(data)

@router.put("/{item_id}", response_model=RegionsResponse)
async def update_region(item_id: UUID, data: RegionsUpdate, db: Session = Depends(get_db)):
    """Update an existing regions."""
    service = RegionsService(db)
    return service.update(item_id, data)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_region(item_id: UUID, db: Session = Depends(get_db)):
    """Delete a regions."""
    service = RegionsService(db)
    service.delete(item_id)


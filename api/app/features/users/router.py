"""
User Profile router - API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_firebase_uid
from app.features.users.schemas import (
    UserProfileMe,
    AdminAccountListResponse,
    AdminAccountCreate,
    AdminAccountItem,
    PasswordResetResponse,
    AdminAccountRegionUpdate,
)
from app.features.users.service import UserProfileService
from app.features.users.user_region_model import UserRegion

router = APIRouter()


@router.get("/me", response_model=UserProfileMe)
async def get_current_user(
    firebase_uid: str = Depends(get_current_firebase_uid),
    db: Session = Depends(get_db),
):
    """Get current user profile based on Firebase token."""
    service = UserProfileService(db)
    profile = service.get_by_firebase_uid(firebase_uid)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found. Please contact administrator."
        )
    
    # Get region IDs from user_regions junction table
    user_regions = db.query(UserRegion.region_id).filter(
        UserRegion.user_id == profile.id
    ).all()
    region_ids = [r.region_id for r in user_regions]
    
    return UserProfileMe(
        id=profile.id,
        firebase_uid=profile.firebase_uid,
        name=profile.name,
        role=profile.role,
        region_ids=region_ids,
    )


def require_owner(
    firebase_uid: str = Depends(get_current_firebase_uid),
    db: Session = Depends(get_db),
):
    service = UserProfileService(db)
    profile = service.get_by_firebase_uid(firebase_uid)
    if not profile or profile.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can manage admin accounts",
        )
    return profile


@router.get("/admins", response_model=AdminAccountListResponse)
async def list_admin_accounts(
    _: dict = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = UserProfileService(db)
    items = service.list_admin_accounts()
    return AdminAccountListResponse(items=items, total=len(items))


@router.post("/admins", response_model=AdminAccountItem, status_code=status.HTTP_201_CREATED)
async def create_admin_account(
    data: AdminAccountCreate,
    _: dict = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = UserProfileService(db)
    return service.create_admin_account(data)


@router.post("/admins/{user_id}/reset-password", response_model=PasswordResetResponse)
async def reset_admin_password(
    user_id: UUID,
    _: dict = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = UserProfileService(db)
    reset_link = service.generate_admin_password_reset(user_id)
    return PasswordResetResponse(reset_link=reset_link)


@router.put("/admins/{user_id}/regions", response_model=AdminAccountItem)
async def update_admin_regions(
    user_id: UUID,
    data: AdminAccountRegionUpdate,
    _: dict = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = UserProfileService(db)
    return service.update_admin_regions(user_id, data.region_ids)


@router.delete("/admins/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_account(
    user_id: UUID,
    _: dict = Depends(require_owner),
    db: Session = Depends(get_db),
):
    service = UserProfileService(db)
    service.delete_admin_account(user_id)

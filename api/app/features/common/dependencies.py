"""
Common dependencies for features.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_firebase_uid
from app.features.users.service import UserProfileService
from app.features.users.user_region_model import UserRegion


async def get_current_user_region(
    region_id: Optional[UUID] = Query(None, description="Region ID (only for owners)"),
    firebase_uid: str = Depends(get_current_firebase_uid),
    db: Session = Depends(get_db),
) -> Optional[UUID]:
    """
    Get current user's region ID.
    
    Logic:
    - If user is OWNER: 
        - If query param region_id is provided, use it.
        - If not provided, return None (implies all regions or no filter).
    - If user is NOT OWNER:
        - If query param region_id is provided and assigned to the user, use it.
        - Otherwise, fall back to the first assigned region_id.
    """
    user_service = UserProfileService(db)
    profile = user_service.get_by_firebase_uid(firebase_uid)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found."
        )
    
    if profile.role == "owner":
        # Owner can override region via query param
        return region_id

    assigned_regions = db.query(UserRegion.region_id).filter(
        UserRegion.user_id == profile.id
    ).all()
    assigned_ids = [r.region_id for r in assigned_regions]
    if not assigned_ids:
        return None
    if region_id and region_id in assigned_ids:
        return region_id
    return assigned_ids[0]

"""
User Profile router - API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_firebase_uid
from app.features.users.schemas import UserProfileMe
from app.features.users.service import UserProfileService

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
    
    return profile

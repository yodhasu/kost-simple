"""
User Profile service - Business logic with database operations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.features.users.model import UserProfile


class UserProfileService:
    """Service class for user profile operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[UserProfile]:
        """Get user profile by Firebase UID."""
        return self.db.query(UserProfile).filter(
            UserProfile.firebase_uid == firebase_uid
        ).first()

    def get_by_firebase_uid_or_404(self, firebase_uid: str) -> UserProfile:
        """Get user profile by Firebase UID or raise 404."""
        profile = self.get_by_firebase_uid(firebase_uid)
        if not profile:
            raise NotFoundException(f"User profile not found for firebase_uid: {firebase_uid}")
        return profile

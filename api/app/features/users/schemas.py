"""
User Profile schemas (Pydantic models).
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: UUID
    firebase_uid: str
    name: str
    role: str
    region_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileMe(BaseModel):
    """Schema for current user profile (returned on /me endpoint)."""
    id: UUID
    firebase_uid: str
    name: str
    role: str
    region_id: Optional[UUID] = None

    class Config:
        from_attributes = True

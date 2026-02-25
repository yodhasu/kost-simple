"""
User Profile schemas (Pydantic models).
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: UUID
    firebase_uid: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileMe(BaseModel):
    """Schema for current user profile (returned on /me endpoint)."""
    id: UUID
    firebase_uid: str
    name: str
    role: str
    region_ids: List[UUID] = []

    class Config:
        from_attributes = True


class AdminAccountItem(BaseModel):
    id: UUID
    firebase_uid: str
    name: str
    email: Optional[str] = None
    role: str
    region_ids: List[UUID] = []
    region_names: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class AdminAccountListResponse(BaseModel):
    items: List[AdminAccountItem]
    total: int


class AdminAccountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    region_ids: List[UUID] = Field(..., min_length=1)
    role: str = "admin"


class PasswordResetResponse(BaseModel):
    reset_link: str


class AdminAccountRegionUpdate(BaseModel):
    region_ids: List[UUID] = Field(..., min_length=1)

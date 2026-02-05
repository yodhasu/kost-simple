"""
Kosts schemas (Pydantic models).
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KostBase(BaseModel):
    """Base kost schema."""
    name: str
    address: Optional[str] = None
    total_units: int = Field(ge=1, default=1)
    notes: Optional[str] = None


class KostCreate(KostBase):
    """Schema for creating a new kost."""
    region_id: UUID


class KostUpdate(BaseModel):
    """Schema for updating a kost."""
    name: Optional[str] = None
    address: Optional[str] = None
    total_units: Optional[int] = None
    notes: Optional[str] = None
    region_id: Optional[UUID] = None


class KostResponse(KostBase):
    """Schema for kost response."""
    id: UUID
    region_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class KostListResponse(BaseModel):
    """Schema for paginated kost list."""
    items: list[KostResponse]
    total: int
    page: int
    page_size: int

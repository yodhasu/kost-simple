"""
Regions schemas (Pydantic models).
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class RegionsBase(BaseModel):
    """Base regions schema."""
    name: str
    


class RegionsCreate(RegionsBase):
    """Schema for creating a new regions."""
    pass


class RegionsUpdate(BaseModel):
    """Schema for updating a regions."""
    name: str
    pass


class RegionsResponse(RegionsBase):
    """Schema for regions response."""
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class RegionsListResponse(BaseModel):
    """Schema for paginated regions list."""
    items: list[RegionsResponse]
    total: int
    page: int
    page_size: int

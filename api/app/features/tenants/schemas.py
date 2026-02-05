"""
Tenants schemas (Pydantic models).
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class TenantStatus(str, Enum):
    """Tenant status enum."""
    ACTIVE = "aktif"
    DP = "dp"


class TenantBase(BaseModel):
    """Base tenant schema."""
    name: str
    phone: Optional[str] = None
    start_date: Optional[date] = None
    rent_price: Optional[Decimal] = Field(None, ge=0)
    status: TenantStatus = TenantStatus.ACTIVE


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""
    kost_id: UUID


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""
    name: Optional[str] = None
    phone: Optional[str] = None
    start_date: Optional[date] = None
    rent_price: Optional[Decimal] = None
    status: Optional[TenantStatus] = None


class TenantResponse(TenantBase):
    """Schema for tenant response."""
    id: UUID
    kost_id: UUID
    end_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Schema for paginated tenant list."""
    items: list[TenantResponse]
    total: int
    page: int
    page_size: int

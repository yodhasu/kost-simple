"""
Tenants schemas (Pydantic models).
"""

from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum
import re

from pydantic import BaseModel, Field, field_validator

from app.features.transactions.schemas import TransactionResponse


class TenantStatus(str, Enum):
    """Tenant status enum."""
    ACTIVE = "aktif"
    DP = "dp"
    INACTIVE = "inaktif"
    MOVE = "pindah"
    LATE = "telat"
    RENOVATION = "renovasi"


class TenantBase(BaseModel):
    """Base tenant schema."""
    name: str
    phone: Optional[str] = None
    start_date: Optional[date] = None
    rent_price: Optional[int] = Field(None, ge=0)
    trash_fee: Optional[int] = Field(None, ge=0)
    security_fee: Optional[int] = Field(None, ge=0)
    admin_fee: Optional[int] = Field(None, ge=0)
    dp_amount: Optional[int] = Field(None, ge=0)
    dp_due_date: Optional[date] = None
    status: TenantStatus = TenantStatus.ACTIVE

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if v == "":
            return None

        # Allow common phone formatting characters, but reject letters/symbols.
        if not re.match(r"^\+?[\d\s().-]+$", v):
            raise ValueError("Invalid phone number format")

        digits = re.sub(r"\D", "", v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Invalid phone number length")

        return v


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""
    kost_id: UUID


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""
    name: Optional[str] = None
    phone: Optional[str] = None
    start_date: Optional[date] = None
    rent_price: Optional[int] = None
    trash_fee: Optional[int] = None
    security_fee: Optional[int] = None
    admin_fee: Optional[int] = None
    dp_amount: Optional[int] = Field(None, ge=0)
    dp_due_date: Optional[date] = None
    status: Optional[TenantStatus] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        # Same validation as TenantBase, but only runs when phone is provided.
        if v is None:
            return None
        v = v.strip()
        if v == "":
            return None

        if not re.match(r"^\+?[\d\s().-]+$", v):
            raise ValueError("Invalid phone number format")

        digits = re.sub(r"\D", "", v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Invalid phone number length")

        return v


class TenantResponse(TenantBase):
    """Schema for tenant response."""
    id: UUID
    kost_id: UUID
    end_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True



class TenantDetailResponse(TenantResponse):
    """Schema for detailed tenant response with relationships."""
    transactions: List[TransactionResponse] = []


class TenantListResponse(BaseModel):
    """Schema for tenant list response."""
    items: List[TenantResponse]
    total: int
    page: int
    page_size: int


"""
Transactions schemas (Pydantic models).
"""

from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    """Base transaction schema."""
    type: str
    category: Optional[str] = None
    amount: Decimal = Field(..., ge=0)
    transaction_date: date
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: UUID
    kost_id: UUID
    tenant_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

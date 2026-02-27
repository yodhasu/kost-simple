"""
Transactions schemas (Pydantic models).
"""

from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    """Base transaction schema."""
    type: Literal["income", "expense"]
    category: Optional[str] = None
    amount: int = Field(..., ge=0)
    transaction_date: date
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: UUID
    kost_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    region_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

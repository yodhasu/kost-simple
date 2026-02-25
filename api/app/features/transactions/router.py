"""
Transactions router - API endpoints.
"""

from uuid import UUID
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.features.transactions.model import Transaction
from app.features.transactions.schemas import TransactionResponse
from app.features.tenants.model import Tenant
from app.features.kosts.model import Kost

router = APIRouter()


class PaymentCreate(BaseModel):
    """Schema for creating a rent payment."""
    kost_id: UUID
    tenant_id: UUID
    amount: int = Field(..., ge=0)
    transaction_date: date


class ExpenseCreate(BaseModel):
    """Schema for creating an expense."""
    kost_id: Optional[UUID] = None
    region_id: Optional[UUID] = None
    category: str
    amount: int = Field(..., ge=0)
    transaction_date: date
    description: Optional[str] = None


@router.post("/payments", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    """
    Record a rent payment.
    
    This will:
    1. Create a new transaction (type=income, category=rent)
    2. Update the tenant's status to 'aktif' (if currently telat or dp)
    """
    # Verify tenant exists and belongs to the kost
    tenant = db.query(Tenant).filter(
        Tenant.id == data.tenant_id,
        Tenant.kost_id == data.kost_id,
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Get kost to retrieve region_id
    kost = db.query(Kost).filter(Kost.id == data.kost_id).first()
    
    # Create transaction
    transaction = Transaction(
        kost_id=data.kost_id,
        tenant_id=data.tenant_id,
        type="income",
        category="rent",
        amount=data.amount,
        transaction_date=data.transaction_date,
        description=f"Pembayaran sewa dari {tenant.name}",
        region_id=kost.region_id if kost else None,
    )
    db.add(transaction)
    
    # Update tenant status to aktif if currently telat or dp
    if tenant.status in ("telat", "dp"):
        tenant.status = "aktif"
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.post("/expenses", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Record an expense.
    
    Creates a new transaction with type=expense.
    Supports two modes:
    - Kost-level: provide kost_id (region_id auto-derived)
    - Region-level: provide region_id only (no kost)
    """
    if not data.kost_id and not data.region_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either kost_id or region_id must be provided"
        )
    
    resolved_region_id = data.region_id
    
    if data.kost_id:
        # Kost-level expense
        kost = db.query(Kost).filter(Kost.id == data.kost_id).first()
        if not kost:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kost not found"
            )
        resolved_region_id = kost.region_id
    
    # Create transaction
    transaction = Transaction(
        kost_id=data.kost_id,
        tenant_id=None,
        type="expense",
        category=data.category,
        amount=data.amount,
        transaction_date=data.transaction_date,
        description=data.description,
        region_id=resolved_region_id,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

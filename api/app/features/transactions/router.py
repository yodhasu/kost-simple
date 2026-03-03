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
    1. Create a new transaction (financial_class=REVENUE, category=rent)
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
    
    # Create rent income transaction
    description = f"Pembayaran sewa dari {tenant.name}"
    if tenant.status == "dp":
        description = f"Pelunasan DP dari {tenant.name}"

    rent_tx = Transaction(
        kost_id=data.kost_id,
        tenant_id=data.tenant_id,
        financial_class="REVENUE",
        category="rent",
        amount=data.amount,
        transaction_date=data.transaction_date,
        description=description,
        region_id=kost.region_id if kost else None,
        is_frozen=False,
    )
    db.add(rent_tx)
    db.flush()

    # If tenant has a frozen DP, release it as revenue and link to this rent payment.
    if tenant.status == "dp":
        dp_tx = (
            db.query(Transaction)
            .filter(
                Transaction.tenant_id == tenant.id,
                Transaction.category == "dp",
                Transaction.is_frozen == True,
            )
            .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
            .first()
        )
        if dp_tx:
            dp_tx.is_frozen = False
            dp_tx.financial_class = "REVENUE"
            dp_tx.reference_id = rent_tx.id

    # Record extra fees as contra expenses (linked to the rent payment).
    extra_fees = (
        (tenant.trash_fee or 0)
        + (tenant.security_fee or 0)
        + (tenant.admin_fee or 0)
    )
    if extra_fees > 0:
        fee_tx = Transaction(
            kost_id=data.kost_id,
            tenant_id=data.tenant_id,
            financial_class="EXPENSE",
            category="extra_fee",
            amount=extra_fees,
            transaction_date=data.transaction_date,
            description=f"Biaya ekstra penyewa {tenant.name}",
            region_id=kost.region_id if kost else None,
            is_frozen=False,
            reference_id=rent_tx.id,
        )
        db.add(fee_tx)
    
    # Update tenant status to aktif if currently telat or dp
    if tenant.status in ("telat", "dp"):
        tenant.status = "aktif"
    
    db.commit()
    db.refresh(rent_tx)
    
    return rent_tx


@router.post("/expenses", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Record an expense.
    
    Creates a new transaction with financial_class=EXPENSE.
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
        financial_class="EXPENSE",
        category=data.category,
        amount=data.amount,
        transaction_date=data.transaction_date,
        description=data.description,
        region_id=resolved_region_id,
        is_frozen=False,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

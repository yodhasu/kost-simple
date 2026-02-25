"""
Tenants service - Business logic with database operations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
import re

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from fastapi import HTTPException, status

from app.core.exceptions import NotFoundException
from app.features.tenants.model import Tenant
from app.features.tenants.schemas import TenantCreate, TenantUpdate
from app.features.kosts.model import Kost
from app.features.transactions.model import Transaction


class TenantsService:
    """Service class for tenants operations."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _extract_due_date_from_description(description: Optional[str]) -> Optional[date]:
        if not description:
            return None
        match = re.search(r"due_date:(\d{4}-\d{2}-\d{2})", description)
        if not match:
            return None
        try:
            return date.fromisoformat(match.group(1))
        except ValueError:
            return None

    def _get_dp_info(self, tenant_id: UUID) -> tuple[Optional[int], Optional[date]]:
        dp_tx = (
            self.db.query(Transaction)
            .filter(
                Transaction.tenant_id == tenant_id,
                cast(Transaction.type, String) == "income",
                Transaction.category == "dp",
            )
            .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
            .first()
        )
        if not dp_tx:
            return None, None
        return int(dp_tx.amount), self._extract_due_date_from_description(dp_tx.description)

    def _attach_dp_fields(self, tenant: Tenant) -> Tenant:
        dp_amount, dp_due_date = self._get_dp_info(tenant.id)
        setattr(tenant, "dp_amount", dp_amount)
        setattr(tenant, "dp_due_date", dp_due_date)
        return tenant

    def get_all(
        self, 
        kost_id: UUID = None,
        region_id: UUID = None,
        page: int = 1, 
        page_size: int = 10,
        search: str = None,
        status: str = None,
    ) -> tuple[List[Tenant], int]:
        """Get paginated list of tenants, optionally filtered by region."""
        query = self.db.query(Tenant)
        
        # Filter by region_id through kost relationship
        if region_id:
            # Get all kost IDs in this region
            kost_ids_in_region = (
                self.db.query(Kost.id)
                .filter(Kost.region_id == region_id)
                .all()
            )
            kost_ids = [k[0] for k in kost_ids_in_region]
            query = query.filter(Tenant.kost_id.in_(kost_ids))
        # Filter by kost_id if provided (more specific filter)
        if kost_id:
            query = query.filter(Tenant.kost_id == kost_id)

        # Filter by status
        if status:
            query = query.filter(Tenant.status == status)
        
        # Search by name or phone
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Tenant.name.ilike(search_term)) | 
                (Tenant.phone.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated items
        offset = (page - 1) * page_size
        items = (
            query
            .order_by(Tenant.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        items = [self._attach_dp_fields(item) for item in items]
        return items, total

    def get_by_id(self, tenant_id: UUID) -> Tenant:
        """Get tenant by ID."""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        if not tenant:
            raise NotFoundException(f"Tenant with id {tenant_id} not found")
        return self._attach_dp_fields(tenant)

    def create(self, data: TenantCreate) -> Tenant:
        """Create new tenant and optionally record initial payment transaction."""
        payload = data.model_dump()
        dp_amount = payload.pop("dp_amount", None)
        dp_due_date = payload.pop("dp_due_date", None)

        if payload.get("status") == "dp":
            if dp_amount is None or dp_amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="dp_amount must be greater than 0 when status is DP",
                )
            if dp_due_date is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="dp_due_date is required when status is DP",
                )

        tenant = Tenant(**payload)
        self.db.add(tenant)

        # Flush first to get tenant.id without committing yet.
        self.db.flush()

        # Auto-create initial income transaction if tenant has non-zero payable amount.
        # This keeps tenant creation and initial payment history in sync.
        kost = self.db.query(Kost).filter(Kost.id == tenant.kost_id).first()

        if tenant.status == "dp" and dp_amount and dp_amount > 0:
            transaction = Transaction(
                kost_id=tenant.kost_id,
                tenant_id=tenant.id,
                type="income",
                category="dp",
                amount=dp_amount,
                transaction_date=tenant.start_date or date.today(),
                description=f"Pembayaran DP penyewa {tenant.name} due_date:{dp_due_date.isoformat()}",
                region_id=kost.region_id if kost else None,
            )
            self.db.add(transaction)
        else:
            total_amount = (
                (tenant.rent_price or 0)
                + (tenant.trash_fee or 0)
                + (tenant.security_fee or 0)
                + (tenant.admin_fee or 0)
            )
            if total_amount > 0:
                transaction = Transaction(
                    kost_id=tenant.kost_id,
                    tenant_id=tenant.id,
                    type="income",
                    category="rent",
                    amount=total_amount,
                    transaction_date=tenant.start_date or date.today(),
                    description=f"Pembayaran awal penyewa {tenant.name}",
                    region_id=kost.region_id if kost else None,
                )
                self.db.add(transaction)

        self.db.commit()
        self.db.refresh(tenant)
        return self._attach_dp_fields(tenant)

    def update(self, tenant_id: UUID, data: TenantUpdate) -> Tenant:
        """Update existing tenant."""
        tenant = self.get_by_id(tenant_id)
        
        update_data = data.model_dump(exclude_unset=True)
        dp_amount = update_data.pop("dp_amount", None)
        dp_due_date = update_data.pop("dp_due_date", None)

        for key, value in update_data.items():
            setattr(tenant, key, value)

        # If tenant is in DP state and DP metadata is provided, upsert DP transaction metadata.
        if tenant.status == "dp" and (dp_amount is not None or dp_due_date is not None):
            dp_tx = (
                self.db.query(Transaction)
                .filter(
                    Transaction.tenant_id == tenant.id,
                    cast(Transaction.type, String) == "income",
                    Transaction.category == "dp",
                )
                .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
                .first()
            )
            kost = self.db.query(Kost).filter(Kost.id == tenant.kost_id).first()
            effective_dp_amount = dp_amount if dp_amount is not None else (int(dp_tx.amount) if dp_tx else 0)
            effective_due_date = dp_due_date or self._extract_due_date_from_description(dp_tx.description if dp_tx else None)

            if effective_dp_amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="dp_amount must be greater than 0 when status is DP",
                )
            if not effective_due_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="dp_due_date is required when status is DP",
                )

            if dp_tx:
                dp_tx.amount = effective_dp_amount
                dp_tx.description = f"Pembayaran DP penyewa {tenant.name} due_date:{effective_due_date.isoformat()}"
            else:
                self.db.add(
                    Transaction(
                        kost_id=tenant.kost_id,
                        tenant_id=tenant.id,
                        type="income",
                        category="dp",
                        amount=effective_dp_amount,
                        transaction_date=tenant.start_date or date.today(),
                        description=f"Pembayaran DP penyewa {tenant.name} due_date:{effective_due_date.isoformat()}",
                        region_id=kost.region_id if kost else None,
                    )
                )
        
        self.db.commit()
        self.db.refresh(tenant)
        return self._attach_dp_fields(tenant)

    def delete(self, tenant_id: UUID) -> None:
        """Soft delete tenant by setting is_active to False."""
        tenant = self.get_by_id(tenant_id)
        tenant.is_active = False
        self.db.commit()

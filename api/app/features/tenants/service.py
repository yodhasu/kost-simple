"""
Tenants service - Business logic with database operations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.exceptions import NotFoundException
from app.features.tenants.model import Tenant
from app.features.tenants.schemas import TenantCreate, TenantUpdate


class TenantsService:
    """Service class for tenants operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, 
        kost_id: UUID = None,
        page: int = 1, 
        page_size: int = 10,
        search: str = None
    ) -> tuple[List[Tenant], int]:
        """Get paginated list of tenants."""
        query = self.db.query(Tenant)
        
        # Filter by kost_id if provided
        if kost_id:
            query = query.filter(Tenant.kost_id == kost_id)
        
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
        
        return items, total

    def get_by_id(self, tenant_id: UUID) -> Tenant:
        """Get tenant by ID."""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        if not tenant:
            raise NotFoundException(f"Tenant with id {tenant_id} not found")
        
        return tenant

    def create(self, data: TenantCreate) -> Tenant:
        """Create new tenant."""
        tenant = Tenant(**data.model_dump())
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def update(self, tenant_id: UUID, data: TenantUpdate) -> Tenant:
        """Update existing tenant."""
        tenant = self.get_by_id(tenant_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)
        
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def delete(self, tenant_id: UUID) -> None:
        """Soft delete tenant by setting end_date."""
        tenant = self.get_by_id(tenant_id)
        tenant.end_date = date.today()
        tenant.status = "inactive"
        self.db.commit()

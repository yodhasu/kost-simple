"""
Tenants router - API endpoints.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.tenants.schemas import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
)
from app.features.tenants.service import TenantsService

router = APIRouter()


@router.get("", response_model=TenantListResponse)
async def get_tenants(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    search: Optional[str] = Query(None, description="Search by name or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get paginated list of tenants."""
    service = TenantsService(db)
    items, total = service.get_all(
        kost_id=kost_id,
        page=page, 
        page_size=page_size,
        search=search
    )
    return TenantListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: UUID, db: Session = Depends(get_db)):
    """Get a single tenant by ID."""
    service = TenantsService(db)
    return service.get_by_id(tenant_id)


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    """Create a new tenant."""
    service = TenantsService(db)
    return service.create(data)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: UUID, data: TenantUpdate, db: Session = Depends(get_db)):
    """Update an existing tenant."""
    service = TenantsService(db)
    return service.update(tenant_id, data)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: UUID, db: Session = Depends(get_db)):
    """Delete a tenant (soft delete)."""
    service = TenantsService(db)
    service.delete(tenant_id)

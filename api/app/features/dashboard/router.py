"""
Dashboard router - API endpoints.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_firebase_uid
from app.features.users.service import UserProfileService
from app.features.dashboard.schemas import (
    DashboardStats,
    IncomeTrendResponse,
    TenantTrackerResponse,
)
from app.features.dashboard.service import DashboardService

router = APIRouter()


from app.features.common.dependencies import get_current_user_region


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics (total tenants, rooms, occupancy)."""
    service = DashboardService(db)
    # If kost_id is provided, it overrides region filtering in the service logic (or refines it)
    # But for "collective data", we pass region_id mainy.
    return service.get_stats(kost_id=kost_id, region_id=region_id)


@router.get("/income-trend", response_model=IncomeTrendResponse)
async def get_income_trend(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    period: str = Query("month", pattern="^(month|semester|year)$", description="Period: month, semester, or year"),
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Get income trend data for chart."""
    service = DashboardService(db)
    return service.get_income_trend(kost_id=kost_id, region_id=region_id, period=period)


@router.get("/tenant-tracker", response_model=TenantTrackerResponse)
async def get_tenant_tracker(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of tenants to return"),
    region_id: Optional[UUID] = Depends(get_current_user_region),
    db: Session = Depends(get_db),
):
    """Get tenant payment status tracker."""
    service = DashboardService(db)
    return service.get_tenant_tracker(kost_id=kost_id, region_id=region_id, limit=limit)

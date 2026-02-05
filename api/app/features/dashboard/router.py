"""
Dashboard router - API endpoints.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.dashboard.schemas import (
    DashboardStats,
    IncomeTrendResponse,
    TenantTrackerResponse,
)
from app.features.dashboard.service import DashboardService

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics (total tenants, rooms, occupancy)."""
    service = DashboardService(db)
    return service.get_stats(kost_id=kost_id)


@router.get("/income-trend", response_model=IncomeTrendResponse)
async def get_income_trend(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    period: str = Query("month", regex="^(month|semester|year)$", description="Period: month, semester, or year"),
    db: Session = Depends(get_db),
):
    """Get income trend data for chart."""
    service = DashboardService(db)
    return service.get_income_trend(kost_id=kost_id, period=period)


@router.get("/tenant-tracker", response_model=TenantTrackerResponse)
async def get_tenant_tracker(
    kost_id: Optional[UUID] = Query(None, description="Filter by kost ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of tenants to return"),
    db: Session = Depends(get_db),
):
    """Get tenant payment status tracker."""
    service = DashboardService(db)
    return service.get_tenant_tracker(kost_id=kost_id, limit=limit)

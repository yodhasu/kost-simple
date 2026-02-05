"""
Dashboard schemas - Pydantic models for API responses.
"""

from typing import List, Optional
from decimal import Decimal
from datetime import date

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics response."""
    total_tenants: int
    total_rooms: int
    empty_rooms: int
    occupancy_rate: float
    tenant_change_percent: Optional[float] = None


class IncomeTrendItem(BaseModel):
    """Single income trend data point."""
    label: str
    amount: Decimal


class IncomeTrendResponse(BaseModel):
    """Income trend response."""
    period: str
    items: List[IncomeTrendItem]
    total: Decimal


class TenantPaymentStatus(BaseModel):
    """Payment status for tenant tracker."""
    type: str  # success, warning, danger
    label: str


class TenantTrackerItem(BaseModel):
    """Single tenant tracker item."""
    id: str
    name: str
    initials: str
    phone: Optional[str]
    room: str
    floor: str
    status: TenantPaymentStatus
    due_date: str
    action: str
    color: str  # purple, blue, red, orange, cyan, pink


class TenantTrackerResponse(BaseModel):
    """Tenant tracker list response."""
    items: List[TenantTrackerItem]
    total: int

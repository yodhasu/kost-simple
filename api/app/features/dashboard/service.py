"""
Dashboard service - Business logic for dashboard endpoints.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Tuple, Optional
from uuid import UUID

from sqlalchemy import func, and_, cast, String
from sqlalchemy.orm import Session

from app.features.kosts.model import Kost
from app.features.tenants.model import Tenant
from app.features.transactions.model import Transaction
from app.features.dashboard.schemas import (
    DashboardStats,
    IncomeTrendItem,
    IncomeTrendResponse,
    TenantPaymentStatus,
    TenantTrackerItem,
    TenantTrackerResponse,
)


class DashboardService:
    """Service for dashboard operations."""

    def __init__(self, db: Session):
        self.db = db

    def _get_kost_ids_by_region(self, region_id: UUID) -> List[UUID]:
        """Get all kost IDs for a given region."""
        return [
            id_tuple[0] for id_tuple in 
            self.db.query(Kost.id).filter(Kost.region_id == region_id).all()
        ]

    def get_stats(self, kost_id: UUID = None, region_id: UUID = None) -> DashboardStats:
        """Get dashboard statistics."""
        # Base query filters
        kost_filter = []
        if kost_id:
            kost_filter = [Kost.id == kost_id]
        elif region_id:
            kost_filter = [Kost.region_id == region_id]
            
        # Get total rooms from kost.total_units
        total_rooms_query = self.db.query(func.coalesce(func.sum(Kost.total_units), 0))
        if kost_filter:
            total_rooms_query = total_rooms_query.filter(*kost_filter)
        total_rooms = total_rooms_query.scalar() or 0

        # Count active tenants
        # Join with Kost to filter by region if needed
        active_tenants_query = self.db.query(func.count(Tenant.id)).join(Kost, Tenant.kost_id == Kost.id).filter(
            Tenant.status == "aktif",
            Tenant.is_active == True
        )
        if kost_filter:
            active_tenants_query = active_tenants_query.filter(*kost_filter)
        total_tenants = active_tenants_query.scalar() or 0

        # Empty rooms = total_units - active tenants
        empty_rooms = max(0, total_rooms - total_tenants)
        
        # Occupancy rate = (occupied / total) * 100
        occupancy_rate = (total_tenants / total_rooms * 100) if total_rooms > 0 else 0

        # Calculate tenant change (compare with last month)
        last_month = date.today().replace(day=1) - timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        
        last_month_query = self.db.query(func.count(Tenant.id)).join(Kost, Tenant.kost_id == Kost.id).filter(
            Tenant.status == "aktif",
            Tenant.is_active == True,
            Tenant.created_at < last_month_start
        )
        if kost_filter:
            last_month_query = last_month_query.filter(*kost_filter)
        last_month_count = last_month_query.scalar() or 0

        tenant_change = None
        if last_month_count > 0:
            tenant_change = round((total_tenants - last_month_count) / last_month_count * 100, 1)

        return DashboardStats(
            total_tenants=total_tenants,
            total_rooms=int(total_rooms),
            empty_rooms=empty_rooms,
            occupancy_rate=round(occupancy_rate, 1),
            tenant_change_percent=tenant_change
        )

    def get_income_trend(self, kost_id: UUID = None, region_id: UUID = None, period: str = "month") -> IncomeTrendResponse:
        """Get income trend for a specific period (month, semester, year)."""
        today = date.today()
        items = []
        total = Decimal("0")
        
        # Month abbreviations in Indonesian
        month_abbr = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", 
                      "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        
        # Determine start and end dates based on period
        if period == "month":
            # Current month only
            start_date = today.replace(day=1)
            # End of current month
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            period_label = f"Bulan {month_abbr[today.month - 1]} {today.year}"
            
        elif period == "semester":
            # Current semester (Jan-Jun or Jul-Dec)
            if today.month <= 6:
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=6, day=30)
                period_label = f"Semester 1 {today.year}"
            else:
                start_date = today.replace(month=7, day=1)
                end_date = today.replace(month=12, day=31)
                period_label = f"Semester 2 {today.year}"
                
        else:  # year
            # Current year
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            period_label = f"Tahun {today.year}"
        
        # Determine filters
        kost_filter = []
        if kost_id:
            kost_filter = [Kost.id == kost_id]
        elif region_id:
            kost_filter = [Kost.region_id == region_id]

        # Generate weeks within the period
        current = start_date
        current = current - timedelta(days=current.weekday()) # Start of week (Monday)
        
        week_num = 1
        while current <= end_date:
            week_start = current
            week_end = current + timedelta(days=6)
            
            # Clamp to period boundaries
            query_start = max(week_start, start_date)
            query_end = min(week_end, end_date)
            
            if query_start <= query_end:
                # Query income for this week
                query = self.db.query(func.coalesce(func.sum(Transaction.amount), 0)).join(Kost, Transaction.kost_id == Kost.id).filter(
                    and_(
                        cast(Transaction.type, String) == "income",
                        Transaction.transaction_date >= query_start,
                        Transaction.transaction_date <= query_end
                    )
                )
                
                if kost_filter:
                    query = query.filter(*kost_filter)
                
                amount = query.scalar() or Decimal("0")
            else:
                amount = Decimal("0")

            total += amount
            
            # Generate label
            if period == "month":
                label = f"Minggu {week_num}"
            else:
                month_name = month_abbr[week_start.month - 1]
                week_of_month = (week_start.day - 1) // 7 + 1
                label = f"{month_name} W{week_of_month}"
            
            items.append(IncomeTrendItem(
                label=label,
                amount=amount
            ))
            
            current += timedelta(days=7)
            week_num += 1

        return IncomeTrendResponse(
            period=period_label,
            items=items,
            total=total
        )

    def get_tenant_tracker(self, kost_id: UUID = None, region_id: UUID = None, limit: int = 10) -> TenantTrackerResponse:
        """Get tenant payment status tracker."""
        today = date.today()
        
        # Get active tenants
        query = self.db.query(Tenant).join(Kost, Tenant.kost_id == Kost.id).filter(
            Tenant.status == "aktif",
            Tenant.is_active == True
        )
        
        if kost_id:
            query = query.filter(Tenant.kost_id == kost_id)
        elif region_id:
            query = query.filter(Kost.region_id == region_id)
        
        tenants = query.limit(limit).all()
        items = []
        colors = ["orange", "cyan", "pink", "purple", "blue"]

        for idx, tenant in enumerate(tenants):
            # Determine payment status based on last transaction
            last_payment = self.db.query(Transaction).filter(
                and_(
                    Transaction.tenant_id == tenant.id,
                    cast(Transaction.type, String) == "income",
                    Transaction.category == "rent"
                )
            ).order_by(Transaction.transaction_date.desc()).first()

            # Calculate due date (assume monthly rent, due on day 25)
            current_month_due = today.replace(day=25) if today.day < 25 else (today.replace(day=1) + timedelta(days=32)).replace(day=25)
            
            if last_payment and last_payment.transaction_date.month == today.month:
                status = TenantPaymentStatus(type="success", label="Lunas")
                action = "Detail"
            elif today.day > 25:
                status = TenantPaymentStatus(type="danger", label="Terlambat")
                action = "Tagih"
            else:
                status = TenantPaymentStatus(type="warning", label="Menunggu")
                action = "Ingatkan"

            # Format due date
            months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
            due_date_str = f"{current_month_due.day} {months[current_month_due.month - 1]} {current_month_due.year}"

            # Get initials
            name_parts = tenant.name.split()
            initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "?"

            # Get room info from kost
            kost = self.db.query(Kost).filter(Kost.id == tenant.kost_id).first()
            room = f"{kost.name[:1]}-{str(idx + 101)}" if kost else f"R-{idx + 1}"

            items.append(TenantTrackerItem(
                id=str(tenant.id),
                name=tenant.name,
                initials=initials,
                phone=tenant.phone,
                room=room,
                floor="Lantai 1",
                status=status,
                due_date=due_date_str,
                action=action,
                color=colors[idx % len(colors)]
            ))

        return TenantTrackerResponse(items=items, total=len(items))

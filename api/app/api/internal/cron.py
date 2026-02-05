"""
Internal Cron Endpoints - Not user-facing.
These endpoints are called by external schedulers (cron jobs).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter(tags=["cron"])


@router.post("/update-tenant-status")
def update_tenant_status(db: Session = Depends(get_db)):
    """
    Update tenant status from 'aktif' to 'telat' if they haven't paid rent
    for the current month.
    
    This is idempotent and safe to run repeatedly.
    """
    result = db.execute(text("""
        UPDATE tenants t
        SET status = 'telat'
        WHERE
            t.end_date IS NULL
            AND t.status = 'aktif'
            AND current_date > t.start_date + interval '1 month'
            AND NOT EXISTS (
                SELECT 1
                FROM transactions tr
                WHERE
                    tr.tenant_id = t.id
                    AND tr.type = 'income'
                    AND tr.category = 'rent'
                    AND date_trunc('month', tr.transaction_date)
                        = date_trunc('month', current_date)
            )
    """))

    db.commit()

    return {
        "updated": result.rowcount
    }

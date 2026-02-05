"""
Internal Cron Endpoints - Not user-facing.
These endpoints are called by external schedulers (cron jobs).
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.config import settings

router = APIRouter(tags=["cron"])


def verify_cron_secret(x_cron_key: str = Header(...)):
    """Verify the X-Cron-Key header matches CRON_SECRET."""
    if not settings.CRON_SECRET:
        raise HTTPException(status_code=500, detail="CRON_SECRET not configured")
    if x_cron_key != settings.CRON_SECRET:
        raise HTTPException(status_code=401, detail="Invalid cron key")
    return True


@router.post("/update-tenant-status")
def update_tenant_status(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_cron_secret)
):
    """
    Update tenant status from 'aktif' to 'telat' if they haven't paid rent
    for the current month.
    
    This is idempotent and safe to run repeatedly.
    Requires X-Cron-Key header for authentication.
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

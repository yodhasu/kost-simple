"""
Sidebar router - endpoints for sidebar guard checks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_firebase_uid
from app.db.session import get_db
from app.features.failsafe.schemas import SidebarUnlockResponse
from app.features.regions.model import Regions
from app.features.users.model import UserProfile

router = APIRouter()


@router.get("/unlock", response_model=SidebarUnlockResponse)
async def sidebar_unlock(
    firebase_uid: str = Depends(get_current_firebase_uid),
    db: Session = Depends(get_db),
):
    """
    Sidebar unlock check:
    - At least one region exists
    - At least one admin/it account exists
    """
    caller = db.query(UserProfile).filter(UserProfile.firebase_uid == firebase_uid).first()
    if not caller:
        raise HTTPException(status_code=403, detail="User profile not found.")

    regions_total = db.query(Regions).count()
    admins_total = (
        db.query(UserProfile)
        .filter(UserProfile.role.in_(["admin", "it"]))
        .count()
    )
    unlock = regions_total > 0 and admins_total > 0

    return SidebarUnlockResponse(
        regions_total=regions_total,
        admins_total=admins_total,
        unlock=unlock,
    )

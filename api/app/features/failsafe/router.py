"""
Failsafe router - sanity checks and repair helpers for fresh/blank DB states.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_firebase_uid
from app.db.session import get_db
from app.features.failsafe.schemas import FailsafeResponse
from app.features.regions.model import Regions
from app.features.users.model import UserProfile
from app.features.users.user_region_model import UserRegion

router = APIRouter()


@router.post("", response_model=FailsafeResponse)
async def failsafe(
    firebase_uid: str = Depends(get_current_firebase_uid),
    db: Session = Depends(get_db),
):
    """
    Failsafe endpoint:
    1. Check if an owner profile exists.
    2. Ensure the (caller) owner is assigned to all regions via user_regions.
    3. Report whether regions are empty (regions are the root of the data graph).
    """
    caller = db.query(UserProfile).filter(UserProfile.firebase_uid == firebase_uid).first()
    if not caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User profile not found.")
    if caller.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can run failsafe.")

    # (1) Check if any owner exists (not just caller, but caller should be owner already)
    owner_profile = db.query(UserProfile).filter(UserProfile.role == "owner").order_by(UserProfile.created_at.asc()).first()
    owner_profile_exists = owner_profile is not None

    regions_total = db.query(Regions).count()
    regions_empty = regions_total == 0

    before = db.query(UserRegion).filter(UserRegion.user_id == caller.id).count()

    added = 0
    if not regions_empty:
        all_region_ids = [r.id for r in db.query(Regions.id).all()]
        existing = {
            ur.region_id
            for ur in db.query(UserRegion.region_id).filter(UserRegion.user_id == caller.id).all()
        }
        missing = [rid for rid in all_region_ids if rid not in existing]
        for rid in missing:
            db.add(UserRegion(user_id=caller.id, region_id=rid))
            added += 1
        if added:
            db.commit()

    after = db.query(UserRegion).filter(UserRegion.user_id == caller.id).count()

    return FailsafeResponse(
        owner_profile_exists=owner_profile_exists,
        owner_user_id=caller.id,
        regions_total=regions_total,
        regions_empty=regions_empty,
        owner_region_assignments_before=before,
        owner_region_assignments_after=after,
        owner_region_assignments_added=added,
    )


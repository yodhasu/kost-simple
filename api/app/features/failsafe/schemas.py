from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FailsafeResponse(BaseModel):
    owner_profile_exists: bool
    owner_user_id: Optional[UUID] = None
    regions_total: int
    regions_empty: bool
    owner_region_assignments_before: int
    owner_region_assignments_after: int
    owner_region_assignments_added: int


class SetupCheckResponse(BaseModel):
    regions_total: int
    admins_total: int
    regions_empty: bool
    admins_empty: bool
    setup_complete: bool

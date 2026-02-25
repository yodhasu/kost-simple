"""
User Profile service - Business logic with database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, BadRequestException
from app.core.firebase_admin_client import (
    create_firebase_user,
    delete_firebase_user,
    generate_password_reset_link,
    get_firebase_user_by_uid,
)
from app.features.users.model import UserProfile
from app.features.users.schemas import AdminAccountCreate, AdminAccountItem
from app.features.users.user_region_model import UserRegion
from app.features.regions.model import Regions


class UserProfileService:
    """Service class for user profile operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[UserProfile]:
        """Get user profile by Firebase UID."""
        return self.db.query(UserProfile).filter(
            UserProfile.firebase_uid == firebase_uid
        ).first()

    def get_by_firebase_uid_or_404(self, firebase_uid: str) -> UserProfile:
        """Get user profile by Firebase UID or raise 404."""
        profile = self.get_by_firebase_uid(firebase_uid)
        if not profile:
            raise NotFoundException(f"User profile not found for firebase_uid: {firebase_uid}")
        return profile

    def list_admin_accounts(self) -> list[AdminAccountItem]:
        profiles = (
            self.db.query(UserProfile)
            .filter(UserProfile.role.in_(["admin", "it"]))
            .order_by(UserProfile.created_at.desc())
            .all()
        )

        items: list[AdminAccountItem] = []
        for profile in profiles:
            user_regions = (
                self.db.query(UserRegion, Regions)
                .join(Regions, Regions.id == UserRegion.region_id)
                .filter(UserRegion.user_id == profile.id)
                .all()
            )
            region_ids = [user_region.region_id for user_region, _region in user_regions]
            region_names = [region.name for _user_region, region in user_regions]

            try:
                firebase_user = get_firebase_user_by_uid(profile.firebase_uid)
            except Exception:
                # If Firebase Admin isn't configured in this environment, don't 500 the whole list endpoint.
                firebase_user = None
            items.append(
                AdminAccountItem(
                    id=profile.id,
                    firebase_uid=profile.firebase_uid,
                    name=profile.name,
                    email=firebase_user.email if firebase_user else None,
                    role=profile.role,
                    region_ids=region_ids,
                    region_names=region_names,
                    created_at=profile.created_at,
                )
            )
        return items

    def create_admin_account(self, data: AdminAccountCreate) -> AdminAccountItem:
        if data.role not in ("admin", "it"):
            raise BadRequestException("role must be either 'admin' or 'it'")
        if not data.region_ids:
            raise BadRequestException("At least one region must be selected")

        firebase_user = create_firebase_user(
            email=data.email,
            password=data.password,
            display_name=data.name,
        )

        try:
            profile = UserProfile(
                firebase_uid=firebase_user.uid,
                name=data.name,
                role=data.role,
            )
            self.db.add(profile)
            self.db.flush()

            for region_id in data.region_ids:
                self.db.add(
                    UserRegion(
                        user_id=profile.id,
                        region_id=region_id,
                    )
                )
            self.db.commit()
            self.db.refresh(profile)
        except Exception:
            self.db.rollback()
            delete_firebase_user(firebase_user.uid)
            raise

        regions = self.db.query(Regions).filter(Regions.id.in_(data.region_ids)).all()
        return AdminAccountItem(
            id=profile.id,
            firebase_uid=profile.firebase_uid,
            name=profile.name,
            email=data.email,
            role=profile.role,
            region_ids=data.region_ids,
            region_names=[region.name for region in regions],
            created_at=profile.created_at,
        )

    def generate_admin_password_reset(self, user_id: UUID) -> str:
        profile = self.db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            raise NotFoundException("Admin account not found")
        if profile.role not in ("admin", "it"):
            raise NotFoundException("Target user is not an admin account")

        firebase_user = get_firebase_user_by_uid(profile.firebase_uid)
        if not firebase_user or not firebase_user.email:
            raise NotFoundException("Firebase user/email not found for this account")

        return generate_password_reset_link(firebase_user.email)

    def update_admin_regions(self, user_id: UUID, region_ids: list[UUID]) -> AdminAccountItem:
        profile = self.db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            raise NotFoundException("Admin account not found")
        if profile.role not in ("admin", "it"):
            raise NotFoundException("Target user is not an admin account")
        if not region_ids:
            raise BadRequestException("At least one region must be selected")

        self.db.query(UserRegion).filter(UserRegion.user_id == profile.id).delete()
        for region_id in region_ids:
            self.db.add(UserRegion(user_id=profile.id, region_id=region_id))
        self.db.commit()

        regions = self.db.query(Regions).filter(Regions.id.in_(region_ids)).all()
        firebase_user = get_firebase_user_by_uid(profile.firebase_uid)
        return AdminAccountItem(
            id=profile.id,
            firebase_uid=profile.firebase_uid,
            name=profile.name,
            email=firebase_user.email if firebase_user else None,
            role=profile.role,
            region_ids=region_ids,
            region_names=[region.name for region in regions],
            created_at=profile.created_at,
        )

    def delete_admin_account(self, user_id: UUID) -> None:
        profile = self.db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            raise NotFoundException("Admin account not found")
        if profile.role not in ("admin", "it"):
            raise NotFoundException("Target user is not an admin account")

        self.db.query(UserRegion).filter(UserRegion.user_id == profile.id).delete()
        self.db.delete(profile)
        self.db.commit()

        delete_firebase_user(profile.firebase_uid)

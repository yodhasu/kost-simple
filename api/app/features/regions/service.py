"""
Regions service - Business logic.
"""

from typing import List, Optional
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.regions.model import Regions
from app.core.exceptions import NotFoundException
from app.features.regions.schemas import RegionsCreate, RegionsUpdate
from app.features.users.model import UserProfile
from app.features.users.user_region_model import UserRegion
from app.features.kosts.model import Kost
from app.features.tenants.model import Tenant
from app.features.transactions.model import Transaction


class RegionsService:
    """Service class for regions operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Regions]:
        """Get all regions."""
        query = self.db.query(Regions)
        items = query.order_by(Regions.created_at.desc()).all()
        return items

    def get_by_id(self, item_id: UUID) -> Regions:
        """Get by ID."""
        item = self.db.query(Regions).filter(Regions.id == item_id).first()
        if not item:
            raise NotFoundException(f"Regions with id {item_id} not found")
        return item

    def create(self, data: RegionsCreate) -> Regions:
        """Create new item."""
        db_item = Regions(**data.model_dump())
        self.db.add(db_item)
        self.db.flush()

        owners = self.db.query(UserProfile).filter(UserProfile.role == "owner").all()
        for owner in owners:
            self.db.add(UserRegion(user_id=owner.id, region_id=db_item.id))

        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, item_id: UUID, data: RegionsUpdate) -> Regions:
        """Update existing item."""
        item = self.get_by_id(item_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item_id: UUID) -> None:
        """Delete item."""
        item = self.get_by_id(item_id)
        # Block deletion when region still has data.
        has_kost = self.db.query(Kost.id).filter(Kost.region_id == item_id).first() is not None
        has_tenants = (
            self.db.query(Tenant.id)
            .join(Kost, Tenant.kost_id == Kost.id)
            .filter(Kost.region_id == item_id)
            .first()
            is not None
        )
        has_transactions = self.db.query(Transaction.id).filter(Transaction.region_id == item_id).first() is not None

        if has_kost or has_tenants or has_transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region masih memiliki data terkait. Hapus data kost, penyewa, dan transaksi terlebih dahulu.",
            )

        self.db.query(UserRegion).filter(UserRegion.region_id == item_id).delete(synchronize_session=False)
        self.db.delete(item)
        self.db.commit()

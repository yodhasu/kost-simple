"""
Kosts service - Business logic with database operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.exceptions import NotFoundException
from app.features.kosts.model import Kost
from app.features.kosts.schemas import KostCreate, KostUpdate


class KostsService:
    """Service class for kosts operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, page: int = 1, page_size: int = 10, region_id: Optional[UUID] = None) -> tuple[List[Kost], int]:
        """Get paginated list of kosts, optionally filtered by region."""
        query = self.db.query(Kost)
        
        if region_id:
            query = query.filter(Kost.region_id == region_id)

        # Get total count
        total = query.with_entities(func.count(Kost.id)).scalar()
        
        # Get paginated items
        offset = (page - 1) * page_size
        items = (
            query
            .order_by(Kost.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return items, total

    def get_by_id(self, kost_id: UUID) -> Kost:
        """Get kost by ID."""
        kost = self.db.query(Kost).filter(Kost.id == kost_id).first()
        
        if not kost:
            raise NotFoundException(f"Kost with id {kost_id} not found")
        
        return kost

    def create(self, data: KostCreate) -> Kost:
        """Create new kost."""
        kost = Kost(**data.model_dump())
        self.db.add(kost)
        self.db.commit()
        self.db.refresh(kost)
        return kost

    def update(self, kost_id: UUID, data: KostUpdate) -> Kost:
        """Update existing kost."""
        kost = self.get_by_id(kost_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(kost, key, value)
        
        self.db.commit()
        self.db.refresh(kost)
        return kost

    def delete(self, kost_id: UUID) -> None:
        """Delete kost."""
        kost = self.get_by_id(kost_id)
        self.db.delete(kost)
        self.db.commit()

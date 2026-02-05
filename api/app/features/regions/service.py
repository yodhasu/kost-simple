"""
Regions service - Business logic.
"""

from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.features.regions.model import Regions
from app.core.exceptions import NotFoundException
from app.features.regions.schemas import RegionsCreate, RegionsUpdate


class RegionsService:
    """Service class for regions operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, page: int = 1, page_size: int = 10) -> tuple[List[Regions], int]:
        """Get paginated list."""
        query = self.db.query(Regions)
        total = query.count()
        items = (
            query.order_by(Regions.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

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
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, item_id: UUID, data: RegionsUpdate) -> Regions:
        """Update existing item."""
        item = self.get_by_id(item_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        
        item.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item_id: UUID) -> None:
        """Delete item."""
        item = self.get_by_id(item_id)
        self.db.delete(item)
        self.db.commit()

"""
UserRegion model - SQLAlchemy ORM model for user-region junction table.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserRegion(Base):
    """Junction table linking users to regions (many-to-many)."""
    
    __tablename__ = "user_regions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), primary_key=True)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)

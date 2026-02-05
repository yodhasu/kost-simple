"""
User Profile model - SQLAlchemy ORM model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class UserProfile(Base):
    """User profile database model - links Firebase UID to role and region."""
    
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

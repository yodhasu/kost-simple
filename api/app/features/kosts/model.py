"""
Kost model - SQLAlchemy ORM model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Kost(Base):
    """Kost database model."""
    
    __tablename__ = "kosts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    total_units = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

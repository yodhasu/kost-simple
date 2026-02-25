"""
Tenant model - SQLAlchemy ORM model.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, BigInteger, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Tenant(Base):
    """Tenant database model."""
    
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kost_id = Column(UUID(as_uuid=True), ForeignKey("kosts.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    rent_price = Column(BigInteger, nullable=True)
    trash_fee = Column(Integer, nullable=True)
    security_fee = Column(Integer, nullable=True)
    admin_fee = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="active")  # active, inactive, pending
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    kost = relationship("Kost", backref="tenants")

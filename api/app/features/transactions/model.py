"""
Transaction model - SQLAlchemy ORM model.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Transaction(Base):
    """Transaction database model."""
    
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kost_id = Column(UUID(as_uuid=True), ForeignKey("kosts.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    type = Column(String, nullable=False)  # income, expense
    category = Column(String, nullable=True)  # rent, utilities, maintenance, etc.
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    kost = relationship("Kost", backref="transactions")
    tenant = relationship("Tenant", backref="transactions")

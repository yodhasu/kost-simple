"""
Transaction model - SQLAlchemy ORM model.
"""

import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class Transaction(Base):
    """Transaction database model."""
    
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kost_id = Column(UUID(as_uuid=True), ForeignKey("kosts.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    # Use existing PostgreSQL enum type "type" from the database schema.
    # Values are declared so SQLAlchemy can correctly deserialize DB rows.
    type = Column(
        PGEnum("income", "expense", name="type", create_type=False),
        nullable=False,
    )
    category = Column(String, nullable=True)  # rent, utilities, maintenance, etc.
    amount = Column(BigInteger, nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=True)

    # Relationships
    kost = relationship("Kost", backref="transactions")
    tenant = relationship("Tenant", backref="transactions")
    region = relationship("Regions", backref="transactions")

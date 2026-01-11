import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Enum, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from .database import Base


class SubConsultantTier(str, PyEnum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"


class CapacityStatus(str, PyEnum):
    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"


class Discipline(Base):
    """Disciplines that may require sub-consultants."""
    __tablename__ = "disciplines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_internal: Mapped[bool] = mapped_column(default=False)  # Can be done in-house
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)  # For matching
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SubConsultant(Base):
    """External sub-consultant partners."""
    __tablename__ = "subconsultants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenancy: organization isolation
    organization_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Company info
    company_name: Mapped[str] = mapped_column(String(512))
    discipline: Mapped[str] = mapped_column(String(256))  # e.g., "Geotechnical Engineering"
    tier: Mapped[SubConsultantTier] = mapped_column(Enum(SubConsultantTier), default=SubConsultantTier.TIER_1)

    # Primary contact
    primary_contact_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    primary_contact_email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    primary_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Performance metrics
    past_joint_projects: Mapped[int] = mapped_column(Integer, default=0)
    win_rate_together: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0

    # Commercial
    typical_fee_range_low: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    typical_fee_range_high: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    capacity_status: Mapped[CapacityStatus] = mapped_column(Enum(CapacityStatus), default=CapacityStatus.AVAILABLE)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_project_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

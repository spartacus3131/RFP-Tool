import uuid
from datetime import datetime, date
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Date, Enum, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector

from .database import Base


class RFPStatus(str, PyEnum):
    NEW = "new"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    REVIEWED = "reviewed"
    GO = "go"
    NO_GO = "no_go"


class RFPSource(str, PyEnum):
    QUICK_SCAN = "quick_scan"  # From URL scrape
    PDF_UPLOAD = "pdf_upload"  # From uploaded PDF


class RFPDocument(Base):
    __tablename__ = "rfp_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Source info
    source: Mapped[RFPSource] = mapped_column(Enum(RFPSource), default=RFPSource.PDF_UPLOAD)
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Status
    status: Mapped[RFPStatus] = mapped_column(Enum(RFPStatus), default=RFPStatus.NEW)

    # Core extracted fields
    rfp_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    client_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    opportunity_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Contact info
    client_contact_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    client_contact_email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    client_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Key dates
    published_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    question_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submission_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    contract_duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Scope
    scope_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # Disciplines (from deep scan)
    required_internal_disciplines: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    required_external_disciplines: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Requirements (from deep scan)
    evaluation_criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    reference_requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    qualification_requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Risk/Compliance (from deep scan)
    insurance_requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_flags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    eligibility_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Budget matching
    matched_budget_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    budget_match_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Decision
    decision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Quick scan recommendation
    quick_scan_recommendation: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # GO, MAYBE, NO_GO

    # Vector embedding for semantic search
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536), nullable=True)

    # Relationships
    extractions: Mapped[List["Extraction"]] = relationship("Extraction", back_populates="rfp", cascade="all, delete-orphan")


class Extraction(Base):
    """Links extracted data back to source PDF location."""
    __tablename__ = "extractions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfp_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rfp_documents.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # What was extracted
    field_name: Mapped[str] = mapped_column(String(100))
    extracted_value: Mapped[str] = mapped_column(Text)

    # Source linking
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_bbox: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {x0, y0, x1, y1}

    # Confidence and verification
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    human_edited: Mapped[bool] = mapped_column(default=False)

    # Relationship
    rfp: Mapped["RFPDocument"] = relationship("RFPDocument", back_populates="extractions")

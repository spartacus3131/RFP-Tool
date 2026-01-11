"""
Capital Budget models for fuzzy budget matching.

Stores municipal capital budgets and extracted line items
with vector embeddings for semantic matching to RFP scopes.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from .database import Base


class CapitalBudget(Base):
    """A municipal capital budget document."""
    __tablename__ = "capital_budgets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Multi-tenancy: organization isolation
    organization_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Source info
    municipality: Mapped[str] = mapped_column(String(256))  # e.g., "City of Brampton"
    fiscal_year: Mapped[str] = mapped_column(String(20))    # e.g., "2024" or "2024-2025"
    filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    # Extracted text
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    line_items: Mapped[List["BudgetLineItem"]] = relationship(
        "BudgetLineItem", back_populates="budget", cascade="all, delete-orphan"
    )


class BudgetLineItem(Base):
    """A single line item from a capital budget."""
    __tablename__ = "budget_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("capital_budgets.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Project info
    project_name: Mapped[str] = mapped_column(String(512))
    project_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Budget project code
    department: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    
    # Funding
    total_budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_year_budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    funding_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Planning, Design, Construction
    
    # Description/Justification
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source linking
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Vector embedding for semantic search (1536 dims for OpenAI ada-002)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536), nullable=True)
    
    # Relationship
    budget: Mapped["CapitalBudget"] = relationship("CapitalBudget", back_populates="line_items")

"""
Audit Log Model - Track user actions for security and compliance.
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from enum import Enum as PyEnum
import uuid

from app.models.database import Base


class AuditAction(str, PyEnum):
    """Types of auditable actions."""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    UPLOAD = "upload"
    EXTRACT = "extract"
    EXPORT = "export"
    DECISION = "decision"


class AuditLog(Base):
    """
    Audit log entry for tracking user actions.

    Stores who did what, when, and from where for compliance
    and security monitoring.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Who
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    user_email: Mapped[str] = mapped_column(String(255), nullable=True)

    # What
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction), nullable=False, index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "rfp", "subconsultant"
    resource_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    details: Mapped[dict] = mapped_column(JSONB, nullable=True)  # Additional context

    # When
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Where
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv6 max length
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)

    # Result
    success: Mapped[bool] = mapped_column(default=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action.value} by {self.user_email} at {self.timestamp}>"

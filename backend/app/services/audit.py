"""
Audit Service - Log user actions for security and compliance.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.models.audit_log import AuditLog, AuditAction


async def log_action(
    db: AsyncSession,
    action: AuditAction,
    user_id: Optional[UUID] = None,
    user_email: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> AuditLog:
    """
    Log an auditable action.

    Args:
        db: Database session
        action: Type of action performed
        user_id: ID of user performing action
        user_email: Email of user (for easier querying)
        resource_type: Type of resource affected (e.g., "rfp", "subconsultant")
        resource_id: ID of resource affected
        details: Additional context as JSON
        ip_address: Client IP address
        user_agent: Client user agent string
        success: Whether the action succeeded
        error_message: Error message if action failed

    Returns:
        Created AuditLog entry
    """
    log_entry = AuditLog(
        action=action,
        user_id=user_id,
        user_email=user_email,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message,
    )

    db.add(log_entry)
    # Note: The caller should commit the transaction
    # This allows batching with other operations

    return log_entry


def get_client_ip(request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check for forwarded header (when behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    # Fall back to direct connection
    if request.client:
        return request.client.host

    return "unknown"


def get_user_agent(request) -> Optional[str]:
    """Extract user agent from request."""
    return request.headers.get("User-Agent", "")[:500]  # Truncate to max length

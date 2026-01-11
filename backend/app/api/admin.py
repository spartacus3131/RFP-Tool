"""
Admin API - Audit logs and system administration.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.models.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction
from app.auth import get_current_active_user


router = APIRouter()


class AuditLogResponse(BaseModel):
    id: str
    user_email: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[dict]
    timestamp: datetime
    ip_address: Optional[str]
    success: bool
    error_message: Optional[str]


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Ensure current user is an admin (superuser)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    action: Optional[str] = None,
    user_email: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    success_only: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """
    Query audit logs with filters.

    Admin-only endpoint for security monitoring and compliance.
    """
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))

    # Apply filters
    if action:
        try:
            query = query.where(AuditLog.action == AuditAction(action))
        except ValueError:
            raise HTTPException(400, f"Invalid action: {action}")

    if user_email:
        query = query.where(AuditLog.user_email == user_email)

    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    if start_date:
        query = query.where(AuditLog.timestamp >= start_date)

    if end_date:
        query = query.where(AuditLog.timestamp <= end_date)

    if success_only is not None:
        query = query.where(AuditLog.success == success_only)

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        AuditLogResponse(
            id=str(log.id),
            user_email=log.user_email,
            action=log.action.value,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            timestamp=log.timestamp,
            ip_address=log.ip_address,
            success=log.success,
            error_message=log.error_message,
        )
        for log in logs
    ]


@router.get("/audit-logs/stats")
async def get_audit_stats(
    days: int = Query(default=7, le=90),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """
    Get audit log statistics for the specified period.

    Useful for security dashboards and anomaly detection.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Count by action type
    action_counts = {}
    for action in AuditAction:
        result = await db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.action == action,
                AuditLog.timestamp >= start_date
            )
        )
        action_counts[action.value] = result.scalar() or 0

    # Count failed logins
    result = await db.execute(
        select(func.count(AuditLog.id)).where(
            AuditLog.action == AuditAction.LOGIN_FAILED,
            AuditLog.timestamp >= start_date
        )
    )
    failed_logins = result.scalar() or 0

    # Count unique users active
    result = await db.execute(
        select(func.count(func.distinct(AuditLog.user_id))).where(
            AuditLog.user_id.isnot(None),
            AuditLog.timestamp >= start_date
        )
    )
    active_users = result.scalar() or 0

    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "action_counts": action_counts,
        "failed_logins": failed_logins,
        "active_users": active_users,
    }

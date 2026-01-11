"""
Dashboard API - Overview stats and RFP list.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.rfp import RFPDocument, RFPStatus
from app.models.user import User
from app.auth import get_current_active_user


router = APIRouter()


def escape_like_pattern(value: str) -> str:
    """Escape special characters for LIKE/ILIKE queries."""
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


@router.get("/")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get dashboard overview with stats and recent RFPs.
    """
    # Get user's organization for filtering (multi-tenancy)
    org_filter = RFPDocument.organization_id == current_user.organization if current_user.organization else True

    # Count by status (filtered by organization)
    status_counts = {}
    for status in RFPStatus:
        result = await db.execute(
            select(func.count(RFPDocument.id)).where(
                RFPDocument.status == status,
                org_filter
            )
        )
        status_counts[status.value] = result.scalar() or 0

    # Total RFPs (filtered by organization)
    total_result = await db.execute(
        select(func.count(RFPDocument.id)).where(org_filter)
    )
    total = total_result.scalar() or 0

    # Recent RFPs (last 30 days, filtered by organization)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_result = await db.execute(
        select(RFPDocument)
        .where(
            RFPDocument.created_at >= thirty_days_ago,
            org_filter
        )
        .order_by(RFPDocument.created_at.desc())
        .limit(10)
    )
    recent_rfps = recent_result.scalars().all()

    # Calculate go rate
    total_decided = status_counts.get("go", 0) + status_counts.get("no_go", 0)
    go_rate = (status_counts.get("go", 0) / total_decided * 100) if total_decided > 0 else 0

    return {
        "stats": {
            "total_rfps": total,
            "by_status": status_counts,
            "go_rate": round(go_rate, 1),
            "pending_decisions": status_counts.get("extracted", 0) + status_counts.get("reviewed", 0),
        },
        "recent_rfps": [
            {
                "id": str(rfp.id),
                "rfp_number": rfp.rfp_number,
                "client_name": rfp.client_name,
                "opportunity_title": rfp.opportunity_title,
                "status": rfp.status.value,
                "submission_deadline": str(rfp.submission_deadline) if rfp.submission_deadline else None,
                "created_at": rfp.created_at.isoformat(),
                "recommendation": rfp.quick_scan_recommendation,
            }
            for rfp in recent_rfps
        ],
    }


@router.get("/rfps")
async def list_rfps(
    status: Optional[str] = None,
    client: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all RFPs with optional filters.
    """
    # Multi-tenancy: filter by organization
    org_filter = RFPDocument.organization_id == current_user.organization if current_user.organization else True
    query = select(RFPDocument).where(org_filter).order_by(RFPDocument.created_at.desc())

    if status:
        try:
            query = query.where(RFPDocument.status == RFPStatus(status))
        except ValueError:
            pass

    if client:
        safe_client = escape_like_pattern(client)
        query = query.where(RFPDocument.client_name.ilike(f"%{safe_client}%"))

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    rfps = result.scalars().all()

    return {
        "rfps": [
            {
                "id": str(rfp.id),
                "rfp_number": rfp.rfp_number,
                "client_name": rfp.client_name,
                "opportunity_title": rfp.opportunity_title,
                "status": rfp.status.value,
                "source": rfp.source.value,
                "submission_deadline": str(rfp.submission_deadline) if rfp.submission_deadline else None,
                "created_at": rfp.created_at.isoformat(),
                "recommendation": rfp.quick_scan_recommendation,
            }
            for rfp in rfps
        ],
        "count": len(rfps),
        "offset": offset,
        "limit": limit,
    }


@router.get("/upcoming-deadlines")
async def get_upcoming_deadlines(
    days: int = 14,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get RFPs with submission deadlines in the next N days.
    """
    now = datetime.utcnow()
    cutoff = now + timedelta(days=days)

    # Multi-tenancy: filter by organization
    org_filter = RFPDocument.organization_id == current_user.organization if current_user.organization else True

    result = await db.execute(
        select(RFPDocument)
        .where(org_filter)
        .where(RFPDocument.submission_deadline >= now)
        .where(RFPDocument.submission_deadline <= cutoff)
        .where(RFPDocument.status.not_in([RFPStatus.GO, RFPStatus.NO_GO]))
        .order_by(RFPDocument.submission_deadline)
    )
    rfps = result.scalars().all()

    return {
        "upcoming": [
            {
                "id": str(rfp.id),
                "rfp_number": rfp.rfp_number,
                "client_name": rfp.client_name,
                "opportunity_title": rfp.opportunity_title,
                "submission_deadline": rfp.submission_deadline.isoformat(),
                "days_remaining": (rfp.submission_deadline - now).days,
                "status": rfp.status.value,
            }
            for rfp in rfps
        ],
        "count": len(rfps),
    }

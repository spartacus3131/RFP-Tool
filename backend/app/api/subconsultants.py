"""
Sub-Consultants API - Manage partner registry and matching.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.models.database import get_db
from app.models.subconsultant import SubConsultant, SubConsultantTier, CapacityStatus
from app.models.user import User
from app.auth import get_current_active_user


router = APIRouter()


def escape_like_pattern(value: str) -> str:
    """Escape special characters for LIKE/ILIKE queries to prevent injection."""
    # Escape %, _, and \ which are special in LIKE patterns
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def verify_subconsultant_access(sub: SubConsultant, user: User) -> bool:
    """Verify user has access to sub-consultant based on organization."""
    if user.is_superuser:
        return True
    if not sub.organization_id:
        return True
    if not user.organization:
        return True
    return sub.organization_id == user.organization


class SubConsultantCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    discipline: str = Field(..., min_length=1, max_length=100)
    tier: str = Field(default="tier_1", pattern="^tier_[12]$")
    primary_contact_name: Optional[str] = Field(None, max_length=255)
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = Field(None, max_length=50)
    past_joint_projects: int = Field(default=0, ge=0, le=10000)
    win_rate_together: Optional[float] = Field(None, ge=0, le=100)
    typical_fee_range_low: Optional[int] = Field(None, ge=0, le=100000000)
    typical_fee_range_high: Optional[int] = Field(None, ge=0, le=100000000)
    notes: Optional[str] = Field(None, max_length=5000)
    preferred_project_types: Optional[List[str]] = Field(None, max_length=20)

    @field_validator('company_name', 'discipline', 'primary_contact_name', mode='before')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class SubConsultantResponse(BaseModel):
    id: str
    company_name: str
    discipline: str
    tier: str
    primary_contact_name: Optional[str]
    primary_contact_email: Optional[str]
    primary_contact_phone: Optional[str]
    past_joint_projects: int
    win_rate_together: Optional[float]
    typical_fee_range_low: Optional[int]
    typical_fee_range_high: Optional[int]
    capacity_status: str
    notes: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SubConsultantResponse])
async def list_subconsultants(
    discipline: Optional[str] = None,
    tier: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all sub-consultants, optionally filtered by discipline or tier."""
    # Multi-tenancy: filter by organization
    org_filter = SubConsultant.organization_id == current_user.organization if current_user.organization else True
    query = select(SubConsultant).where(org_filter)

    if discipline:
        safe_discipline = escape_like_pattern(discipline)
        query = query.where(SubConsultant.discipline.ilike(f"%{safe_discipline}%"))
    if tier:
        query = query.where(SubConsultant.tier == SubConsultantTier(tier))

    result = await db.execute(query)
    subs = result.scalars().all()

    return [
        SubConsultantResponse(
            id=str(sub.id),
            company_name=sub.company_name,
            discipline=sub.discipline,
            tier=sub.tier.value,
            primary_contact_name=sub.primary_contact_name,
            primary_contact_email=sub.primary_contact_email,
            primary_contact_phone=sub.primary_contact_phone,
            past_joint_projects=sub.past_joint_projects,
            win_rate_together=sub.win_rate_together,
            typical_fee_range_low=sub.typical_fee_range_low,
            typical_fee_range_high=sub.typical_fee_range_high,
            capacity_status=sub.capacity_status.value,
            notes=sub.notes,
        )
        for sub in subs
    ]


@router.post("/", response_model=SubConsultantResponse)
@limiter.limit("30/minute")
async def create_subconsultant(
    request: Request,
    sub: SubConsultantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a new sub-consultant to the registry."""
    subconsultant = SubConsultant(
        company_name=sub.company_name,
        discipline=sub.discipline,
        tier=SubConsultantTier(sub.tier),
        primary_contact_name=sub.primary_contact_name,
        primary_contact_email=sub.primary_contact_email,
        primary_contact_phone=sub.primary_contact_phone,
        past_joint_projects=sub.past_joint_projects,
        win_rate_together=sub.win_rate_together,
        typical_fee_range_low=sub.typical_fee_range_low,
        typical_fee_range_high=sub.typical_fee_range_high,
        notes=sub.notes,
        preferred_project_types=sub.preferred_project_types,
        # Multi-tenancy: link to user's organization
        organization_id=current_user.organization,
    )

    db.add(subconsultant)
    await db.commit()
    await db.refresh(subconsultant)

    return SubConsultantResponse(
        id=str(subconsultant.id),
        company_name=subconsultant.company_name,
        discipline=subconsultant.discipline,
        tier=subconsultant.tier.value,
        primary_contact_name=subconsultant.primary_contact_name,
        primary_contact_email=subconsultant.primary_contact_email,
        primary_contact_phone=subconsultant.primary_contact_phone,
        past_joint_projects=subconsultant.past_joint_projects,
        win_rate_together=subconsultant.win_rate_together,
        typical_fee_range_low=subconsultant.typical_fee_range_low,
        typical_fee_range_high=subconsultant.typical_fee_range_high,
        capacity_status=subconsultant.capacity_status.value,
        notes=subconsultant.notes,
    )


@router.get("/match")
async def match_subconsultants(
    disciplines: str,  # Comma-separated list
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Find matching sub-consultants for given disciplines.

    Returns Tier 1 and Tier 2 partners for each discipline.
    """
    # Multi-tenancy: filter by organization
    org_filter = SubConsultant.organization_id == current_user.organization if current_user.organization else True

    discipline_list = [d.strip() for d in disciplines.split(",")]
    results = {}

    for disc in discipline_list:
        safe_disc = escape_like_pattern(disc)
        query = select(SubConsultant).where(
            org_filter,
            SubConsultant.discipline.ilike(f"%{safe_disc}%")
        ).order_by(SubConsultant.tier, SubConsultant.win_rate_together.desc())

        result = await db.execute(query)
        subs = result.scalars().all()

        tier_1 = [s for s in subs if s.tier == SubConsultantTier.TIER_1]
        tier_2 = [s for s in subs if s.tier == SubConsultantTier.TIER_2]

        results[disc] = {
            "tier_1": [
                {
                    "id": str(s.id),
                    "company_name": s.company_name,
                    "contact_name": s.primary_contact_name,
                    "contact_email": s.primary_contact_email,
                    "contact_phone": s.primary_contact_phone,
                    "win_rate": s.win_rate_together,
                    "past_projects": s.past_joint_projects,
                    "capacity": s.capacity_status.value,
                }
                for s in tier_1
            ],
            "tier_2": [
                {
                    "id": str(s.id),
                    "company_name": s.company_name,
                    "contact_name": s.primary_contact_name,
                    "contact_email": s.primary_contact_email,
                    "win_rate": s.win_rate_together,
                    "capacity": s.capacity_status.value,
                }
                for s in tier_2
            ],
        }

    return results


@router.get("/{sub_id}", response_model=SubConsultantResponse)
async def get_subconsultant(
    sub_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single sub-consultant by ID."""
    result = await db.execute(select(SubConsultant).where(SubConsultant.id == sub_id))
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(404, "Sub-consultant not found")

    # Multi-tenancy: verify organization access
    if not verify_subconsultant_access(sub, current_user):
        raise HTTPException(403, "Access denied")

    return SubConsultantResponse(
        id=str(sub.id),
        company_name=sub.company_name,
        discipline=sub.discipline,
        tier=sub.tier.value,
        primary_contact_name=sub.primary_contact_name,
        primary_contact_email=sub.primary_contact_email,
        primary_contact_phone=sub.primary_contact_phone,
        past_joint_projects=sub.past_joint_projects,
        win_rate_together=sub.win_rate_together,
        typical_fee_range_low=sub.typical_fee_range_low,
        typical_fee_range_high=sub.typical_fee_range_high,
        capacity_status=sub.capacity_status.value,
        notes=sub.notes,
    )


@router.put("/{sub_id}", response_model=SubConsultantResponse)
async def update_subconsultant(
    sub_id: UUID,
    updates: SubConsultantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a sub-consultant."""
    result = await db.execute(select(SubConsultant).where(SubConsultant.id == sub_id))
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(404, "Sub-consultant not found")

    # Multi-tenancy: verify organization access
    if not verify_subconsultant_access(sub, current_user):
        raise HTTPException(403, "Access denied")

    sub.company_name = updates.company_name
    sub.discipline = updates.discipline
    sub.tier = SubConsultantTier(updates.tier)
    sub.primary_contact_name = updates.primary_contact_name
    sub.primary_contact_email = updates.primary_contact_email
    sub.primary_contact_phone = updates.primary_contact_phone
    sub.past_joint_projects = updates.past_joint_projects
    sub.win_rate_together = updates.win_rate_together
    sub.typical_fee_range_low = updates.typical_fee_range_low
    sub.typical_fee_range_high = updates.typical_fee_range_high
    sub.notes = updates.notes
    sub.preferred_project_types = updates.preferred_project_types

    await db.commit()
    await db.refresh(sub)

    return SubConsultantResponse(
        id=str(sub.id),
        company_name=sub.company_name,
        discipline=sub.discipline,
        tier=sub.tier.value,
        primary_contact_name=sub.primary_contact_name,
        primary_contact_email=sub.primary_contact_email,
        primary_contact_phone=sub.primary_contact_phone,
        past_joint_projects=sub.past_joint_projects,
        win_rate_together=sub.win_rate_together,
        typical_fee_range_low=sub.typical_fee_range_low,
        typical_fee_range_high=sub.typical_fee_range_high,
        capacity_status=sub.capacity_status.value,
        notes=sub.notes,
    )


@router.delete("/{sub_id}")
async def delete_subconsultant(
    sub_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a sub-consultant."""
    result = await db.execute(select(SubConsultant).where(SubConsultant.id == sub_id))
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(404, "Sub-consultant not found")

    # Multi-tenancy: verify organization access
    if not verify_subconsultant_access(sub, current_user):
        raise HTTPException(403, "Access denied")

    await db.delete(sub)
    await db.commit()

    return {"status": "deleted", "id": str(sub_id)}


@router.patch("/{sub_id}/capacity")
async def update_capacity(
    sub_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a sub-consultant's capacity status."""
    result = await db.execute(select(SubConsultant).where(SubConsultant.id == sub_id))
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(404, "Sub-consultant not found")

    # Multi-tenancy: verify organization access
    if not verify_subconsultant_access(sub, current_user):
        raise HTTPException(403, "Access denied")

    try:
        sub.capacity_status = CapacityStatus(status)
    except ValueError:
        raise HTTPException(400, f"Invalid status. Must be: {[s.value for s in CapacityStatus]}")

    await db.commit()
    return {"status": "updated", "capacity": status}

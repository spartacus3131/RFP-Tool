"""
Capital Budget API - Upload budgets, extract line items, match to RFPs.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional, List
from uuid import UUID
import uuid
import os
import aiofiles
import re
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.models.database import get_db
from app.models.user import User
from app.auth import get_current_active_user

# File upload security constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max
PDF_MAGIC = b'%PDF'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    filename = filename.lstrip('.')
    return filename if filename else 'unnamed'


def sanitize_path_component(value: str) -> str:
    """Sanitize a path component (like municipality name)."""
    # Remove any path separators and special characters
    value = re.sub(r'[^\w\-_ ]', '', value)
    value = value.strip()
    return value[:50] if value else 'unknown'


def escape_like_pattern(value: str) -> str:
    """Escape special characters for LIKE/ILIKE queries."""
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


from app.models.budget import CapitalBudget, BudgetLineItem


from app.services.pdf_extractor import extract_text_from_pdf
from app.services.budget_extractor import extract_budget_items, match_rfp_to_budget
from app.models.audit_log import AuditAction
from app.services.audit import log_action, get_client_ip, get_user_agent


def verify_budget_access(budget: CapitalBudget, user) -> bool:
    """Verify user has access to budget based on organization."""
    if user.is_superuser:
        return True
    if not budget.organization_id:
        return True
    if not user.organization:
        return True
    return budget.organization_id == user.organization


router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(f"{UPLOAD_DIR}/budgets", exist_ok=True)


class BudgetCreate(BaseModel):
    municipality: str
    fiscal_year: str


class BudgetResponse(BaseModel):
    id: str
    municipality: str
    fiscal_year: str
    filename: Optional[str]
    page_count: Optional[int]
    line_item_count: int

    class Config:
        from_attributes = True


class BudgetLineItemResponse(BaseModel):
    id: str
    project_name: str
    project_id: Optional[str]
    department: Optional[str]
    total_budget: Optional[float]
    description: Optional[str]
    source_page: Optional[int]


@router.post("/upload")
@limiter.limit("5/minute")
async def upload_budget(
    request: Request,
    file: UploadFile = File(...),
    municipality: str = Field(default="Unknown Municipality", max_length=255),
    fiscal_year: str = Field(default="2024", max_length=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a capital budget PDF for extraction.

    Extracts line items with project names, funding amounts, and descriptions
    for semantic matching to RFP scopes.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")

    # Validate file magic bytes (prevent fake extensions)
    if content[:4] != PDF_MAGIC:
        raise HTTPException(400, "File content does not match PDF format")

    # Sanitize all path components to prevent path traversal attacks
    safe_municipality = sanitize_path_component(municipality)
    safe_fiscal_year = sanitize_path_component(fiscal_year)
    safe_filename = sanitize_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_municipality}_{safe_fiscal_year}_{safe_filename}"

    # Build and validate file path
    budgets_dir = os.path.join(UPLOAD_DIR, "budgets")
    os.makedirs(budgets_dir, exist_ok=True)
    file_path = os.path.join(budgets_dir, unique_filename)

    # Verify path is within allowed directory
    abs_budgets_dir = os.path.abspath(budgets_dir)
    abs_file_path = os.path.abspath(file_path)
    if not abs_file_path.startswith(abs_budgets_dir):
        raise HTTPException(400, "Invalid file path")

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Extract text
    extraction_result = extract_text_from_pdf(file_path)
    
    if not extraction_result.success:
        raise HTTPException(500, f"Failed to extract text: {extraction_result.error}")

    # Create budget record (with multi-tenancy support)
    budget = CapitalBudget(
        municipality=municipality,
        fiscal_year=fiscal_year,
        filename=file.filename,
        file_path=file_path,
        raw_text=extraction_result.text,
        page_count=extraction_result.page_count,
        # Multi-tenancy: link to user's organization
        organization_id=current_user.organization,
    )
    
    db.add(budget)

    # Audit log: budget upload
    await log_action(
        db=db,
        action=AuditAction.UPLOAD,
        user_id=current_user.id,
        user_email=current_user.email,
        resource_type="budget",
        resource_id=str(budget.id),
        details={"filename": file.filename, "municipality": municipality, "fiscal_year": fiscal_year},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )

    await db.commit()
    await db.refresh(budget)

    return {
        "id": str(budget.id),
        "municipality": municipality,
        "fiscal_year": fiscal_year,
        "filename": file.filename,
        "page_count": extraction_result.page_count,
        "message": f"Budget uploaded. {extraction_result.page_count} pages extracted. Ready for line item extraction.",
    }


@router.post("/{budget_id}/extract")
@limiter.limit("10/minute")
async def extract_budget_line_items(
    request: Request,
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Extract line items from a budget using Claude AI.
    
    Parses the budget text to identify individual projects with
    funding amounts, descriptions, and justifications.
    """
    result = await db.execute(select(CapitalBudget).where(CapitalBudget.id == budget_id))
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(404, "Budget not found")

    # Multi-tenancy: verify organization access
    if not verify_budget_access(budget, current_user):
        raise HTTPException(403, "Access denied")

    if not budget.raw_text:
        raise HTTPException(400, "Budget has no extracted text")

    # Extract line items using Claude
    extraction_result = extract_budget_items(budget.raw_text, budget.municipality)
    
    if not extraction_result.success:
        return {
            "status": "error",
            "error": extraction_result.error,
        }

    # Store line items
    items_created = 0
    for item in extraction_result.items:
        line_item = BudgetLineItem(
            budget_id=budget.id,
            project_name=item.get("project_name", "Unknown"),
            project_id=item.get("project_id"),
            department=item.get("department"),
            total_budget=item.get("total_budget"),
            current_year_budget=item.get("current_year_budget"),
            funding_type=item.get("funding_type"),
            description=item.get("description"),
            justification=item.get("justification"),
            source_page=item.get("source_page"),
            source_text=item.get("source_text"),
        )
        db.add(line_item)
        items_created += 1

    await db.commit()

    return {
        "status": "success",
        "budget_id": str(budget.id),
        "items_extracted": items_created,
        "input_tokens": extraction_result.input_tokens,
        "output_tokens": extraction_result.output_tokens,
    }


@router.get("/", response_model=List[BudgetResponse])
async def list_budgets(
    municipality: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all capital budgets."""
    # Multi-tenancy: filter by organization
    org_filter = CapitalBudget.organization_id == current_user.organization if current_user.organization else True
    query = select(CapitalBudget).where(org_filter)

    if municipality:
        safe_municipality = escape_like_pattern(municipality)
        query = query.where(CapitalBudget.municipality.ilike(f"%{safe_municipality}%"))
    
    result = await db.execute(query)
    budgets = result.scalars().all()

    responses = []
    for b in budgets:
        # Count line items
        count_result = await db.execute(
            select(BudgetLineItem).where(BudgetLineItem.budget_id == b.id)
        )
        line_items = count_result.scalars().all()
        
        responses.append(BudgetResponse(
            id=str(b.id),
            municipality=b.municipality,
            fiscal_year=b.fiscal_year,
            filename=b.filename,
            page_count=b.page_count,
            line_item_count=len(line_items),
        ))
    
    return responses


@router.get("/{budget_id}/items", response_model=List[BudgetLineItemResponse])
async def get_budget_items(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all line items for a budget."""
    # First verify budget access
    budget_result = await db.execute(select(CapitalBudget).where(CapitalBudget.id == budget_id))
    budget = budget_result.scalar_one_or_none()

    if not budget:
        raise HTTPException(404, "Budget not found")

    # Multi-tenancy: verify organization access
    if not verify_budget_access(budget, current_user):
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(BudgetLineItem).where(BudgetLineItem.budget_id == budget_id)
    )
    items = result.scalars().all()
    
    return [
        BudgetLineItemResponse(
            id=str(item.id),
            project_name=item.project_name,
            project_id=item.project_id,
            department=item.department,
            total_budget=item.total_budget,
            description=item.description,
            source_page=item.source_page,
        )
        for item in items
    ]


@router.get("/match/{rfp_id}")
async def match_budget_to_rfp(
    rfp_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Find budget line items that match an RFP's scope.
    
    Uses semantic similarity to match the RFP scope summary
    to budget project descriptions.
    """
    from app.models.rfp import RFPDocument
    
    # Get RFP
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()
    
    if not rfp:
        raise HTTPException(404, "RFP not found")
    
    if not rfp.scope_summary and not rfp.client_name:
        raise HTTPException(400, "RFP needs scope summary or client name for matching")

    # Get all budget line items
    items_result = await db.execute(select(BudgetLineItem))
    all_items = items_result.scalars().all()
    
    if not all_items:
        return {"matches": [], "message": "No budget line items available for matching"}

    # Perform matching
    matches = match_rfp_to_budget(
        rfp_scope=rfp.scope_summary or "",
        rfp_client=rfp.client_name or "",
        rfp_title=rfp.opportunity_title or "",
        budget_items=all_items,
    )

    return {
        "rfp_id": str(rfp.id),
        "rfp_client": rfp.client_name,
        "matches": [
            {
                "budget_item_id": str(m["item"].id),
                "project_name": m["item"].project_name,
                "total_budget": m["item"].total_budget,
                "description": m["item"].description,
                "confidence": m["confidence"],
                "match_reason": m["reason"],
                "source_page": m["item"].source_page,
            }
            for m in matches[:5]  # Top 5 matches
        ],
    }

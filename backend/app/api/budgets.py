"""
Capital Budget API - Upload budgets, extract line items, match to RFPs.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional, List
from uuid import UUID
import os
import aiofiles

from app.models.database import get_db
from app.models.budget import CapitalBudget, BudgetLineItem
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.budget_extractor import extract_budget_items, match_rfp_to_budget


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
async def upload_budget(
    file: UploadFile = File(...),
    municipality: str = "Unknown Municipality",
    fiscal_year: str = "2024",
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a capital budget PDF for extraction.
    
    Extracts line items with project names, funding amounts, and descriptions
    for semantic matching to RFP scopes.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, "budgets", f"{municipality}_{fiscal_year}_{file.filename}")
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Extract text
    extraction_result = extract_text_from_pdf(file_path)
    
    if not extraction_result.success:
        raise HTTPException(500, f"Failed to extract text: {extraction_result.error}")

    # Create budget record
    budget = CapitalBudget(
        municipality=municipality,
        fiscal_year=fiscal_year,
        filename=file.filename,
        file_path=file_path,
        raw_text=extraction_result.text,
        page_count=extraction_result.page_count,
    )
    
    db.add(budget)
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
async def extract_budget_line_items(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
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
):
    """List all capital budgets."""
    query = select(CapitalBudget)
    
    if municipality:
        query = query.where(CapitalBudget.municipality.ilike(f"%{municipality}%"))
    
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
):
    """Get all line items for a budget."""
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

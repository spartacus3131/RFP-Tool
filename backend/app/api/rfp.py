"""
RFP API - Upload PDFs, manage RFPs, record decisions.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
import os
import aiofiles

from app.models.database import get_db
from app.models.rfp import RFPDocument, RFPStatus, RFPSource


router = APIRouter()

# File storage path
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class RFPResponse(BaseModel):
    id: str
    status: str
    source: str
    rfp_number: Optional[str]
    client_name: Optional[str]
    opportunity_title: Optional[str]
    submission_deadline: Optional[str]
    quick_scan_recommendation: Optional[str]

    class Config:
        from_attributes = True


class RFPDecisionRequest(BaseModel):
    decision: str  # "go" or "no_go"
    notes: Optional[str] = None


@router.post("/upload")
async def upload_rfp(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an RFP PDF for deep analysis.

    Returns the RFP ID for tracking extraction progress.
    """
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{file.filename}")
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Create RFP record
    rfp = RFPDocument(
        source=RFPSource.PDF_UPLOAD,
        filename=file.filename,
        file_path=file_path,
        status=RFPStatus.NEW,
    )

    db.add(rfp)
    await db.commit()
    await db.refresh(rfp)

    # TODO: Trigger async extraction job

    return {
        "id": str(rfp.id),
        "filename": file.filename,
        "status": rfp.status.value,
        "message": "Upload successful. Extraction will begin shortly.",
    }


@router.get("/{rfp_id}", response_model=RFPResponse)
async def get_rfp(
    rfp_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get RFP details by ID."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    return RFPResponse(
        id=str(rfp.id),
        status=rfp.status.value,
        source=rfp.source.value,
        rfp_number=rfp.rfp_number,
        client_name=rfp.client_name,
        opportunity_title=rfp.opportunity_title,
        submission_deadline=str(rfp.submission_deadline) if rfp.submission_deadline else None,
        quick_scan_recommendation=rfp.quick_scan_recommendation,
    )


@router.patch("/{rfp_id}")
async def update_rfp(
    rfp_id: UUID,
    updates: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update RFP fields (for human-in-the-loop editing)."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Apply allowed updates
    allowed_fields = [
        "client_name", "opportunity_title", "scope_summary",
        "rfp_number", "decision_notes",
    ]
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(rfp, field, value)

    await db.commit()
    return {"status": "updated", "id": str(rfp.id)}


@router.post("/{rfp_id}/decide")
async def record_decision(
    rfp_id: UUID,
    decision: RFPDecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record go/no-go decision for an RFP."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    if decision.decision not in ["go", "no_go"]:
        raise HTTPException(400, "Decision must be 'go' or 'no_go'")

    rfp.status = RFPStatus.GO if decision.decision == "go" else RFPStatus.NO_GO
    rfp.decision_notes = decision.notes

    await db.commit()
    return {
        "status": "decision_recorded",
        "id": str(rfp.id),
        "decision": decision.decision,
    }


@router.get("/{rfp_id}/evidence/{field_name}")
async def get_field_evidence(
    rfp_id: UUID,
    field_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get source evidence for a specific extracted field."""
    # TODO: Implement extraction evidence lookup
    return {
        "rfp_id": str(rfp_id),
        "field_name": field_name,
        "message": "Evidence lookup not yet implemented",
    }

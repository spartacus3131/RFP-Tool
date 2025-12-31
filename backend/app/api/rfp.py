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
from app.models.rfp import RFPDocument, RFPStatus, RFPSource, Extraction
from app.services.pdf_extractor import extract_text_from_pdf
from app.llm.client import extract_rfp_fields, parse_extraction_to_fields


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
    page_count: Optional[int] = None
    has_raw_text: bool = False
    extraction_error: Optional[str] = None

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

    # Extract text from PDF
    extraction_result = None
    if file.filename.lower().endswith(".pdf"):
        extraction_result = extract_text_from_pdf(file_path)

    # Create RFP record
    rfp = RFPDocument(
        source=RFPSource.PDF_UPLOAD,
        filename=file.filename,
        file_path=file_path,
        status=RFPStatus.PROCESSING if extraction_result and extraction_result.success else RFPStatus.NEW,
        raw_text=extraction_result.text if extraction_result and extraction_result.success else None,
        page_count=extraction_result.page_count if extraction_result else None,
        extraction_error=extraction_result.error if extraction_result and not extraction_result.success else None,
    )

    db.add(rfp)
    await db.commit()
    await db.refresh(rfp)

    # Build response
    response = {
        "id": str(rfp.id),
        "filename": file.filename,
        "status": rfp.status.value,
    }

    if extraction_result and extraction_result.success:
        response["message"] = f"Upload successful. Extracted text from {extraction_result.page_count} pages."
        response["page_count"] = extraction_result.page_count
        response["text_length"] = len(extraction_result.text) if extraction_result.text else 0
    elif extraction_result and not extraction_result.success:
        response["message"] = f"Upload successful but text extraction failed: {extraction_result.error}"
        response["extraction_error"] = extraction_result.error
    else:
        response["message"] = "Upload successful. DOCX extraction not yet implemented."

    return response


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
        page_count=rfp.page_count,
        has_raw_text=rfp.raw_text is not None and len(rfp.raw_text) > 0,
        extraction_error=rfp.extraction_error,
    )


@router.get("/{rfp_id}/detail")
async def get_rfp_detail(
    rfp_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full RFP details with all extractions for review UI."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Get all extractions
    extractions_result = await db.execute(
        select(Extraction).where(Extraction.rfp_id == rfp_id)
    )
    extractions = extractions_result.scalars().all()

    return {
        "id": str(rfp.id),
        "status": rfp.status.value,
        "source": rfp.source.value,
        "filename": rfp.filename,
        "created_at": rfp.created_at.isoformat() if rfp.created_at else None,
        "page_count": rfp.page_count,
        "has_raw_text": rfp.raw_text is not None and len(rfp.raw_text) > 0,

        # Extracted fields
        "fields": {
            "client_name": rfp.client_name,
            "rfp_number": rfp.rfp_number,
            "opportunity_title": rfp.opportunity_title,
            "scope_summary": rfp.scope_summary,
            "published_date": str(rfp.published_date) if rfp.published_date else None,
            "question_deadline": rfp.question_deadline.isoformat() if rfp.question_deadline else None,
            "submission_deadline": rfp.submission_deadline.isoformat() if rfp.submission_deadline else None,
            "contract_duration": rfp.contract_duration,
            "required_internal_disciplines": rfp.required_internal_disciplines,
            "required_external_disciplines": rfp.required_external_disciplines,
            "evaluation_criteria": rfp.evaluation_criteria,
            "reference_requirements": rfp.reference_requirements,
            "insurance_requirements": rfp.insurance_requirements,
            "risk_flags": rfp.risk_flags,
        },

        # Source linking data
        "extractions": [
            {
                "field_name": e.field_name,
                "value": e.extracted_value,
                "source_page": e.source_page,
                "source_text": e.source_text,
                "confidence": e.confidence,
                "verified": e.verified_by is not None,
            }
            for e in extractions
        ],

        # Decision info
        "decision_notes": rfp.decision_notes,
        "quick_scan_recommendation": rfp.quick_scan_recommendation,
    }


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
    result = await db.execute(
        select(Extraction).where(
            Extraction.rfp_id == rfp_id,
            Extraction.field_name == field_name
        )
    )
    extraction = result.scalar_one_or_none()

    if not extraction:
        raise HTTPException(404, f"No extraction found for field '{field_name}'")

    return {
        "rfp_id": str(rfp_id),
        "field_name": field_name,
        "value": extraction.extracted_value,
        "source_page": extraction.source_page,
        "source_text": extraction.source_text,
        "confidence": extraction.confidence,
        "verified": extraction.verified_by is not None,
    }


@router.post("/{rfp_id}/extract")
async def extract_rfp_fields_endpoint(
    rfp_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Claude AI extraction on an uploaded RFP.

    Extracts structured fields from the raw PDF text and stores
    them with source linking for human verification.
    """
    # Get RFP
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    if not rfp.raw_text:
        raise HTTPException(400, "RFP has no extracted text. Upload a PDF first.")

    # Run Claude extraction
    extraction_result = extract_rfp_fields(rfp.raw_text)

    if not extraction_result.success:
        return {
            "status": "error",
            "error": extraction_result.error,
            "id": str(rfp.id),
        }

    # Parse and store field values
    field_values = parse_extraction_to_fields(extraction_result.data)

    # Update RFP document with extracted values
    for field, value in field_values.items():
        if hasattr(rfp, field) and value is not None:
            setattr(rfp, field, value)

    # Store individual extractions with source linking
    for field_name, field_data in extraction_result.data.items():
        if not isinstance(field_data, dict) or "value" not in field_data:
            continue

        value = field_data.get("value")
        if value is None:
            continue

        # Convert complex values to string for storage
        if isinstance(value, (dict, list)):
            import json
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        extraction = Extraction(
            rfp_id=rfp.id,
            field_name=field_name,
            extracted_value=value_str,
            source_page=field_data.get("source_page"),
            source_text=field_data.get("source_text"),
            confidence=0.9,  # Default high confidence for Claude extractions
        )
        db.add(extraction)

    # Update status
    rfp.status = RFPStatus.EXTRACTED

    await db.commit()
    await db.refresh(rfp)

    return {
        "status": "success",
        "id": str(rfp.id),
        "fields_extracted": len(field_values),
        "input_tokens": extraction_result.input_tokens,
        "output_tokens": extraction_result.output_tokens,
        "extracted_fields": {
            "client_name": rfp.client_name,
            "rfp_number": rfp.rfp_number,
            "opportunity_title": rfp.opportunity_title,
            "submission_deadline": str(rfp.submission_deadline) if rfp.submission_deadline else None,
            "scope_summary": rfp.scope_summary[:200] + "..." if rfp.scope_summary and len(rfp.scope_summary) > 200 else rfp.scope_summary,
            "required_internal_disciplines": rfp.required_internal_disciplines,
            "required_external_disciplines": rfp.required_external_disciplines,
        }
    }

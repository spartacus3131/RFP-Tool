"""
RFP API - Upload PDFs, manage RFPs, record decisions.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
import uuid
import os
import aiofiles
import re

from datetime import datetime

# File upload security constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
# PDF magic bytes (first 4 bytes of PDF files)
PDF_MAGIC = b'%PDF'
# DOCX files are ZIP archives
DOCX_MAGIC = b'PK\x03\x04'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    # Get just the filename, strip any path components
    filename = os.path.basename(filename)
    # Remove any non-alphanumeric characters except dots, hyphens, underscores
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    # Prevent hidden files
    filename = filename.lstrip('.')
    return filename if filename else 'unnamed'


def generate_safe_filepath(upload_dir: str, original_filename: str, prefix: str = "") -> tuple[str, str]:
    """Generate a safe file path using UUID prefix.

    Returns:
        Tuple of (safe_filename, full_path)
    """
    safe_name = sanitize_filename(original_filename)
    unique_filename = f"{prefix}{uuid.uuid4().hex[:8]}_{safe_name}"
    file_path = os.path.join(upload_dir, unique_filename)

    # Validate path is within upload directory (prevent path traversal)
    abs_upload_dir = os.path.abspath(upload_dir)
    abs_file_path = os.path.abspath(file_path)
    if not abs_file_path.startswith(abs_upload_dir):
        raise ValueError("Invalid file path")

    return unique_filename, file_path


def validate_file_magic(content: bytes, filename: str) -> bool:
    """Validate file content matches expected type based on magic bytes."""
    ext = os.path.splitext(filename.lower())[1]

    if ext == ".pdf":
        return content[:4] == PDF_MAGIC
    elif ext == ".docx":
        return content[:4] == DOCX_MAGIC
    return False


from app.models.database import get_db
from app.models.rfp import RFPDocument, RFPStatus, RFPSource, Extraction, Contradiction, ContradictionType
from app.models.user import User
from app.models.audit_log import AuditAction
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.audit import log_action, get_client_ip, get_user_agent
from app.llm.client import extract_rfp_fields, parse_extraction_to_fields, detect_contradictions
from app.auth import get_current_active_user


router = APIRouter()


def verify_organization_access(rfp: RFPDocument, user: User) -> bool:
    """
    Verify user has access to RFP based on organization.

    Returns True if:
    - User is a superuser (admin)
    - RFP has no organization (legacy data)
    - User has no organization (unrestricted access for now)
    - User's organization matches RFP's organization
    """
    if user.is_superuser:
        return True
    if not rfp.organization_id:
        return True
    if not user.organization:
        return True
    return rfp.organization_id == user.organization

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
    decision: str = Field(..., pattern="^(go|no_go)$")
    notes: Optional[str] = Field(None, max_length=5000)


class RFPUpdateRequest(BaseModel):
    """Validated model for RFP field updates."""
    client_name: Optional[str] = Field(None, max_length=500)
    opportunity_title: Optional[str] = Field(None, max_length=1000)
    scope_summary: Optional[str] = Field(None, max_length=50000)
    rfp_number: Optional[str] = Field(None, max_length=100)
    decision_notes: Optional[str] = Field(None, max_length=5000)

    @field_validator('client_name', 'opportunity_title', 'rfp_number', mode='before')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


@router.post("/upload")
@limiter.limit("5/minute")
async def upload_rfp(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload an RFP PDF for deep analysis.

    Returns the RFP ID for tracking extraction progress.
    """
    # Validate file extension
    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")

    # Validate file magic bytes (prevent fake extensions)
    if not validate_file_magic(content, file.filename):
        raise HTTPException(400, "File content does not match expected format")

    # Generate safe file path (prevents path traversal attacks)
    try:
        safe_filename, file_path = generate_safe_filepath(UPLOAD_DIR, file.filename)
    except ValueError:
        raise HTTPException(400, "Invalid filename")

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Extract text from PDF
    extraction_result = None
    if file.filename.lower().endswith(".pdf"):
        extraction_result = extract_text_from_pdf(file_path)

    # Create RFP record (with multi-tenancy support)
    rfp = RFPDocument(
        source=RFPSource.PDF_UPLOAD,
        filename=file.filename,
        file_path=file_path,
        status=RFPStatus.PROCESSING if extraction_result and extraction_result.success else RFPStatus.NEW,
        raw_text=extraction_result.text if extraction_result and extraction_result.success else None,
        page_count=extraction_result.page_count if extraction_result else None,
        extraction_error=extraction_result.error if extraction_result and not extraction_result.success else None,
        # Multi-tenancy: link to user's organization
        organization_id=current_user.organization,
        created_by_id=current_user.id,
    )

    db.add(rfp)

    # Audit log: file upload
    await log_action(
        db=db,
        action=AuditAction.UPLOAD,
        user_id=current_user.id,
        user_email=current_user.email,
        resource_type="rfp",
        resource_id=str(rfp.id),
        details={"filename": file.filename, "page_count": rfp.page_count},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )

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
    current_user: User = Depends(get_current_active_user),
):
    """Get RFP details by ID."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

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
    current_user: User = Depends(get_current_active_user),
):
    """Get full RFP details with all extractions for review UI."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

    # Get all extractions
    extractions_result = await db.execute(
        select(Extraction).where(Extraction.rfp_id == rfp_id)
    )
    extractions = extractions_result.scalars().all()

    # Get all contradictions
    contradictions_result = await db.execute(
        select(Contradiction).where(Contradiction.rfp_id == rfp_id)
    )
    contradictions = contradictions_result.scalars().all()

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

        # Contradictions
        "contradictions": [
            {
                "id": str(c.id),
                "type": c.contradiction_type.value,
                "description": c.description,
                "statement_a": c.statement_a,
                "statement_a_page": c.statement_a_page,
                "statement_b": c.statement_b,
                "statement_b_page": c.statement_b_page,
                "clarifying_question": c.clarifying_question,
                "is_helpful": c.is_helpful,
                "feedback_at": c.feedback_at.isoformat() if c.feedback_at else None,
            }
            for c in contradictions
        ],

        # Decision info
        "decision_notes": rfp.decision_notes,
        "quick_scan_recommendation": rfp.quick_scan_recommendation,
    }


@router.patch("/{rfp_id}")
async def update_rfp(
    rfp_id: UUID,
    updates: RFPUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update RFP fields (for human-in-the-loop editing)."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

    # Apply validated updates (only fields that were provided)
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rfp, field, value)

    await db.commit()
    return {"status": "updated", "id": str(rfp.id)}


@router.post("/{rfp_id}/decide")
async def record_decision(
    request: Request,
    rfp_id: UUID,
    decision: RFPDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record go/no-go decision for an RFP."""
    result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

    # Decision is validated by Pydantic pattern constraint
    rfp.status = RFPStatus.GO if decision.decision == "go" else RFPStatus.NO_GO
    rfp.decision_notes = decision.notes

    # Audit log: decision
    await log_action(
        db=db,
        action=AuditAction.DECISION,
        user_id=current_user.id,
        user_email=current_user.email,
        resource_type="rfp",
        resource_id=str(rfp.id),
        details={"decision": decision.decision, "client_name": rfp.client_name},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )

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
    current_user: User = Depends(get_current_active_user),
):
    """Get source evidence for a specific extracted field."""
    # First verify RFP access
    rfp_result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = rfp_result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

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
@limiter.limit("10/minute")
async def extract_rfp_fields_endpoint(
    request: Request,
    rfp_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

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

    # Run contradiction detection
    contradiction_result = detect_contradictions(rfp.raw_text)
    contradictions_found = 0

    if contradiction_result.success:
        for c in contradiction_result.contradictions:
            # Map type string to enum
            c_type = c.get("type", "scope").lower()
            if c_type == "numerical":
                contradiction_type = ContradictionType.NUMERICAL
            elif c_type == "timeline":
                contradiction_type = ContradictionType.TIMELINE
            else:
                contradiction_type = ContradictionType.SCOPE

            contradiction = Contradiction(
                rfp_id=rfp.id,
                contradiction_type=contradiction_type,
                description=c.get("description", ""),
                statement_a=c.get("statement_a", {}).get("text", ""),
                statement_a_page=c.get("statement_a", {}).get("page"),
                statement_b=c.get("statement_b", {}).get("text", ""),
                statement_b_page=c.get("statement_b", {}).get("page"),
                clarifying_question=c.get("clarifying_question", ""),
            )
            db.add(contradiction)
            contradictions_found += 1

    # Audit log: extraction
    await log_action(
        db=db,
        action=AuditAction.EXTRACT,
        user_id=current_user.id,
        user_email=current_user.email,
        resource_type="rfp",
        resource_id=str(rfp.id),
        details={
            "fields_extracted": len(field_values),
            "contradictions_found": contradictions_found,
            "input_tokens": extraction_result.input_tokens,
            "output_tokens": extraction_result.output_tokens,
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )

    await db.commit()
    await db.refresh(rfp)

    return {
        "status": "success",
        "id": str(rfp.id),
        "fields_extracted": len(field_values),
        "contradictions_found": contradictions_found,
        "input_tokens": extraction_result.input_tokens + contradiction_result.input_tokens,
        "output_tokens": extraction_result.output_tokens + contradiction_result.output_tokens,
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


class ContradictionFeedbackRequest(BaseModel):
    is_helpful: bool


@router.post("/{rfp_id}/contradictions/{contradiction_id}/feedback")
async def submit_contradiction_feedback(
    rfp_id: UUID,
    contradiction_id: UUID,
    feedback: ContradictionFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit user feedback on whether a contradiction was helpful."""
    # Verify RFP exists
    rfp_result = await db.execute(select(RFPDocument).where(RFPDocument.id == rfp_id))
    rfp = rfp_result.scalar_one_or_none()

    if not rfp:
        raise HTTPException(404, "RFP not found")

    # Multi-tenancy: verify organization access
    if not verify_organization_access(rfp, current_user):
        raise HTTPException(403, "Access denied")

    # Get contradiction
    result = await db.execute(
        select(Contradiction).where(
            Contradiction.id == contradiction_id,
            Contradiction.rfp_id == rfp_id
        )
    )
    contradiction = result.scalar_one_or_none()

    if not contradiction:
        raise HTTPException(404, "Contradiction not found")

    # Update feedback
    contradiction.is_helpful = feedback.is_helpful
    contradiction.feedback_at = datetime.utcnow()

    await db.commit()

    return {
        "status": "feedback_recorded",
        "contradiction_id": str(contradiction_id),
        "is_helpful": feedback.is_helpful,
    }

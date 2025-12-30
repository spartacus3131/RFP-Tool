"""
Quick Scan API - paste a bidsandtenders.ca URL to get instant triage.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.models.database import get_db
from app.models.rfp import RFPDocument, RFPSource, RFPStatus
from app.services.scraper import scraper, QuickScanResult


router = APIRouter()


class QuickScanRequest(BaseModel):
    url: HttpUrl


class QuickScanResponse(BaseModel):
    # Status
    success: bool
    error: Optional[str] = None

    # Core fields
    rfp_number: Optional[str] = None
    client_name: Optional[str] = None
    opportunity_title: Optional[str] = None

    # Dates
    published_date: Optional[str] = None
    question_deadline: Optional[str] = None
    submission_deadline: Optional[str] = None
    contract_duration: Optional[str] = None

    # Details
    scope_summary: Optional[str] = None
    category: Optional[str] = None
    eligibility_notes: Optional[str] = None
    trade_agreements: Optional[str] = None

    # Recommendation
    recommendation: Optional[str] = None
    recommendation_reasons: Optional[list[str]] = None

    # Meta
    source_url: str
    scraped_at: datetime
    rfp_id: Optional[str] = None  # If saved to database


@router.post("/", response_model=QuickScanResponse)
async def quick_scan(
    request: QuickScanRequest,
    db: AsyncSession = Depends(get_db),
    save: bool = True,
):
    """
    Quick scan an RFP listing URL to extract key details.

    Paste a bidsandtenders.ca URL to get:
    - Client name, RFP number, title
    - Key dates (published, questions due, submission deadline)
    - Category and eligibility notes
    - GO/MAYBE/NO_GO recommendation

    Set save=false to scan without saving to database.
    """
    url = str(request.url)

    # Check if supported
    if not scraper.is_supported_url(url):
        return QuickScanResponse(
            success=False,
            error="Unsupported URL. Currently supports: bidsandtenders.ca domains",
            source_url=url,
            scraped_at=datetime.utcnow(),
        )

    # Scrape the listing
    result: QuickScanResult = await scraper.scrape(url)

    # Build response
    response = QuickScanResponse(
        success=result.error is None,
        error=result.error,
        rfp_number=result.rfp_number,
        client_name=result.client_name,
        opportunity_title=result.opportunity_title,
        published_date=result.published_date,
        question_deadline=result.question_deadline,
        submission_deadline=result.submission_deadline,
        contract_duration=result.contract_duration,
        scope_summary=result.scope_summary,
        category=result.category,
        eligibility_notes=result.eligibility_notes,
        trade_agreements=result.trade_agreements,
        recommendation=result.recommendation,
        recommendation_reasons=result.recommendation_reasons,
        source_url=url,
        scraped_at=result.scraped_at,
    )

    # Optionally save to database
    if save and result.error is None:
        rfp = RFPDocument(
            source=RFPSource.QUICK_SCAN,
            source_url=url,
            status=RFPStatus.EXTRACTED,
            rfp_number=result.rfp_number,
            client_name=result.client_name,
            opportunity_title=result.opportunity_title,
            scope_summary=result.scope_summary,
            category=result.category,
            eligibility_notes=result.eligibility_notes,
            contract_duration=result.contract_duration,
            quick_scan_recommendation=result.recommendation,
        )

        # Parse dates if possible
        # (In production, would use dateutil.parser for flexible parsing)

        db.add(rfp)
        await db.commit()
        await db.refresh(rfp)
        response.rfp_id = str(rfp.id)

    return response


@router.get("/supported-domains")
async def get_supported_domains():
    """Get list of supported scraping domains."""
    return {
        "domains": scraper.SUPPORTED_DOMAINS,
        "note": "Paste any RFP listing URL from these domains",
    }

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RFP Intelligence Platform - a tool for mid-sized consulting firms (15-150 employees) to streamline go/no-go decisions on RFPs. The platform extracts structured data from RFP PDFs, matches required disciplines to sub-consultant pools, and provides evidence-based pursuit recommendations with full source traceability.

**Target Market:** AEC (Architecture, Engineering, Construction), legal, management consulting, IT services firms in Canada.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Stack                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Frontend │  │ Backend  │  │    PostgreSQL    │  │
│  │ (React)  │  │ (FastAPI)│  │   + pgvector     │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │     LLM API           │
           │  (Claude / OpenAI)    │
           └───────────────────────┘
```

## Tech Stack

- **Frontend:** React + TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL + pgvector
- **PDF Processing:** PyMuPDF
- **LLM:** Claude API (primary)
- **Deployment:** Docker Compose (self-hosted priority)

## Key Commands

```bash
# Development
docker-compose up -d              # Start all services
docker-compose logs -f backend    # Tail backend logs
docker-compose down               # Stop all services

# Backend only
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend only
cd frontend
npm install
npm run dev

# Database
docker-compose exec db psql -U postgres -d rfp_tool

# Run tests
cd backend && pytest
cd frontend && npm test
```

## Project Structure

```
/backend
  /app
    /api          # FastAPI route handlers
    /models       # SQLAlchemy models
    /services     # Business logic (extraction, matching)
    /llm          # LLM integration (prompts, parsing)
  main.py         # FastAPI app entry
  requirements.txt

/frontend
  /src
    /components   # React components
    /pages        # Page-level components
    /hooks        # Custom React hooks
    /api          # API client functions
  package.json

/docker
  docker-compose.yml
  Dockerfile.backend
  Dockerfile.frontend

/docs
  PLAN.md         # Full build plan and specifications
```

## Core Domain Concepts

### RFP Document
The central entity. Contains:
- Extracted fields (client, dates, scope, disciplines, requirements)
- Source linking (every extraction maps to PDF page/bbox)
- Decision status (pending, go, no_go)

### Sub-Consultant
External partners organized by discipline and tier:
- **Tier 1:** Primary partners (2-3 per discipline)
- **Tier 2:** Backup options
- Track: past projects, win rate, fee range, capacity

### Extraction
Links extracted data to source:
- `field_name`: What was extracted
- `source_page`: PDF page number
- `source_text`: Exact text from PDF
- `source_bbox`: Coordinates for highlighting
- `confidence`: AI confidence score
- `verified_by`: User who confirmed/edited

## Critical Requirements

### Source of Truth
Every AI extraction MUST link to the exact PDF location. Users must be able to click any extracted field and see the highlighted source text. This is the #1 trust factor.

### Human-in-the-Loop
AI provides suggestions, humans verify and decide. All extractions should be editable with audit trail. Never auto-commit decisions.

### Self-Hosted First
Primary deployment is Docker on customer infrastructure. Data sovereignty is a real concern for this market. Design with self-hosted as the default.

## API Patterns

```python
# Extraction endpoint pattern
@router.get("/rfp/{rfp_id}/evidence/{field_name}")
async def get_field_evidence(rfp_id: UUID, field_name: str):
    """Return the source PDF excerpt for a specific extracted field"""
    # Returns: {source_text, page, bbox, confidence}

# Sub-consultant matching
@router.get("/subconsultants/match")
async def match_subconsultants(disciplines: List[str]):
    """Given required disciplines, return matching sub-consultants by tier"""
    # Returns: {discipline: {tier_1: [...], tier_2: [...]}}
```

## LLM Integration Notes

- Use Claude API for extraction (best for long documents)
- Prompts should request structured JSON output
- Always include source page/location in extraction requests
- Handle rate limits gracefully
- Consider customer-owned LLM endpoints (Azure OpenAI) for enterprise

## Testing Priorities

1. PDF extraction accuracy on real RFPs
2. Source linking correctness (bbox coordinates)
3. Sub-consultant matching logic
4. API endpoint contracts
5. Docker deployment end-to-end

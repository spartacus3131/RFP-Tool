# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RFP Intelligence Platform - a tool for mid-sized consulting firms (15-150 employees) to streamline go/no-go decisions on RFPs. The platform extracts structured data from RFP PDFs, matches required disciplines to sub-consultant pools, and provides evidence-based pursuit recommendations with full source traceability.

**Target Market:** AEC (Architecture, Engineering, Construction), legal, management consulting, IT services firms in Canada.

## Project State

### Current Workflow Phase
- [x] Sprint 1: Foundation + Quick Scan
  - [x] Docker Compose stack setup
  - [x] Database schema (PostgreSQL + pgvector)
  - [x] Quick Scan from bidsandtenders.ca URL
  - [x] Basic React UI with routing
  - [x] PDF text extraction with PyMuPDF
- [x] Sprint 2: LLM Extraction
- [x] Sprint 3: Sub-Consultant Matching
- [x] Sprint 4: Go/No-Go Scoring Engine
- [x] Sprint 5: Review UI + Evidence Panel
- [x] Sprint 6: Fuzzy Budget Matching
- [x] Sprint 7: Testing & Hardening
  - [x] Multi-tenancy implementation
  - [x] Audit logging expansion
  - [x] Password complexity requirements
  - [x] Database migrations (Alembic)
  - [x] Security test suite (15 tests)
  - [x] Production infrastructure (Nginx + Docker Compose)
  - [x] Security headers middleware

**Current Phase:** V1 MVP Complete - Production-Ready (January 11, 2026)
**Next Milestone:** Deploy to production, verify security features with real database

### Key Decisions & Context

#### Idea & Validation
- **Core Idea**: RFP intelligence platform that reduces go/no-go decision time from 8-12 hours to under 1 hour
- **Target Audience**: Mid-sized AEC consulting firms (15-150 employees) in Ontario, Canada
- **Validation Approach**: Primary interview with Sam (environmental consulting), synthesized with research from Claude, Gemini, Perplexity, ChatGPT
- **Key Insight**: Firms pay per-bid ($138) or annual ($461) for RFP document access. Quick triage before download provides immediate value.

#### Research Insights
- Go/no-go decisions cost $750-1,000+ per RFP in senior time (3 people × 1hr × $250/hr)
- Firms have 2-3 preferred subs per discipline (Tier 1), not massive databases
- Data sovereignty is non-negotiable for this market (self-hosted deployment required)
- Source linking is #1 trust factor (every extraction must link to PDF location)
- Corporate vs. team references is critical distinction in RFP evaluation

#### Creative Strategy
- **Positioning**: Not "proposal management software" but "RFP intelligence + pursuit decisioning platform"
- **Key Differentiator**: Fuzzy budget matching (connect RFP to client's capital budget line items)
- **Workflow**: Two-phase approach - Quick Scan (triage) → Deep Scan (full PDF analysis)
- **Philosophy**: Human-in-the-loop (AI suggests, humans decide)

#### Production Decisions
- **Tech Stack**: FastAPI (Python) + React (TypeScript) + PostgreSQL + pgvector
- **Deployment**: Docker Compose for self-hosted deployment (data sovereignty requirement)
- **LLM**: Claude API for extraction (best for long documents)
- **Database**: PostgreSQL with pgvector (keeps relational + vector search in one DB)
- **PDF Processing**: PyMuPDF (open source, handles most PDFs)
- **Security**: Multi-tenancy via organization_id, comprehensive audit logging, Alembic migrations
- **Testing**: pytest with async support, 15-test security suite

### Working Instructions

#### Current Focus
Production deployment preparation and security verification:
1. Run Alembic migration against development database
2. Test multi-tenancy isolation with multiple organizations
3. Verify audit logging captures all mutations
4. Test production Docker Compose stack with Nginx
5. Document security features and deployment process

#### Relevant Workflow Prompts
- When running migrations: Use `alembic upgrade head` to apply all migrations
- When testing multi-tenancy: Create users in different organizations, verify data isolation
- When deploying: Use production Docker Compose with Nginx reverse proxy
- When auditing: Check audit_logs table for all create/update/delete actions
- When testing security: Run `pytest backend/tests/test_security.py` to verify all 15 tests pass

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

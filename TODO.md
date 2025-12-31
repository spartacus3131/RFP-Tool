# TODO - RFP Intelligence Platform

## Completed Sprints

### Sprint 1: Foundation + Quick Scan ✓
- [x] Docker Compose stack (Frontend, Backend, PostgreSQL + pgvector)
- [x] Quick Scan from bidsandtenders.ca URL
- [x] PDF upload with PyMuPDF text extraction
- [x] Store raw_text, page_count in database

### Sprint 2: LLM Extraction ✓
- [x] Claude API integration (Sonnet model)
- [x] Structured extraction prompts with source linking
- [x] Extract: client_name, rfp_number, dates, scope, disciplines, evaluation criteria, risk flags
- [x] `/api/rfp/{id}/extract` endpoint
- [x] Tested with real 222-page RFP (Ministry of Transportation Ontario)

### Sprint 3: Human-in-the-Loop Review UI ✓
- [x] RFPDetail page with extracted fields display
- [x] Source page linking (click field to see source page)
- [x] GO/NO-GO decision buttons with notes
- [x] `/api/rfp/{id}/detail` endpoint for full extractions
- [x] Route navigation from RFP list

### Sprint 4: Sub-Consultant Matching ✓
- [x] SubConsultant model with discipline and tier
- [x] `/api/subconsultants/match` endpoint
- [x] Seeded 6 sample sub-consultants
- [x] Sub-consultant cards in RFP detail view
- [x] Match by extracted external disciplines

### Sprint 5: Fuzzy Budget Matching ✓
- [x] CapitalBudget and BudgetLineItem models
- [x] Budget PDF upload and text extraction
- [x] Claude-powered budget line item extraction
- [x] Keyword + semantic matching (SequenceMatcher)
- [x] `/api/budgets/match/{rfp_id}` endpoint
- [x] Budget match UI in RFP detail page

## Current: Sprint 6 - Dashboard & Polish

### Dashboard Enhancements
- [ ] Stats cards (total RFPs, GO/NO-GO counts, pending decisions)
- [ ] Key dates timeline (submissions due this week/month)
- [ ] Filter by status, client, discipline
- [ ] Quick stats visualization

### Export Functionality
- [ ] Export RFP summary as PDF
- [ ] Export to Excel (extractions + decisions)

### Compliance Checker
- [ ] Define compliance requirements (insurance, WSIB, licenses)
- [ ] Check RFP requirements against firm capabilities
- [ ] Display PASS/FAIL checklist

### Polish
- [ ] Error handling improvements
- [ ] Loading states throughout UI
- [ ] Empty state designs
- [ ] Mobile responsiveness

## Sprint 7: Testing & Hardening (Future)

### End-to-End Testing
- [ ] Test with 5-10 diverse RFPs
- [ ] Measure extraction accuracy
- [ ] Performance benchmarking (large PDFs)

### Security & Documentation
- [ ] Security review (input validation, API auth)
- [ ] User documentation
- [ ] Deployment guide

## Architecture Summary

```
Docker Compose Stack:
├── Frontend (React + TypeScript) - port 5173
├── Backend (FastAPI + Python) - port 8000
└── Database (PostgreSQL + pgvector) - port 5432

Key Files:
├── backend/
│   ├── app/api/           # FastAPI route handlers
│   ├── app/models/        # SQLAlchemy models
│   ├── app/services/      # Business logic
│   └── app/llm/           # Claude API integration
└── frontend/
    ├── src/pages/         # Page components
    └── src/api/client.ts  # API client
```

## Running the Project

```bash
# Start all services
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose -f docker/docker-compose.yml logs -f backend

# Rebuild after changes
docker compose -f docker/docker-compose.yml up -d --build

# Access
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## API Endpoints

### RFP
- `POST /api/rfp/upload` - Upload RFP PDF
- `GET /api/rfp/{id}` - Get RFP summary
- `GET /api/rfp/{id}/detail` - Get RFP with all extractions
- `POST /api/rfp/{id}/extract` - Run Claude extraction
- `POST /api/rfp/{id}/decide` - Record GO/NO-GO decision

### Budgets
- `POST /api/budgets/upload` - Upload budget PDF
- `POST /api/budgets/{id}/extract` - Extract line items
- `GET /api/budgets/match/{rfp_id}` - Match RFP to budget items

### Sub-Consultants
- `GET /api/subconsultants/` - List all
- `GET /api/subconsultants/match?disciplines=X,Y` - Match by discipline

### Dashboard
- `GET /api/dashboard/` - Stats
- `GET /api/dashboard/rfps` - List RFPs with filters

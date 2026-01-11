# RFP Intelligence Platform

An AI-powered platform that transforms the go/no-go decision process for mid-sized consulting firms. Extract structured data from RFP documents, match required disciplines to sub-consultant pools, and make evidence-based pursuit decisions—all with full source traceability.

## Current Status: Production-Ready with Security Hardening

### What's Built (January 11, 2026)

**Core Features:**
- **Quick Scan**: Paste a bidsandtenders.ca URL for instant RFP triage (GO/MAYBE/NO-GO)
- **PDF Upload & Extraction**: Upload RFP PDFs, extract text with PyMuPDF
- **Claude AI Integration**: Structured extraction of 11+ fields with source page linking
- **Human Review UI**: Side-by-side view of extractions with GO/NO-GO decisions
- **Sub-Consultant Matching**: Match RFP disciplines to your partner registry
- **Budget Matching**: Fuzzy match RFPs to capital budget line items
- **Dashboard**: Stats, upcoming deadlines, recent RFPs, quick actions

**Infrastructure:**
- Docker Compose stack (frontend, backend, PostgreSQL + pgvector)
- Toast notifications for user feedback
- Filter controls on RFP list (status, client search)

**Security Features (NEW):**
- Multi-tenancy with organization-level data isolation
- Comprehensive audit logging for compliance
- Password complexity requirements (8+ chars, uppercase, lowercase, number, special char)
- Security headers middleware (XSS, clickjacking, MIME sniffing protection)
- Database migrations with Alembic
- Production-ready Nginx configuration with rate limiting
- 15-test security test suite (all passing)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Anthropic API key (for Claude AI extraction)

### Setup

1. **Clone and configure:**
```bash
git clone <repository>
cd RFP-Tool

# Create .env file in project root
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/rfp_tool
ANTHROPIC_API_KEY=your-api-key-here
UPLOAD_DIR=./uploads
EOF
```

2. **Start the platform:**
```bash
docker compose -f docker/docker-compose.yml up -d
```

3. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Common Commands

```bash
# View logs
docker compose -f docker/docker-compose.yml logs -f backend

# Rebuild after code changes
docker compose -f docker/docker-compose.yml up -d --build

# Stop all services
docker compose -f docker/docker-compose.yml down

# Reset database (warning: deletes all data)
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d
```

## Features Guide

### 1. Quick Scan (Triage)
Paste a bidsandtenders.ca URL to get key details before downloading the full RFP:
- Client name, RFP number, deadlines
- Scope summary, categories
- GO/MAYBE/NO-GO recommendation

### 2. PDF Upload & AI Extraction
Upload RFP PDFs for deep analysis:
1. Go to RFPs page, click "Upload PDF"
2. Click on the uploaded RFP
3. Click "Extract with Claude" to run AI extraction
4. Review extracted fields with source page links

**Extracted Fields:**
- Client name and contact
- RFP number, dates (published, questions, submission)
- Scope summary (AI-generated)
- Required internal/external disciplines
- Evaluation criteria and weights
- Risk flags (insurance, bonding, payment terms)

### 3. Sub-Consultant Management
Manage your partner registry at `/sub-consultants`:
- Add/Edit/Delete sub-consultants
- Organize by discipline and tier (Tier 1 = preferred, Tier 2 = backup)
- Track win rates and past projects
- Auto-match to RFP requirements

### 4. Budget Matching
Upload client capital budgets to match RFP scope to funded projects:
```bash
# Upload via API
curl -X POST "http://localhost:8000/api/budgets/upload?municipality=City%20Name&fiscal_year=2025" \
  -F "file=@budget.pdf"

# Extract line items
curl -X POST "http://localhost:8000/api/budgets/{budget_id}/extract"
```

### 5. GO/NO-GO Decisions
On any RFP detail page:
- Review all extracted fields
- See matched sub-consultants
- View budget matches (if available)
- Click GO or NO-GO to record decision with notes

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + Tailwind CSS + Vite |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.x (async) |
| Database | PostgreSQL 16 + pgvector |
| AI | Claude API (Sonnet model) |
| PDF | PyMuPDF |
| Deployment | Docker Compose |

## Project Structure

```
RFP-Tool/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   │   ├── rfp.py
│   │   │   ├── dashboard.py
│   │   │   ├── subconsultants.py
│   │   │   ├── budgets.py
│   │   │   └── quick_scan.py
│   │   ├── models/        # SQLAlchemy models
│   │   │   ├── rfp.py
│   │   │   ├── subconsultant.py
│   │   │   └── budget.py
│   │   ├── services/      # Business logic
│   │   │   ├── pdf_extractor.py
│   │   │   └── budget_extractor.py
│   │   └── llm/           # Claude API integration
│   │       ├── client.py
│   │       └── prompts.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable UI components
│   │   └── api/           # API client
│   └── package.json
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── .env                   # Environment variables (create this)
├── PLAN.md               # Full product specification
├── TODO.md               # Current tasks and progress
└── CLAUDE.md             # AI coding context
```

## API Reference

### RFP Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rfp/upload` | Upload RFP PDF |
| GET | `/api/rfp/{id}` | Get RFP summary |
| GET | `/api/rfp/{id}/detail` | Get RFP with all extractions |
| POST | `/api/rfp/{id}/extract` | Run Claude AI extraction |
| POST | `/api/rfp/{id}/decide` | Record GO/NO-GO decision |

### Dashboard Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/` | Get stats and recent RFPs |
| GET | `/api/dashboard/rfps` | List RFPs with filters |
| GET | `/api/dashboard/upcoming-deadlines` | Get upcoming submission deadlines |

### Sub-Consultant Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subconsultants/` | List all sub-consultants |
| POST | `/api/subconsultants/` | Create sub-consultant |
| PUT | `/api/subconsultants/{id}` | Update sub-consultant |
| DELETE | `/api/subconsultants/{id}` | Delete sub-consultant |
| GET | `/api/subconsultants/match` | Match by disciplines |

### Budget Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/budgets/upload` | Upload capital budget PDF |
| POST | `/api/budgets/{id}/extract` | Extract line items with AI |
| GET | `/api/budgets/match/{rfp_id}` | Match RFP to budget items |

## Key Design Decisions

1. **Self-Hosted First**: Target market requires data sovereignty. Docker Compose is the primary deployment model.
2. **Source of Truth**: Every AI extraction links to the exact PDF page. Users can verify all suggestions.
3. **Human-in-the-Loop**: AI provides suggestions, humans verify and decide. No auto-commit of decisions.
4. **Two-Phase Workflow**: Quick Scan (triage) then Deep Scan (full PDF analysis).

## Target Market

Mid-sized consulting firms (15-150 employees) in:
- Architecture, Engineering, Construction (AEC)
- Legal services
- Management consulting
- IT services

**Primary Geography**: Ontario, Canada

## Development

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Run backend tests
cd backend && pytest

# Run frontend tests
cd frontend && npm test
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
Ensure your `.env` file exists in the project root with a valid API key.

### "Connection refused" errors
Make sure all Docker containers are running:
```bash
docker compose -f docker/docker-compose.yml ps
```

### PDF extraction fails
Check the backend logs for specific errors:
```bash
docker compose -f docker/docker-compose.yml logs backend
```

## License

Proprietary - All Rights Reserved

# RFP Intelligence Platform

An AI-powered platform that transforms the go/no-go decision process for mid-sized consulting firms. Extract structured data from RFP documents, match required disciplines to sub-consultant pools, and make evidence-based pursuit decisions—all with full source traceability.

## Current Status: Sprint 1 - MVP Foundation

### What's Built (December 30, 2024)

- **Quick Scan Feature**: Paste a bidsandtenders.ca URL to get instant RFP triage (GO/MAYBE/NO-GO recommendations)
- **Full Stack Architecture**: FastAPI backend, React frontend, PostgreSQL + pgvector database
- **Docker Deployment**: Self-hosted three-container stack (frontend, backend, database)
- **Database Models**: RFP and Sub-Consultant entities with SQLAlchemy 2.x
- **PDF Upload Scaffold**: UI and endpoint ready for PDF processing

### Running the Platform

```bash
# Start all services
cd docker
docker-compose up -d

# Access the application
Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy 2.x
- **Database**: PostgreSQL 15 + pgvector
- **Deployment**: Docker Compose (self-hosted first)
- **PDF Processing**: PyMuPDF (planned for Sprint 2)
- **LLM**: Claude API integration (planned for Sprint 2)

## Features Roadmap

### Sprint 1: Foundation + Quick Scan (CURRENT)
- [x] Docker Compose stack
- [x] Database models (RFP, Sub-Consultant)
- [x] Quick Scan from bidsandtenders.ca URL
- [x] Basic React UI with routing
- [ ] PDF text extraction with PyMuPDF

### Sprint 2: LLM Extraction (NEXT)
- [ ] Claude API integration
- [ ] Structured data extraction from PDFs
- [ ] Source linking (extractions → PDF page/location)
- [ ] Frontend display of AI-extracted fields

### Sprint 3: Sub-Consultant Matching
- [ ] Discipline taxonomy
- [ ] Matching algorithm (RFP disciplines → sub pool)
- [ ] Sub-consultant CRUD interface

### Sprint 4: Go/No-Go Scoring Engine
- [ ] Six-factor scoring framework
- [ ] Editable weights and decision logic
- [ ] Score visualization

### Sprint 5: Review UI + Evidence Panel
- [ ] Side-by-side view (extractions | PDF viewer)
- [ ] Click-to-source highlighting
- [ ] Edit/verify interface with audit trail

### Sprint 6: Fuzzy Budget Matching
- [ ] Capital budget PDF parsing
- [ ] Vector-based semantic matching
- [ ] Budget context display

### Sprint 7: Polish + Export
- [ ] Dashboard with stats and filters
- [ ] Export to PDF/Excel
- [ ] Documentation and deployment guides

## Key Design Decisions

1. **Self-Hosted First**: Target market requires data sovereignty. Docker Compose is the primary deployment model.
2. **Source of Truth**: Every AI extraction links to the exact PDF location. Users must be able to verify all suggestions.
3. **Human-in-the-Loop**: AI provides suggestions, humans verify and decide. No auto-commit of decisions.
4. **Two-Phase Workflow**: Quick Scan (triage) → Deep Scan (full PDF analysis). Prevents wasted spend on document downloads.

## Target Market

Mid-sized consulting firms (15-150 employees) in:
- Architecture, Engineering, Construction (AEC)
- Legal services
- Management consulting
- IT services

**Primary Geography**: Ontario, Canada (expanding to other provinces)

## Project Structure

```
/backend          FastAPI application
  /app
    /api          Route handlers
    /models       SQLAlchemy models
    /services     Business logic
    /llm          LLM integration (Sprint 2)
  main.py         App entry point
  requirements.txt

/frontend         React application
  /src
    /components   Reusable components
    /pages        Page-level components
    /services     API client
  package.json

/docker           Docker configuration
  docker-compose.yml
  Dockerfile.backend
  Dockerfile.frontend

PLAN.md           Full product specification
CLAUDE.md         AI context and patterns
```

## Documentation

- **PLAN.md**: Complete product vision, architecture, and 7-sprint roadmap
- **CLAUDE.md**: AI coding context (architecture, patterns, key commands)
- **RFP-Tool-session-summary.md**: Session-by-session development history

## Contributing

This is a private project in active development. See `TODO.md` for next steps.

## License

Proprietary - All Rights Reserved

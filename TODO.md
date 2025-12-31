# TODO - RFP Intelligence Platform

## Status: V1 MVP Complete (Dec 31, 2024)

All 7 sprints completed. Platform is feature-complete and ready for deployment.

---

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

### Sprint 3: Human-in-the-Loop Review UI ✓
- [x] RFPDetail page with extracted fields display
- [x] Source page linking (click field to see source page)
- [x] GO/NO-GO decision buttons with notes
- [x] `/api/rfp/{id}/detail` endpoint

### Sprint 4: Sub-Consultant Matching ✓
- [x] SubConsultant model with discipline and tier
- [x] `/api/subconsultants/match` endpoint
- [x] Sub-consultant cards in RFP detail view
- [x] Full CRUD UI (create/edit/delete)

### Sprint 5: Fuzzy Budget Matching ✓
- [x] CapitalBudget and BudgetLineItem models
- [x] Budget PDF upload and text extraction
- [x] Claude-powered budget line item extraction
- [x] Keyword + semantic matching
- [x] Budget match UI in RFP detail page

### Sprint 6: Dashboard & Polish ✓
- [x] Stats cards (Total, GO, NO-GO, Pending, Sub-consultants)
- [x] GO Rate panel with breakdown
- [x] Upcoming deadlines timeline (next 14 days)
- [x] RFP filters (status dropdown, client search)
- [x] Quick link cards

### Sprint 7: Testing & Hardening ✓
- [x] Toast notification system
- [x] Error handling on mutations
- [x] README with full documentation
- [x] Git commit and push to GitHub

---

## Remaining Tasks (Post-V1)

### Deployment
- [ ] Deploy to Railway (or other hosting)
  - PostgreSQL database service
  - Backend service with env vars
  - Frontend service
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificates

### Future Enhancements (V2)
- [ ] PDF viewer with highlighted source text
- [ ] Export RFP summary to PDF/Excel
- [ ] Compliance checker (insurance, WSIB, licenses)
- [ ] GO/NO-GO scoring framework with weighted factors
- [ ] User authentication (Auth0 or Keycloak)
- [ ] Budget upload UI (currently API-only)
- [ ] Email notifications for upcoming deadlines

### Technical Debt
- [ ] Add unit tests (pytest for backend, vitest for frontend)
- [ ] Add E2E tests (Playwright)
- [ ] Performance optimization for large PDFs (>300 pages)
- [ ] Rate limiting on API endpoints
- [ ] Input sanitization review

---

## Quick Reference

### Running Locally
```bash
docker compose -f docker/docker-compose.yml up -d
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

### GitHub Repo
https://github.com/spartacus3131/RFP-Tool

### Key Files
- `README.md` - Setup and feature documentation
- `PLAN.md` - Full product specification
- `CLAUDE.md` - AI coding context

# TODO - Next Session

## Immediate Next Steps

### Sprint 1 Completion
- [ ] Add PyMuPDF to requirements.txt
- [ ] Implement PDF text extraction in `/api/rfp/upload` endpoint
  - Extract text from all pages
  - Store in `rfps.raw_text` field
  - Return extraction status (success/failed + page count)
- [ ] Test PDF upload → text extraction with a real RFP document
- [ ] Update frontend Upload page to show extraction status

### Sprint 2 Kickoff (Claude API Integration)
- [ ] Set up Claude API credentials in `.env`
- [ ] Create `/backend/app/llm/prompts.py` for structured extraction prompts
- [ ] Create `/backend/app/llm/client.py` for Claude API client
- [ ] Implement extraction endpoint: `POST /api/rfp/{id}/extract`
  - Send PDF text + extraction prompt to Claude
  - Parse JSON response
  - Store extractions with source linking
- [ ] Create Extraction model in database
  - `field_name`, `extracted_value`, `confidence`, `source_page`, `source_text`, `source_bbox`
- [ ] Test with 2-3 real RFP documents (50-200 pages each)

## Questions to Answer

### Technical Decisions
1. **Claude API tier**: Should we use Opus (more accurate, slower, expensive) or Sonnet (faster, cheaper) for extraction?
   - Consider: Opus for complex RFPs (>100 pages), Sonnet for simple ones?

2. **Text extraction strategy**: Extract full PDF upfront or page-by-page on demand?
   - Upfront: Better for LLM context, but storage intensive
   - On-demand: Less storage, but slower LLM calls

3. **Scanned PDFs**: How do we handle RFPs that are scanned images (no text layer)?
   - PyMuPDF alone won't work - need OCR (Tesseract? Azure CV?)
   - Should we support this in Sprint 2 or defer to later?

### Product Decisions
1. **Extraction fields priority**: Which fields should we extract first?
   - Suggested: Client name, submission deadline, scope summary, required disciplines
   - Or: All fields from PLAN.md at once?

2. **Confidence thresholds**: What confidence score qualifies an extraction as "verified"?
   - Low confidence → require human review
   - High confidence → auto-approve?
   - Or: Always require human review in V1?

## Dependencies/Blockers

### External Dependencies
- **Claude API Key**: Need to create Anthropic account and get API key
  - URL: https://console.anthropic.com/
  - Estimated cost: ~$0.50-2.00 per RFP extraction (depending on length and model)

### Data Dependencies
- **Real RFP Documents**: Need 5-10 sample RFPs for testing
  - Source: bidsandtenders.ca (can download from Quick Scan results)
  - Range: Mix of simple (20-page) and complex (150-page) documents
  - Variety: Different municipalities, project types

### None Blocking
- No current blockers preventing Sprint 2 work

## Context for Next Session

### Where We Left Off
Sprint 1 is 95% complete. All three Docker containers are running successfully:
- Frontend (React) on port 5173
- Backend (FastAPI) on port 8000
- Database (PostgreSQL + pgvector) on port 5432

Quick Scan feature is fully functional and tested with Durham Region RFP from bidsandtenders.ca.

PDF upload UI exists, but the backend endpoint only saves the file - it doesn't extract text yet.

### Why We Made Key Decisions

**Docker Compose for deployment**: Target market (AEC consulting) requires self-hosted deployment due to data sovereignty concerns. Cloud-only SaaS would be a non-starter.

**Two-phase workflow (Quick Scan → Deep Scan)**: Firms pay per-bid to download RFP documents. Quick triage from listing page prevents wasted spend on obvious NO-GOs before paying for full document.

**PostgreSQL + pgvector**: Keeps relational data (RFPs, sub-consultants) and vector search (fuzzy budget matching) in one database. Simpler operations than separate vector DB.

**SQLAlchemy 2.x**: Future-proof choice, but requires `text()` wrapper for raw SQL (learned this when creating pgvector extension).

### What to Tackle First

**Priority 1**: Complete PDF text extraction with PyMuPDF
- This unblocks Sprint 2 (can't send text to Claude API without extracting it first)
- Should take 1-2 hours max
- Test with at least one real RFP to confirm it works

**Priority 2**: Set up Claude API integration
- Create account, get API key, add to `.env`
- Write structured extraction prompt
- Test with simple RFP first (20-30 pages)

**Priority 3**: Implement source linking foundation
- This is the #1 trust factor - users must see where extractions came from
- Start simple: just `source_page` field in Sprint 2
- Add `source_bbox` for click-to-highlight in Sprint 5

## Testing Plan

### Sprint 1 Completion Test
1. Upload a real RFP PDF (50+ pages)
2. Verify text extraction completes without errors
3. Check database for `raw_text` populated
4. Confirm page count matches PDF

### Sprint 2 Integration Test
1. Upload RFP → extract text → send to Claude
2. Verify Claude returns structured JSON
3. Check extractions stored in database with source pages
4. Display extractions in frontend with "AI-suggested" badges
5. Calculate extraction accuracy on known fields (dates, client name)

### Success Criteria
- Extract text from 100-page PDF in < 30 seconds
- Claude API returns structured data in < 60 seconds
- Extraction accuracy > 90% on key fields (client, dates, scope)
- Source page numbers map correctly to PDF

## Future Session Reminders

### Code Quality Checks Before Commit
- [ ] No `console.log` or `print()` debugging statements
- [ ] No hardcoded API keys or credentials
- [ ] Type hints on Python functions
- [ ] TypeScript strict mode errors resolved
- [ ] Docker containers still build and run

### Documentation to Update
- [ ] Update this TODO.md with new tasks
- [ ] Append to RFP-Tool-session-summary.md with session notes
- [ ] Update CLAUDE.md "Current Workflow Phase" checkboxes
- [ ] Update README.md "Current Status" section if sprint changes

### Git Workflow
- Commit message format: `Sprint X: [Feature Name] - Brief description`
- Always include "What changed" and "Why" in commit body
- Reference TODO.md tasks in commit messages

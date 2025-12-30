# RFP Intelligence Platform - Build Plan

## Executive Summary

Build an RFP intelligence platform that transforms the go/no-go decision process for mid-sized consulting firms (15-150 employees) in Canada's AEC, legal, management consulting, and IT services sectors. The platform extracts structured data from RFP documents, provides evidence-based pursuit recommendations, and matches required disciplines to sub-consultant pools—all with full source traceability and human-in-the-loop controls.

**Core Value Proposition:** Reduce go/no-go decision time from 8-12 hours to under 1 hour per RFP while improving pursuit quality through structured scoring and evidence-based recommendations.

**Target Pricing:** $1,500-3,000 CAD/month ($18k-36k/year)

**ROI Story:** At $750+ saved per RFP in senior time alone, the platform pays for itself in 2-4 RFPs per month.

---

## Problem Statement

### The Current Pain

Mid-sized consulting firms receive dozens of RFPs annually. Each RFP triggers a resource-intensive evaluation process:

1. **Manual Reading** (Day 1-3): 3 senior staff each spend 30-60 minutes reading a 50-200 page PDF
2. **Discussion** (Day 3-5): Go/no-go call scheduled, additional hours spent debating merits
3. **Sub-consultant Scramble** (Day 5-7): "Oh shit, we need a geotech sub" - scrambling to engage partners
4. **Proposal Development** (Day 7-21): If GO, another 25-34 hours of effort begins

**Economic Impact:**
- Go/no-go decision alone: $750-1,000+ per RFP (3 people × 1hr × $250/hr)
- 30 RFPs/year = $22,500-30,000/year just in decision overhead
- Bad pursuits waste even more (full proposal effort on low-probability bids)

### Why Existing Tools Don't Solve This

| Tool Type | What They Do | What They Miss |
|-----------|--------------|----------------|
| Loopio, QorusDocs | Content reuse, templates, collaboration | No go/no-go scoring, no sub matching, no evidence linking |
| Ontopical | Lead discovery | No RFP analysis or pursuit qualification |
| Citylitics | Predictive intel | No sub-consultant registry integration |

**The Gap:** No tool provides extraction → scoring → sub-matching → evidence trail in one workflow.

---

## Product Vision

### Platform Positioning

**Not** "proposal management software"

**Is** "RFP intelligence + pursuit decisioning platform"

The platform is the operating system for strategic pursuits—connecting market signals, RFP analysis, relationship data, and team capacity into a unified decision engine.

### Three-Phase Roadmap

| Phase | Name | Focus | Value |
|-------|------|-------|-------|
| V1 | RFP Tool | Day 0 extraction + sub-consultant matching + **fuzzy budget matching** | Time savings + differentiator |
| V2 | Intelligence Feed | EA pipeline + go/no-go scoring framework | Revenue generation |
| V3 | Relationship Engine | CRM sync + touchpoint alerts + win/loss learning | Account protection |

---

## V1 MVP Specification

### Scope Definition

V1 delivers the "Day 0" value: when an RFP arrives, the platform immediately extracts key information, identifies required disciplines, and surfaces the sub-consultant pool—with full source traceability.

### Core Features

#### 1. RFP Document Upload & Parsing

**User Story:** As a proposal manager, I upload an RFP PDF and get a structured summary within minutes so I can make initial qualification decisions without reading 100+ pages.

**Extraction Fields:**
- Client name and contact information
- Opportunity title / project name
- Key dates:
  - RFP release date
  - Question submission deadline
  - Addendum periods
  - Proposal due date
- Scope summary (2-3 sentences, AI-generated)
- Required disciplines (internal capabilities needed)
- Required sub-consultants (external expertise needed)
- Mandatory qualifications (years of experience, certifications, licenses)
- Project reference requirements:
  - Corporate references vs. team references (critical distinction)
  - Number required, recency requirements
- Evaluation criteria:
  - Technical vs. financial weighting (e.g., 80/20 split)
  - Scoring rubric if provided
- Risk flags:
  - Insurance requirements
  - Bonding requirements
  - Payment terms / fee structure
  - Contractual risk indicators

**Source of Truth Requirement:**
Every extracted field must link to the specific page/section of the source PDF. Users click any field to see the highlighted original text.

#### 2. Sub-Consultant Matching

**User Story:** As a project manager, I see on Day 0 which external sub-consultants I need and have contact info for our preferred partners ready to engage.

**Data Model - Sub-Consultant Registry:**
```
Discipline:
  - name: "Geotechnical Engineering"
  - tier_1_partners: [
      {
        company: "ABC Geotech",
        contact_name: "John Smith",
        email: "john@abcgeo.com",
        phone: "416-555-1234",
        past_joint_projects: 12,
        win_rate_together: 0.67,
        typical_fee_range: "$15k-50k",
        notes: "Preferred for municipal work, responsive"
      },
      ...
    ]
  - tier_2_partners: [...]
```

**Matching Logic:**
1. Parse RFP scope for discipline keywords
2. Match against firm's discipline taxonomy
3. Flag internal vs. external requirements
4. For external: surface Tier 1 partners first, Tier 2 as backup
5. For large projects (fee > threshold): suggest early engagement + exclusivity discussion

**Common External Disciplines (AEC):**
- Geotechnical Engineering
- Topographic Survey
- Archaeological Assessment
- Hydrogeological Studies
- Environmental Site Assessment
- Traffic Engineering
- Structural Engineering
- Landscape Architecture

#### 3. Compliance Gatekeeper

**User Story:** As a proposal manager, I get an immediate pass/fail check on whether we meet mandatory requirements before investing time in evaluation.

**Compliance Checks:**
- [ ] Required licenses held by firm
- [ ] Required certifications (ISO, etc.)
- [ ] Insurance minimums met
- [ ] WSIB status current
- [ ] Geographic eligibility (if restricted)
- [ ] Conflict of interest check (prior involvement with client)

**Output:** Binary PASS/FAIL with specific failures highlighted and linked to RFP clause.

#### 4. Fuzzy Budget Matching (Key Differentiator)

**User Story:** As a proposal manager, I want to see if this RFP project appears in the client's capital budget, what the approved funding is, and what the budget justification says—so I understand the "backstory" and can speak to the client's real priorities.

**Why This Matters:**
- Competitors only summarize RFPs—they don't connect to funding context
- Budget line item names often don't match RFP titles (hence "fuzzy" matching)
- Example: "Reconstruction of 7th Line" (budget) → "Arterial Road Improvements" (RFP)
- Understanding budget justification helps craft winning proposals

**How It Works:**
1. Extract client name from RFP (e.g., "City of Brampton")
2. Search for client's published capital budget PDF online
3. Parse budget document for project line items
4. Use semantic/vector search to match RFP scope to budget line items
5. Display matched budget info alongside RFP extraction

**Data Extracted from Capital Budgets:**
- Project name/ID in budget
- Approved funding amount
- Funding type (Planning, Engineering/Design, Construction)
- Multi-year funding breakdown
- Project justification / rationale
- Department / service area

**Source of Truth Requirement:**
Show the matched budget PDF with highlighted line item. User can verify the match is correct or mark as "no match found."

**MVP Scope:**
- Support Ontario municipal capital budgets (most common format)
- Manual budget PDF upload initially (auto-fetch in V2)
- Semantic matching using vector embeddings
- Confidence score for matches

#### 5. Human-in-the-Loop Review Interface

**User Story:** As a senior reviewer, I can verify AI extractions, correct errors, add context, and approve the summary before it's shared with the team.

**Interface Requirements:**
- Side-by-side view: extracted data | original PDF
- Edit any extracted field with audit trail
- Add notes/context to any field
- Mark confidence level (AI-suggested vs. human-verified)
- Approve/reject extraction before sharing
- Export to standardized format (PDF summary, Excel, or integration)

#### 6. Project Dashboard

**User Story:** As a practice leader, I see all active RFP evaluations in one view with status and key dates.

**Dashboard Elements:**
- List of uploaded RFPs with status (New, In Review, GO, NO-GO)
- Key dates timeline (submissions due this week/month)
- Filter by discipline, client, status
- Quick stats: RFPs this month, GO rate, pending decisions

---

## Technical Architecture

### Deployment Model

**Primary:** Self-hosted Docker deployment (addresses data sovereignty concerns)
**Secondary:** Hosted SaaS option for less sensitive clients

```
┌─────────────────────────────────────────────────────────┐
│                    Client Environment                    │
│  ┌─────────────────────────────────────────────────────┐│
│  │              Docker Compose Stack                    ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  ││
│  │  │ Frontend │  │ Backend  │  │    PostgreSQL    │  ││
│  │  │ (React)  │  │ (FastAPI)│  │   + pgvector     │  ││
│  │  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  ││
│  │       │             │                  │            ││
│  │       └─────────────┼──────────────────┘            ││
│  │                     │                               ││
│  │              ┌──────┴──────┐                        ││
│  │              │ File Store  │                        ││
│  │              │ (Local Vol) │                        ││
│  │              └─────────────┘                        ││
│  └─────────────────────────────────────────────────────┘│
│                          │                               │
│                          ▼                               │
│              ┌───────────────────────┐                  │
│              │  LLM API (External)   │                  │
│              │  - Claude API         │                  │
│              │  - Azure OpenAI       │                  │
│              │  - Customer's choice  │                  │
│              └───────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack (Recommended)

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | React + TypeScript | Widely adopted, good PDF viewer libraries |
| **Backend** | Python + FastAPI | Best LLM ecosystem, fast async, easy Docker |
| **Database** | PostgreSQL + pgvector | Single DB for relational + vector search |
| **PDF Processing** | PyMuPDF + pdf2image | Open source, handles most PDFs |
| **LLM** | Claude API (default) | Best for long documents, structured extraction |
| **Vector Search** | pgvector | Keeps everything in one DB, simplifies ops |
| **Auth** | Auth0 or self-hosted Keycloak | Enterprise-ready, SSO support |
| **File Storage** | Local volume (self-hosted) or S3 | PDFs stay on customer infrastructure |

### Data Models

#### RFP Document
```python
class RFPDocument:
    id: UUID
    filename: str
    upload_date: datetime
    status: Enum["new", "processing", "extracted", "reviewed", "decided"]

    # Extracted fields
    client_name: str
    client_contact: dict  # {name, email, phone, role}
    opportunity_title: str

    # Key dates
    release_date: date
    question_deadline: date
    submission_deadline: date

    # Scope
    scope_summary: str  # AI-generated 2-3 sentences

    # Disciplines
    required_internal_disciplines: list[str]
    required_external_disciplines: list[str]

    # Requirements
    qualifications: list[QualificationRequirement]
    reference_requirements: ReferenceRequirement
    evaluation_criteria: EvaluationCriteria

    # Risk/Compliance
    insurance_requirements: dict
    payment_terms: str
    risk_flags: list[str]

    # Source linking
    extractions: list[Extraction]  # Each field linked to PDF location

    # Decision
    decision: Enum["pending", "go", "no_go"]
    decision_date: datetime
    decision_notes: str

class Extraction:
    field_name: str
    extracted_value: Any
    confidence: float
    source_page: int
    source_text: str  # The exact text from PDF
    source_bbox: tuple  # Bounding box for highlighting
    verified_by: UUID  # User who verified, if any
    verified_at: datetime
```

#### Sub-Consultant
```python
class SubConsultant:
    id: UUID
    company_name: str
    discipline: str
    tier: Enum["tier_1", "tier_2"]

    # Contact
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: str

    # Performance
    past_joint_projects: int
    win_rate_together: float

    # Commercial
    typical_fee_range_low: int
    typical_fee_range_high: int

    # Notes
    notes: str
    preferred_project_types: list[str]

    # Status
    current_capacity: Enum["available", "limited", "unavailable"]
    exclusivity_status: dict  # {rfp_id: "exclusive" | "non_exclusive"}
```

---

## API Design (V1)

### Endpoints

```
POST   /api/rfp/upload              # Upload RFP PDF
GET    /api/rfp/{id}                # Get RFP with extractions
PATCH  /api/rfp/{id}                # Update/verify extractions
POST   /api/rfp/{id}/decide         # Record go/no-go decision

GET    /api/rfp/{id}/evidence/{field}  # Get source evidence for field
GET    /api/rfp/{id}/pdf            # Stream original PDF
GET    /api/rfp/{id}/pdf/page/{n}   # Get specific page as image

GET    /api/subconsultants          # List all sub-consultants
POST   /api/subconsultants          # Add sub-consultant
GET    /api/subconsultants/match?disciplines=X,Y  # Get matches

GET    /api/dashboard               # Dashboard stats
GET    /api/rfps                    # List all RFPs with filters
```

---

## User Interface Wireframes

### Screen 1: RFP Upload
```
┌─────────────────────────────────────────────────────────┐
│  RFP Intelligence                          [+ New RFP]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │                                                 │   │
│   │     Drag & drop RFP document here              │   │
│   │              or click to browse                │   │
│   │                                                 │   │
│   │         Supported: PDF, DOCX                   │   │
│   │                                                 │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
│   Recent Uploads:                                       │
│   ┌─────────────────────────────────────────────────┐   │
│   │ City of Brampton - Water Main Replacement       │   │
│   │ Due: Jan 15, 2025  |  Status: In Review        │   │
│   └─────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────┐   │
│   │ Region of Peel - Transit Corridor Study         │   │
│   │ Due: Jan 22, 2025  |  Status: GO               │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Screen 2: RFP Analysis View (Human-in-the-Loop)
```
┌─────────────────────────────────────────────────────────────────────────┐
│  City of Brampton - Water Main Replacement RFP      [Approve] [Reject]  │
├────────────────────────────────┬────────────────────────────────────────┤
│  EXTRACTED DATA                │  SOURCE DOCUMENT                       │
│                                │                                        │
│  Client: City of Brampton [✓]  │  ┌────────────────────────────────┐   │
│  ───────────────────────────   │  │                                │   │
│  Contact: John Smith           │  │    [PDF Page 1 of 87]          │   │
│           jsmith@brampton.ca   │  │                                │   │
│                                │  │  ████████████████████████      │   │
│  KEY DATES                     │  │  ████████████████████████      │   │
│  ───────────────────────────   │  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      │   │
│  Questions Due: Jan 8 [✓]      │  │  ████████████████████████      │   │
│  Submission: Jan 15 [edit]     │  │                                │   │
│                                │  │  [Highlighted: "Proposals      │   │
│  SCOPE SUMMARY                 │  │   must be submitted by         │   │
│  ───────────────────────────   │  │   January 15, 2025 at 2:00pm"] │   │
│  Design services for 2.4km     │  │                                │   │
│  water main replacement on     │  └────────────────────────────────┘   │
│  Queen St. Includes geotech    │                                        │
│  investigation and traffic...  │  Page: [<] 1 [>]  of 87               │
│                                │                                        │
│  REQUIRED DISCIPLINES          │                                        │
│  ───────────────────────────   │                                        │
│  Internal:                     │                                        │
│  ☑ Civil Engineering           │                                        │
│  ☑ Water Resources             │                                        │
│                                │                                        │
│  External (Sub-consultants):   │                                        │
│  ☑ Geotechnical  [View Subs]   │                                        │
│  ☑ Traffic       [View Subs]   │                                        │
│                                │                                        │
│  COMPLIANCE CHECK              │                                        │
│  ───────────────────────────   │                                        │
│  ✓ Insurance: PASS             │                                        │
│  ✓ WSIB: PASS                  │                                        │
│  ✓ Licenses: PASS              │                                        │
│                                │                                        │
└────────────────────────────────┴────────────────────────────────────────┘
```

### Screen 3: Sub-Consultant Matching
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Sub-Consultants Required: Geotechnical Engineering                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1 PARTNERS (Preferred)                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ABC Geotech                                    [Contact] [Add] │   │
│  │  Contact: John Smith | john@abcgeo.com | 416-555-1234          │   │
│  │  Past Projects Together: 12 | Win Rate: 67%                     │   │
│  │  Typical Fee: $15k-50k | Status: Available                      │   │
│  │  Notes: Preferred for municipal work, very responsive           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  XYZ Geosciences                                [Contact] [Add] │   │
│  │  Contact: Jane Doe | jane@xyzgeo.com | 905-555-5678             │   │
│  │  Past Projects Together: 8 | Win Rate: 62%                      │   │
│  │  Typical Fee: $20k-60k | Status: Limited Capacity               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  TIER 2 PARTNERS (Backup)                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  DEF Drilling                                   [Contact] [Add] │   │
│  │  Contact: Bob Wilson | bob@defdrilling.com                      │   │
│  │  Past Projects Together: 3 | Win Rate: 50%                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                                              [+ Add New Sub-Consultant] │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Build Sequence

### Sprint 1: Foundation (Week 1-2)
- [ ] Project setup (Docker, FastAPI, React scaffolding)
- [ ] Database schema (PostgreSQL + pgvector)
- [ ] File upload endpoint (PDF storage)
- [ ] Basic PDF text extraction (PyMuPDF)
- [ ] Simple frontend: upload + display raw text

### Sprint 2: LLM Extraction (Week 3-4)
- [ ] Claude API integration
- [ ] Structured extraction prompts (dates, scope, disciplines)
- [ ] Source linking (map extractions to page/bbox)
- [ ] Extraction data model and API endpoints
- [ ] Frontend: display extractions with source links

### Sprint 3: Human-in-the-Loop (Week 5-6)
- [ ] PDF viewer component (react-pdf or pdf.js)
- [ ] Side-by-side view (extractions | PDF)
- [ ] Edit/verify extraction interface
- [ ] Audit trail for changes
- [ ] Approve/reject workflow

### Sprint 4: Sub-Consultant Matching (Week 7-8)
- [ ] Sub-consultant data model and CRUD
- [ ] Discipline taxonomy
- [ ] Matching algorithm (RFP disciplines → sub pool)
- [ ] Sub-consultant management UI
- [ ] Integration into RFP analysis view

### Sprint 5: Fuzzy Budget Matching (Week 9-10)
- [ ] Capital budget PDF upload and parsing
- [ ] Budget line item extraction (project name, funding, justification)
- [ ] Vector embeddings for budget items (pgvector)
- [ ] Semantic matching: RFP scope → budget line items
- [ ] Budget match UI (show matched budget with confidence score)
- [ ] Source linking (highlight matched budget PDF section)

### Sprint 6: Dashboard & Polish (Week 11-12)
- [ ] Dashboard with RFP list, stats, filters
- [ ] Key dates timeline view
- [ ] Export functionality (PDF summary, Excel)
- [ ] Compliance checker logic
- [ ] Docker compose for full stack deployment

### Sprint 7: Testing & Hardening (Week 13-14)
- [ ] End-to-end testing with real RFPs
- [ ] Error handling and edge cases
- [ ] Performance optimization (large PDFs)
- [ ] Documentation (setup, usage)
- [ ] Security review

---

## V2 Features (Post-MVP)

### Go/No-Go Scoring Framework
Six-factor scoring with editable weights:
1. Client relationship (25 pts) - past projects, EA involvement, win history
2. Proposal & delivery capacity (25 pts) - team availability
3. Competitive positioning (20 pts) - likely competitors, historical win rate
4. Project characteristics (20 pts) - fit, margin, strategic value
5. Budget & funding clarity (10 pts) - confirmed in capital plan

Score buckets: 75-100 Strong GO, 50-74 Cautious GO, 25-49 Weak GO, 0-24 NO-GO

### EA Pipeline Mining
- Monitor Ontario ERO for EA notices
- Track project phases (Commencement → Completion)
- Predict detailed design RFPs 6-24 months out
- Alert when tracked projects issue RFPs

### Office 365 Integration
- SharePoint: pull RFPs from document libraries
- Outlook: extract RFP attachments from emails
- Teams: post summaries to channels

### Salesforce Integration
- Sync client/account data
- Pull historical win/loss data
- Update opportunity records with pursuit decisions

---

## Open Questions (Decisions Needed)

### Technical
1. **LLM Provider:** Claude API vs. OpenAI vs. allow customer choice?
2. **Vector DB:** pgvector (simpler) vs. dedicated (Pinecone/Weaviate)?
3. **Auth:** Auth0 (faster) vs. Keycloak (self-hostable)?
4. **PDF Processing:** Open source only vs. allow commercial (Adobe)?

### Product
1. **Initial disciplines:** Start with AEC-only or broader?
2. **Pricing model:** Per-seat vs. per-RFP volume vs. flat?
3. **Onboarding:** How do firms populate sub-consultant data initially?

### Go-to-Market
1. **First customers:** Sam's firm? Other AEC contacts?
2. **Channel:** Direct sales vs. APMP/ACEC associations?
3. **Pilot structure:** Free pilot → paid conversion?

---

## Success Metrics

### V1 Launch Criteria
- [ ] Process 50+ page RFP in < 5 minutes
- [ ] Extraction accuracy > 90% on key fields (dates, disciplines)
- [ ] Source linking works for all extracted fields
- [ ] 3 pilot firms onboarded and providing feedback

### Business Metrics (6 months post-launch)
- [ ] 5+ paying customers at $1.5-3k/month
- [ ] NPS > 40 from pilot users
- [ ] < 2 hour average time to go/no-go decision (down from 8-12)
- [ ] User-reported "bad pursuits avoided" stories

---

## Appendix: Research Sources

This plan synthesizes insights from:
1. **Primary Interview** - Sam (environmental consulting, Ontario)
2. **Claude Validation** - Customer validation answers (Dec 2024)
3. **Gemini Research** - Comprehensive AEC pursuit framework
4. **Perplexity Framework** - Go/no-go scoring model, deployment architecture
5. **ChatGPT Market Research** - Canada consulting market, competitive landscape, pricing

Key validated assumptions:
- 2-3 go-to subs per discipline (not massive database needed)
- Data sovereignty is real blocker (self-hosted required)
- Source of truth is #1 trust factor (must show PDF excerpts)
- $750+/RFP in senior time for go/no-go decisions
- Office 365 is priority 1 integration

# RFP Intelligence Platform - Design Brief

## Target Persona

### Environmental Consultant Profile

| Attribute | Detail |
|-----------|--------|
| **Role** | BD Manager, Senior Associate, Principal at environmental consulting firm |
| **Education** | Environmental sciences degree |
| **Personality** | Nerdy, analytical, detail-oriented |
| **Work style** | Organized, thorough (consulting culture) |
| **Work tools** | Microsoft suite (corporate, dated feel) |
| **Personal tools** | YouTube, Airbnb, ChatGPT/LLMs (modern, polished) |
| **Company size** | 15-150 employees |
| **Geography** | Ontario, Canada (expanding) |

### Key Insight
There's a significant gap between their work tools (Microsoft suite - functional but dated) and their personal tools (modern consumer apps). They'll notice and appreciate a modern UI - it represents a breath of fresh air in their daily workflow.

### Product Feedback (from Sam)
- RFPs aren't single documents - they come with background data files
- Open data online may be relevant (past studies, etc.)
- Implies need for multi-file handling and research/context panel

---

## Design Direction

### Chosen Style: Confident Minimalism + Data Density

A blend of:
- **Linear's** dark mode sophistication and information density
- **Notion's** clean spacing system and readable typography
- **Superhuman's** performance-focused, keyboard-first feel
- **Stripe Dashboard's** confident, purposeful minimalism

### Why This Works for Our Persona
1. Scientific background → they respect evidence, data, precision
2. Technical/nerdy → higher tolerance for information density
3. Environmental science training → comfortable with GIS tools, data viz
4. Gap from personal tools → will appreciate modern aesthetic
5. Consulting culture → needs to feel professional, not playful

### What to Avoid
- Generic "AI-built" look (same Tailwind defaults, card-heavy layouts)
- Gaming aesthetics (would feel incongruent with professional context)
- Over-simplified interfaces (these users can handle density)
- Pure white backgrounds (harsh, dated feel)

---

## Competitor Landscape

### RFP Software (Baseline Expectations)

**Loopio**
- Clean, modern UI with intuitive navigation
- Bright design, user-friendly
- Ease of Use rating: 4.8/5
- Focus on autofill and content library features
- Source: [Loopio](https://loopio.com/)

**RFP360 (Responsive)**
- AI-driven tools for proposal management
- Knowledge management focus
- Searchable proposal database rated 9.8
- More enterprise/corporate feel
- Source: [RFP360 Reviews](https://www.trustradius.com/products/rfp360/reviews)

**Market Observation**: Most RFP tools are functional but not inspiring. They serve enterprise buyers, not individual practitioners. Opportunity to differentiate with a more refined, modern feel.

### Environmental Consulting Tools (What They Already Use)

**ESRI ArcGIS**
- Data-dense, professional interfaces
- GIS visualization, mapping focus
- Field apps: Survey123, Field Maps, QuickCapture
- Users are comfortable with complex, layered UIs
- Source: [Esri Environmental Consulting](https://www.esri.com/en-us/industries/aec/business-areas/environmental-consulting)

**Locus Technologies**
- Cloud-based EHS software
- Integration with Google Maps and ESRI ArcGIS Online
- Data management, compliance reporting focus
- Source: [Locus GIS Mapping](https://www.locustec.com/applications/gis-mapping/)

**Implication**: These users already work with complex, data-rich interfaces (GIS, compliance tools). They won't be intimidated by information density.

---

## Mood Board Reference

### Linear App
- Dark mode with brand colors at 1-10% lightness (not pure black)
- Inter typeface - optimized for screen readability
- Minimal CTAs and navigation options
- High contrast for accessibility
- Command palette (Cmd+K) for power users
- Source: [Linear Design Analysis](https://blog.logrocket.com/ux-design/linear-design/)

**Key Takeaway**: "Professional to engineers" - dark gray, sans-serif, minimalist

### Superhuman
- "Carbon" dark mode - five shades of gray, no pure black/white
- Surface layering: closer layers lighter, distant layers darker
- White text at 90% opacity (not 100%) to reduce eye strain
- Metadata prioritized over navigational elements
- Keyboard-first, speed-focused
- Source: [Superhuman Dark Themes](https://blog.superhuman.com/how-to-design-delightful-dark-themes/)

**Key Takeaway**: Dark themes require independent design, not simple inversion

### Notion
- Inter typeface (same as Linear)
- 8px grid system for spacing
- Sidebar width: 224px (optimized for readability)
- Warm grays instead of harsh blacks
- Minimalist with functional depth
- Source: [Notion Sidebar Breakdown](https://medium.com/@quickmasum/ui-breakdown-of-notions-sidebar-2121364ec78d)

**Key Takeaway**: "Thoughtful design that feels simple but is built for clarity"

### Stripe Dashboard
- Confident use of whitespace
- Clear information hierarchy
- Professional without being boring
- Subtle gradients and depth
- Data visualization done well

---

## Technical Design Principles (Synthesized from LLM Research)

> **Sources**: ChatGPT, Claude, Gemini, Perplexity research synthesis

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| UI Text | Inter | 12-14px | 400-600 |
| Headings | Inter Display | 18-62px | 600-800 |
| Data/Numbers | Geist Mono or JetBrains Mono | 12-14px | 400 |
| IDs/Timestamps | Monospace | 12px | 400 |

- Use **tabular figures** for number alignment in tables
- Font stack: `"Inter UI", "SF Pro Display", -apple-system, system-ui, Roboto`
- Maximum 3-4 sizes with weight variation for hierarchy

### Color System (Exact Values)

```css
/* Core palette - Dark mode first */
--background:     #1F2126;  /* Dark gray, not pure black */
--surface:        #2A2E35;  /* Elevated surfaces */
--surface-hover:  #353A42;  /* Hover states */

/* Text */
--text-primary:   #F5F5F5;  /* 90% opacity feel */
--text-secondary: #A7A9A9;  /* Muted text */
--text-tertiary:  #6B7280;  /* Disabled/placeholder */

/* Semantic colors (use sparingly) */
--accent:         #2780A0;  /* Teal - primary actions */
--success:        #2DB864;  /* Go decision */
--warning:        #D4A634;  /* Caution/review needed */
--error:          #FF5459;  /* No-go/critical */
--info:           #3B82F6;  /* In progress */

/* Status-specific */
--status-go:      #2DB864;  /* Green */
--status-maybe:   #D4A634;  /* Yellow/Orange */
--status-nogo:    #FF5459;  /* Red */
--status-pending: #6B7280;  /* Gray */
```

**Color philosophy**:
- Use LCH color space for perceptual uniformity (Linear approach)
- Only 3 core variables (base, accent, contrast) - derive rest algorithmically
- Color for meaning only, never decoration

### Spacing & Grid

- **Base grid**: 8px with 4px half-steps for tight spacing
- **Sidebar width**: 224px (Notion standard)
- **Row height**: Condensed by default (32-40px)
- **Table padding**: 8px horizontal, 4px vertical per cell
- **Section margins**: 24px between major sections

### Data Alignment Rules

| Data Type | Alignment | Rationale |
|-----------|-----------|-----------|
| Text/Labels | Left | Reading direction |
| Numbers/Currency | Right | Decimal alignment |
| Dates | Left | Treated as text |
| Status badges | Left + icon | Scannable |
| Actions | Far right | End-of-row convention |

### Interaction Patterns

**Speed requirements**:
- All interactions < 100ms (feels instant)
- Use optimistic UI updates
- No unnecessary confirmation dialogs
- Animations functional only, never decorative

**Keyboard-first design**:
- Command palette (Cmd+K) available everywhere
- Single-key shortcuts for common actions
- Two-letter "Go To" sequences (57% faster to learn)
- All shortcuts visible in tooltips

**Hover/Focus states**:
- Hover: 5-10% background shift
- Focus: 2px outline, accent color at 40% opacity
- No color inversion or dramatic changes

---

## Keyboard Shortcuts Specification

### Command Palette (Cmd+K)

Five rules from Superhuman:
1. **Available everywhere** - Same shortcut works from any context
2. **Central and singular** - One palette for ALL actions
3. **Omnipotent** - Include every possible action
4. **Flexible search** - Fuzzy matching with synonyms
5. **Context-aware** - Show relevant commands first

### Core Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Cmd+K` | Open command palette | Global |
| `Cmd+N` | Create new RFP | Global |
| `/` | Focus search | Global |
| `?` | Show all shortcuts | Global |
| `Escape` | Close/deselect | Global |

### Navigation (Two-letter "Go To")

| Shortcut | Destination |
|----------|-------------|
| `G` then `D` | Go to Dashboard |
| `G` then `I` | Go to Inbox/New RFPs |
| `G` then `L` | Go to Library |
| `G` then `S` | Go to Settings |

### List Navigation (Vim-style)

| Shortcut | Action |
|----------|--------|
| `J` / `↓` | Next item |
| `K` / `↑` | Previous item |
| `Enter` | Open detail view |
| `Space` | Toggle selection |
| `Shift+Click` | Multi-select range |

### RFP Actions

| Shortcut | Action |
|----------|--------|
| `E` | Edit selected |
| `R` | Mark as reviewed |
| `G` | Mark as Go |
| `N` | Mark as No-Go |
| `A` | Assign to team |
| `D` | Delete (soft) |

### Libraries
- [cmdk](https://cmdk.paco.me/) - Command palette component
- [kbar](https://kbar.vercel.app/) - Alternative command palette
- [Mousetrap](https://craig.is/killing/mice) - Keyboard event binding

---

## Screen Specifications

### Main RFP List View (Primary Interface)

**Layout**: 12-column data table

| Column | Width | Alignment | Notes |
|--------|-------|-----------|-------|
| 1. Checkbox | 40px | Center | Bulk select |
| 2. Client/RFP Name | flex | Left | Primary identifier |
| 3. Status | 100px | Left | Badge: Pending/Reviewing/Go/No-Go |
| 4. Team Lead | 120px | Left | Avatar + name |
| 5. Deadline | 100px | Left | Date format |
| 6. Days Left | 80px | Right | Countdown, color-coded |
| 7. Score | 60px | Right | Numeric with indicator |
| 8. Go/No-Go | 100px | Left | Decision badge |
| 9. Team | 100px | Left | Avatars |
| 10. Created | 100px | Left | Date |
| 11. Notes | 150px | Left | Truncated preview |
| 12. Actions | 60px | Right | 3-dot menu |

**Features**:
- Sort by any column
- Filter by status, date range, value range
- Bulk actions on selected rows
- Row expansion for scope summary
- Frozen header on scroll

### RFP Detail View (Split-Pane)

```
┌─────────────────────────────────────────────────────────────┐
│  [← Back]  RFP Name                           [Actions ▼]   │
├─────────────────────────────────────┬───────────────────────┤
│                                     │                       │
│  RFP CONTENT (70%)                  │  EVALUATION (30%)     │
│                                     │                       │
│  - Full document text               │  Scoring Rubric:      │
│  - Extracted fields                 │  ┌─────────────────┐  │
│  - Source highlighting              │  │ Strategic Fit   │  │
│  - PDF viewer                       │  │ ████████░░ 80%  │  │
│                                     │  ├─────────────────┤  │
│  [Scrollable]                       │  │ Capacity        │  │
│                                     │  │ ██████░░░░ 60%  │  │
│                                     │  ├─────────────────┤  │
│                                     │  │ Financial       │  │
│                                     │  │ █████████░ 90%  │  │
│                                     │  └─────────────────┘  │
│                                     │                       │
│                                     │  Total: 76/100        │
│                                     │  [GO] [MAYBE] [NO-GO] │
│                                     │                       │
│                                     │  [Sticky on scroll]   │
└─────────────────────────────────────┴───────────────────────┘
```

### Go/No-Go Weighted Scoring

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Strategic Alignment | 20% | Core expertise match |
| Resource Capacity | 15% | Team bandwidth |
| Financial Threshold | 30% | Margin after pursuit costs |
| Indigenous Participation | 20% | 5% federal target, OCAP compliance |
| Competitive Context | 15% | Incumbent advantage |

Formula: `Score = Σ(Value × Weight)`

---

## Canadian Regulatory Context

### Multi-Portal Landscape
- **Federal**: CanadaBuys (centralized)
- **Ontario**: Tender Opportunities Portal
- **BC**: BC Bid
- **Other provinces**: Individual systems

### Indigenous Engagement Requirements
- Federal 5% Indigenous procurement target
- OCAP principles for Indigenous data
- Community protocol observance
- **No-Go trigger**: Timeline too aggressive for meaningful consultation

### Environmental Consulting Context
- Phase I ESA: $2,500-$5,000 fees
- Liability can far exceed profit if REC overlooked
- Need to flag: unrealistic timelines, ambiguous liability, capacity gaps

---

## Anti-Patterns to Avoid

### Trust Killers (Immediate)
- Excessive clicks for common tasks
- Hidden complexity behind modals
- Visual hierarchy that obscures data
- Bloatware and unused features
- Performance > 100ms response

### Common RFP Software Mistakes

| Mistake | Impact | Solution |
|---------|--------|----------|
| Card layout for comparison | Can't compare side-by-side | Use tables |
| Hide data behind clicks | Slow decision-making | 12 columns visible |
| No keyboard support | 3+ clicks per task | Full shortcut system |
| 15-20 custom fields | Overwhelming forms | Core fields only, progressive disclosure |
| Status as small label | Users miss action items | Color-coded badges, always visible |
| No bulk actions | 5 RFPs = 5 clicks each | Shift+Click multi-select |
| Evaluation hidden from RFP | Context switching | Split-pane view |
| Unclear workflow | User confusion | Clear status indicators |
| No undo/restore | Fear of mistakes | Soft deletes, 30-day recovery |
| Inconsistent navigation | Trust erosion | Consistent sidebar + shortcuts |

### Feature Fatigue Warning
> "RFP products do so many things that I just get lost and don't know what to do."

**Philosophy**: Start with core fields only. Resist customization requests initially - this is what makes tools feel bloated.

---

## UI Components to Design

### Priority Screens (MVP)

1. **Dashboard/Home**
   - Recent RFPs in table format
   - Quick stats (Go/No-Go breakdown)
   - Command palette shortcut visible

2. **Main RFP List**
   - 12-column data table (see spec above)
   - Filters in header
   - Bulk action bar

3. **RFP Detail View**
   - Split-pane: 70% content, 30% evaluation
   - Sticky scoring rubric
   - Source highlighting

4. **Quick Scan Results**
   - GO/MAYBE/NO-GO recommendation badge
   - Key extracted fields
   - Source attribution with page links

5. **Sub-Consultant List**
   - Filterable table
   - Discipline tags
   - Tier indicators (1/2)

### Component Library Needs
- Data tables (sortable, filterable, selectable)
- Status badges (Go/Maybe/No-Go/Pending)
- Score indicators (progress bars, numeric)
- Buttons (primary, secondary, ghost, danger)
- Form inputs (dark mode optimized)
- Command palette
- Side panels (non-modal)
- Toast notifications
- Keyboard shortcut hints

---

## Research Prompt for LLM Deep-Dive

Use this prompt with Claude/GPT for additional persona research:

```
I'm designing a B2B SaaS tool for environmental consultants at mid-sized consulting firms (15-150 employees) in Canada. The tool helps them make go/no-go decisions on RFPs.

User profile:
- Environmental science degree holders
- Work in consulting (organized, thorough, deadline-driven)
- Use Microsoft suite at work, but modern apps (Airbnb, YouTube, ChatGPT) personally
- Comfortable with data-dense interfaces (GIS tools, compliance software)
- Analytical, detail-oriented, "nerdy"

Research questions:
1. What UI patterns resonate with technical professionals who have a scientific background?
2. What makes enterprise B2B software feel "premium" vs "dated"?
3. How do successful tools like Linear, Notion, and Superhuman create trust and perceived quality through design?
4. What are common UI/UX mistakes in RFP/proposal management software?
5. What design elements signal "this tool was built by people who understand my work"?

Please provide specific, actionable design recommendations with examples.
```

---

## Figma MCP Integration

### Setup Instructions

1. **Enable in Figma Desktop**
   - Open Figma desktop app (latest version)
   - Click Figma menu → Preferences → "Enable Dev Mode MCP Server"
   - Server runs at `http://127.0.0.1:3845/sse`

2. **Connect to Claude Code**
   ```bash
   claude mcp add --transport sse figma-dev-mode-mcp-server http://127.0.0.1:3845/sse
   ```

3. **Verify Connection**
   ```bash
   claude mcp list
   ```

### Alternative: Remote Server (No Desktop Required)
```bash
claude mcp add --transport http figma https://mcp.figma.com/mcp
```

### Capabilities Once Connected
- Generate code from selected Figma frames
- Extract design context (variables, components, layout data)
- Reference Figma designs in prompts
- Create pixel-perfect implementations from mockups

### Sources
- [Claude Code + Figma MCP](https://www.builder.io/blog/claude-code-figma-mcp-server)
- [Figma Remote Server Docs](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/)
- [Composio Figma MCP Guide](https://composio.dev/blog/how-to-use-figma-mcp-with-claude-code-to-build-pixel-perfect-designs)

---

## Next Steps

1. [ ] Create mood board in Figma with reference screenshots
2. [ ] Set up Figma MCP connection
3. [ ] Design core component library (buttons, cards, tables)
4. [ ] Create Dashboard wireframe
5. [ ] Create Quick Scan results wireframe
6. [ ] Design RFP detail view with evidence panel
7. [ ] Test with Sam (or similar user) for feedback
8. [ ] Iterate based on feedback

---

## References

### Competitor/Tool Research
- [Loopio RFP Software](https://loopio.com/)
- [RFP360 Reviews](https://www.trustradius.com/products/rfp360/reviews)
- [ESRI Environmental Consulting](https://www.esri.com/en-us/industries/aec/business-areas/environmental-consulting)
- [Locus Technologies GIS](https://www.locustec.com/applications/gis-mapping/)

### Design Inspiration
- [Linear Design Trend Analysis](https://blog.logrocket.com/ux-design/linear-design/)
- [Linear UI Redesign](https://linear.app/now/how-we-redesigned-the-linear-ui)
- [Linear Design System (Figma)](https://www.figma.com/community/file/1222872653732371433/linear-design-system)
- [Superhuman Dark Theme Design](https://blog.superhuman.com/how-to-design-delightful-dark-themes/)
- [Notion Sidebar UI Breakdown](https://medium.com/@quickmasum/ui-breakdown-of-notions-sidebar-2121364ec78d)
- [SaaS Dashboard Inspiration 2024](https://muz.li/blog/dashboard-design-inspirations-in-2024/)

### MCP Integration
- [Claude Code + Figma MCP](https://www.builder.io/blog/claude-code-figma-mcp-server)
- [Figma MCP Remote Server](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/)

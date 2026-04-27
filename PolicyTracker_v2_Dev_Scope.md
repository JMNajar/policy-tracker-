# PolicyTracker v2 — Development Scope
**Product:** GFTO AI Compliance Engine / PolicyTracker
**Owner:** Horsepower AI / GF Tech One
**Date:** April 26, 2026
**Stack:** Python static site generator → Vercel (static hosting) → GitHub Actions (CI/CD)

---

## Current Architecture (What We're Building On)

```
build_policytracker.py (~1,850 lines, monolithic)
  → fetches: Google News RSS, Congress.gov API, Federal Register API, FEC API
  → outputs: 7 static HTML files
  → GitHub Actions rebuilds daily (news) + weekly (bills/PAC)
  → Vercel auto-deploys on push
```

No database. No user accounts. No server-side runtime. Pure static HTML.

---

## V2 Build Phases

---

### Phase 1 — Intelligence Layer + Risk Scoring
**Timeline: 1–2 weeks**
**Score impact: 2.5 → 3.5**
**Architecture change: None — stays static, adds Claude API call at build time**

#### Feature 1A: "What This Means" Executive Briefings

**What to build:**
- Add a call to the Claude API inside `build_policytracker.py` during the build
- For each Top 10 news item and each Key Bill to Watch, generate a 3-bullet briefing:
  - **Operational Impact:** What this means for cannabis businesses
  - **Timeline:** When this takes effect or when to expect movement
  - **Action Required:** What an executive should do now
- Briefings render as a collapsible block under each news item (click "Executive Briefing ▼")
- Cap at 20 items per build to control API cost (~$0.10–0.30/build with Haiku)

**Technical implementation:**
1. Add `anthropic` to GitHub Actions pip install step
2. Add `ANTHROPIC_API_KEY` as GitHub Secret
3. In `build_policytracker.py`, add `generate_briefing(headline, summary, item_type)` function
4. Use `claude-haiku-4-5-20251001` (fastest, cheapest) with a tight prompt
5. Cache briefings in a local JSON file (`briefings_cache.json`) — only regenerate if headline has changed
6. Inject briefing HTML into each item's card at render time

**Prompt template:**
```
You are a cannabis industry policy analyst. Given this regulatory news item, provide a 3-bullet executive briefing for cannabis business leaders. Be specific, not general. Use plain English.

Item: {headline}
Context: {summary}
Type: {bill|news|executive_action}

Respond with exactly 3 lines:
IMPACT: [one sentence]
TIMELINE: [one sentence with specific dates or timeframes if known]
ACTION: [one specific thing a cannabis executive should do this week]
```

**Files to modify:**
- `build_policytracker.py`: Add briefing generation function + cache logic + HTML injection
- `.github/workflows/update.yml`: Add `anthropic` to pip install, add ANTHROPIC_API_KEY secret
- `briefings_cache.json`: New file (committed to repo, updated by Actions)

---

#### Feature 1B: Risk Scoring on Bills

**What to build:**
- Add a Risk Score badge to every bill in bills.html and on the homepage Key Bills section
- Scores: `LOW` (gray) / `MEDIUM` (yellow) / `HIGH` (orange) / `CRITICAL` (red)
- Score is computed at build time from available data signals

**Scoring heuristic (in Python):**
```python
def score_bill(bill):
    score = 0
    # Committee status signals
    if 'passed' in bill['latest_action'].lower(): score += 3
    if 'vote' in bill['latest_action'].lower(): score += 2
    if 'referred' in bill['latest_action'].lower(): score += 0
    if 'markup' in bill['latest_action'].lower(): score += 2
    # Bipartisan signal (look for "cosponsors" count if available)
    if bill.get('cosponsor_count', 0) > 10: score += 2
    if bill.get('cosponsor_count', 0) > 25: score += 1
    # Known high-priority bill override
    HIGH_PRIORITY_BILLS = ['SAFER Banking', 'Schedule III', '280E', 'HOPE']
    if any(name in bill['title'] for name in HIGH_PRIORITY_BILLS): score += 2

    if score >= 6: return 'CRITICAL'
    if score >= 4: return 'HIGH'
    if score >= 2: return 'MEDIUM'
    return 'LOW'
```

**Files to modify:**
- `build_policytracker.py`: Add `score_bill()` function, inject badge HTML into bill rows

**Effort:** Low — 2–3 hours of Python work

---

### Phase 2 — State + Sector Filtering
**Timeline: 1 week**
**Score impact: 3.5 → 4.0**
**Architecture change: None — client-side JavaScript only**

#### Feature 2A: State and Sector Filter Bar

**What to build:**
- Filter bar on index.html (news) and bills.html with two dropdowns:
  - **State:** All States + 50-state list
  - **Sector:** All Sectors | Cultivation | Retail/Dispensary | Testing | Distribution | Hemp | MSO
- Items that don't match the active filter are hidden via CSS (`display: none`)
- Filter state persists in `localStorage` (survives page reload)
- "Showing X of Y items" counter updates dynamically

**Technical implementation — Python side:**
- Add state and sector tagging to each news item and bill at parse time
- Tagging logic: keyword match against title + summary text
  ```python
  STATE_KEYWORDS = {'california': 'CA', 'ohio': 'OH', 'new york': 'NY', ...}  # all 50
  SECTOR_KEYWORDS = {
    'banking': ['bank', 'financial', 'credit union', 'payment'],
    'retail': ['dispensary', 'retail', 'storefront', 'point of sale'],
    'cultivation': ['grow', 'cultivat', 'farm', 'harvest', 'greenhouse'],
    'testing': ['lab', 'testing', 'compliance', 'potency'],
    'hemp': ['hemp', 'cbd', 'cbg', 'delta-8', 'delta8'],
    'tax': ['280e', 'tax', 'irs', 'deduction']
  }
  ```
- Emit tags as `data-states="CA,OH"` and `data-sectors="banking,retail"` attributes on each card element

**Technical implementation — JavaScript side:**
- Add `<script>` block to each page with filter logic
- Dropdown `change` → iterate all cards → show/hide by matching data attributes
- Counter text updates on every filter change

**Files to modify:**
- `build_policytracker.py`: Add tagging functions, emit data attributes, inject filter bar HTML + JS

**Effort:** Medium — 4–6 hours

---

### Phase 3 — Money Section Rebuild + Conflict of Interest Flags
**Timeline: 1 week**
**Score impact: 4.0 → 4.2**
**Architecture change: None — enhanced Python data pipeline**

#### Feature 3A: Conflict-of-Interest Flags

**What to build:**
- Cross-reference: lawmakers receiving opposition-industry PAC money vs. lawmakers sitting on cannabis-relevant committees
- Flag lawmakers where BOTH are true with a red `⚠ Conflict` badge
- Committees to watch: Senate Judiciary, Senate Banking, House Energy & Commerce, House Judiciary, Senate Finance

**Technical implementation:**
- Congress.gov API has a `/v3/member/{bioguideId}/committee` endpoint — fetch committee assignments for top 50 lawmakers
- Already have FEC opposition disbursements data (who's receiving pharma/alcohol/prison PAC money)
- Cross-reference: `conflict = lawmaker in opposition_recipients AND lawmaker in relevant_committees`
- Render badge in lawmakers.html and money.html

**Files to modify:**
- `build_policytracker.py`: Add committee fetch function, add conflict detection logic, add badge rendering

**Effort:** Medium — 4–6 hours

#### Feature 3B: PAC Spend Trend Chart

**What to build:**
- Simple bar chart on money.html showing cannabis industry PAC total receipts vs. opposition PAC totals
- Use a lightweight charting library (Chart.js via CDN — no npm needed)
- Data comes from existing FEC API calls

**Files to modify:**
- `build_policytracker.py`: Aggregate totals, inject Chart.js canvas + data into money.html

**Effort:** Low-Medium — 2–3 hours

---

### Phase 4 — Trust Signal Upgrade
**Timeline: 2–3 days**
**Score impact: 4.2 → 4.4**
**Architecture change: None — new static page + content edits**

#### Feature 4A: Methodology Page

**What to build:**
- New page: `methodology.html`
- Sections:
  - How We Collect Data (per source with verification process)
  - Update Schedule (daily vs. weekly cadence)
  - What We Do Not Do (no legal advice, no investment advice)
  - How To Report An Error (contact email)
  - Editorial Independence Statement
- Add "Methodology" to nav bar

**Files to modify:**
- `build_policytracker.py`: Add `generate_methodology_page()` function
- `.github/workflows/update.yml`: No change needed (static content, regenerates on any build)

**Effort:** Low — 2–3 hours

#### Feature 4B: Named Authorship in About Page

**What to build:**
- Add a named "Data Intelligence Team" section with at minimum:
  - Horsepower AI as builder/operator
  - A contact email for corrections/inquiries
  - A brief statement of editorial review process

**Files to modify:**
- `build_policytracker.py`: Edit `generate_about_page()` content strings

**Effort:** Low — 30 minutes

---

### Phase 5 — User Accounts, Watchlists & Personalized Alerts
**Timeline: 3–4 weeks**
**Score impact: 4.4 → 4.8**
**Architecture change: SIGNIFICANT — requires backend infrastructure**

> **Note:** This is the only phase that requires changing the architecture. All other phases are Python + static HTML only.

#### What changes:

The static site stays. We add a **thin serverless layer**:
- **Supabase** (free tier): User auth (email/password + Google OAuth) + database (watchlists, alert preferences)
- **Vercel Serverless Functions**: API endpoints for save/fetch watchlist, subscribe/unsubscribe alerts
- **Resend or SendGrid**: Transactional email for personalized weekly digests

#### New infrastructure:

| Service | Purpose | Cost |
|---|---|---|
| Supabase (free tier) | Auth + PostgreSQL DB | $0 to start |
| Vercel Functions | API endpoints | $0 (included in Vercel free tier) |
| Resend | Transactional email | $0 (100 emails/day free) |

#### Database schema (Supabase):

```sql
-- users: handled by Supabase Auth (built-in)

CREATE TABLE watchlist_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  item_type text NOT NULL,  -- 'bill' | 'lawmaker' | 'topic'
  item_id text NOT NULL,    -- bill number, bioguide ID, or topic slug
  item_label text NOT NULL, -- display name
  created_at timestamptz DEFAULT now()
);

CREATE TABLE alert_preferences (
  user_id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  email_digest boolean DEFAULT true,
  digest_frequency text DEFAULT 'weekly',  -- 'daily' | 'weekly'
  states text[],     -- e.g. ['CA', 'OH']
  sectors text[]     -- e.g. ['banking', 'retail']
);
```

#### Vercel Functions to build:

```
/api/watchlist/add.js      — POST: add item to watchlist
/api/watchlist/remove.js   — DELETE: remove item
/api/watchlist/list.js     — GET: fetch user's watchlist
/api/alerts/subscribe.js   — POST: save alert preferences
/api/digest/send.js        — POST: triggered by GitHub Actions, sends personalized digest
```

#### Frontend changes (minimal):

- Add a "Save to Watchlist ☆" button to each bill card and lawmaker card
- Button calls `/api/watchlist/add` if user is logged in; prompts login modal if not
- Add a lightweight login/signup modal (uses Supabase JS SDK via CDN)
- Add "My Watchlist" link in nav (shows only when logged in)
- `watchlist.html`: New page listing user's saved items

**Files to create:**
- `api/watchlist/add.js`, `api/watchlist/remove.js`, `api/watchlist/list.js`
- `api/alerts/subscribe.js`
- `api/digest/send.js`
- `watchlist.html` (generated by Python OR static)

**Files to modify:**
- `build_policytracker.py`: Add watchlist buttons to bill/lawmaker cards, add login modal HTML/JS
- `.github/workflows/update.yml`: Add digest trigger step
- `vercel.json`: Configure function routes

**Effort:** High — 3–4 weeks. This is real software engineering. Recommend doing Phases 1–4 first and shipping V2.0, then building Phase 5 as V2.1.

---

## Full Build Timeline

| Phase | Features | Effort | Timeline | Score After |
|---|---|---|---|---|
| **Phase 1** | Intelligence layer + Risk scoring | Medium | 1–2 weeks | 3.5 |
| **Phase 2** | State/sector filtering | Medium | 1 week | 4.0 |
| **Phase 3** | Money rebuild + CoI flags | Medium | 1 week | 4.2 |
| **Phase 4** | Methodology + trust signals | Low | 2–3 days | 4.4 |
| **Phase 5** | User accounts + alerts | High | 3–4 weeks | 4.8 |
| | | | | |
| **V2.0 ship date** | Phases 1–4 | ~4–5 weeks | ~June 1, 2026 | **4.4** |
| **V2.1 ship date** | Phase 5 | +3–4 weeks | ~July 1, 2026 | **4.8** |

---

## New API Keys / Secrets Required

| Secret | Service | How to Get | Cost |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API (briefings) | console.anthropic.com | ~$5–15/month |
| `SUPABASE_URL` | Supabase (Phase 5 only) | supabase.com | Free tier |
| `SUPABASE_ANON_KEY` | Supabase (Phase 5 only) | supabase.com | Free tier |
| `RESEND_API_KEY` | Email digests (Phase 5 only) | resend.com | Free tier |

---

## Files Modified Per Phase

| Phase | Files Modified | Files Created |
|---|---|---|
| 1A | `build_policytracker.py`, `update.yml` | `briefings_cache.json` |
| 1B | `build_policytracker.py` | — |
| 2 | `build_policytracker.py` | — |
| 3 | `build_policytracker.py` | — |
| 4 | `build_policytracker.py` | `methodology.html` |
| 5 | `build_policytracker.py`, `vercel.json`, `update.yml` | `api/watchlist/*.js`, `api/alerts/*.js`, `api/digest/send.js`, `watchlist.html` |

---

## Recommended Build Order

1. **Start with Phase 1B (Risk Scoring)** — easiest win, pure Python, ships in a day
2. **Then Phase 4 (Trust Signals)** — low effort, high credibility payoff for enterprise conversations
3. **Then Phase 1A (Intelligence Layer)** — highest impact, requires Claude API setup
4. **Then Phase 2 (Filtering)** — makes the product personally relevant
5. **Then Phase 3 (Money/CoI)** — differentiating data layer
6. **Then Phase 5 (Accounts/Alerts)** — infrastructure lift, build last when you have users to serve

---

## Decision Point Before Starting

Before writing code, confirm:
- [ ] Do you have an Anthropic API key? (Required for Phase 1A)
- [ ] Is Jeff or GFT1 the owner of the GitHub repo? (Required to add Secrets)
- [ ] Is the goal to ship V2.0 by a specific date? (Affects what we cut)
- [ ] Do you want to build Phase 5 yourself or hand it to a developer?

---

*Scope prepared by Horsepower AI — April 26, 2026*

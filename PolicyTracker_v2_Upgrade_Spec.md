# PolicyTracker v2 — Product Upgrade Specification
**Product:** GFTO AI Compliance Engine / PolicyTracker
**Owner:** Horsepower AI / GF Tech One
**Date:** April 26, 2026
**Current URL:** https://policy-tracker-rosy.vercel.app/
**Current Score:** 2.5 / 5
**Target Score:** 4.5 / 5

---

## Executive Summary

PolicyTracker v1 is a credible, clean cannabis policy news aggregator. It has the right categories, verified sources, and a professional enough appearance to be forwarded in a boardroom. What it lacks is the layer that separates a news feed from an intelligence tool: **synthesis, personalization, and actionability**. V2 closes that gap.

---

## Upgrade Priorities

### Priority 1 — Add the "What This Means" Intelligence Layer
**The Gap:** Cannabis executives can find headlines anywhere. What they cannot get elsewhere is a clear, jargon-free interpretation of what a policy change means for their operation.

**The Fix:**
- Add an "Executive Briefing" block below each news item or bill summary
- Format: 2–3 bullet points titled **Operational Impact**, **Timeline**, **Action Required**
- Example: *"DEA rescheduling announcement → Banking restrictions ease within 90 days → Notify your CFO to begin traditional banking outreach now"*
- Can be AI-generated with human editorial review, or AI-only with a disclaimer

**Outcome:** Converts the product from news feed to decision-support tool.

---

### Priority 2 — State and Sector Filtering
**The Gap:** Cannabis is a state-regulated business. A dispensary operator in Ohio has zero use for Missouri hemp rules. Currently, everything is presented as a flat national feed.

**The Fix:**
- Add filter bar at top of dashboard: **State** (dropdown, multi-select) + **Sector** (Cultivation / Retail / Testing / Distribution / Hemp / Multi-State Operator)
- Persist user preferences via cookie or login
- Tag every item with applicable states and sectors on ingest
- Default view shows all; filtered view shows only relevant items

**Outcome:** Personal relevance. The executive sees their world, not the whole industry.

---

### Priority 3 — Risk Scoring on Active Legislation
**The Gap:** There is no way to assess which bills actually matter. A bill that will never pass is noise. A bill three votes from passage that affects banking is a fire drill.

**The Fix:**
- Add a **Risk Score** badge to each bill: Low / Medium / High / Critical
- Score based on: committee status, sponsor bipartisan support, executive branch alignment, floor vote schedule
- Add a "Bills to Watch" section to the homepage that surfaces only High + Critical items
- Can start with manual editorial scoring and automate later

**Outcome:** Executives stop reading everything and start acting on what matters.

---

### Priority 4 — Saved Watchlists and Custom Alerts
**The Gap:** There is no way for a user to say "track this bill" or "alert me when anything touches banking regulation." The product has no memory of who you are.

**The Fix:**
- Add lightweight user accounts (email + password, or Google OAuth)
- Let users bookmark bills, lawmakers, and topics
- Weekly email digest (already exists as newsletter — extend it to personalized alerts)
- Alert trigger options: new vote scheduled, status change, new related news item

**Outcome:** Creates stickiness. Executives return because the product is watching their issues for them.

---

### Priority 5 — Strengthen the Money / Campaign Finance Section
**The Gap:** The PAC and campaign finance data is the most differentiated asset in this product — nowhere else surfaces it in a cannabis-specific context. But it's underdeveloped.

**The Fix:**
- Pull FEC.gov and OpenSecrets data into a structured table: Lawmaker → PAC Donors → Opposition Industry donors (alcohol, pharma, tobacco)
- Add a **Conflict of Interest** flag when a lawmaker has significant opposition-industry funding and is on a relevant committee
- Show total cannabis-industry PAC spend by cycle, updated quarterly

**Outcome:** Turns PolicyTracker into the only place a cannabis lobbyist or government affairs executive needs to go before a Hill meeting.

---

### Priority 6 — Trust Signal Upgrade for Enterprise Buyers
**The Gap:** "Official cannabis news supplier to Easyriders Magazine" works for the enthusiast market. It does not close a contract with a CCO or VP of Government Affairs at an MSO.

**The Fix:**
- Add a "Methodology" page explaining how data is sourced, verified, and updated
- Add a legal disclaimer co-reviewed with a cannabis attorney (even one statement of review adds credibility)
- Consider a "Trusted By" logos section once 3–5 named clients are using it
- Add named authorship or editorial team — even one person's name and title

**Outcome:** Unlocks enterprise sales conversations. Executives need to know who stands behind the data.

---

## Feature Roadmap Summary

| Phase | Feature | Effort | Impact |
|---|---|---|---|
| V2.0 | Intelligence layer ("What This Means") | Medium | Very High |
| V2.0 | State/sector filtering | Medium | High |
| V2.0 | Risk scoring on bills | Low-Medium | High |
| V2.1 | User accounts + watchlists | High | Very High |
| V2.1 | Personalized email alerts | Medium | High |
| V2.1 | Money/PAC section rebuild | Medium | Very High |
| V2.2 | Methodology page + trust signals | Low | High |
| V2.2 | Conflict-of-interest flags | Medium | High |

---

## Success Metrics

| Metric | V1 Baseline | V2 Target |
|---|---|---|
| Return visit rate | Unknown | 3x per week per user |
| Newsletter open rate | Unknown | 40%+ |
| Time on site | Unknown | 4+ minutes average |
| Enterprise client conversations | 0 | 3+ active in 90 days |
| Product trust score (executive survey) | ~2.5 / 5 | 4.0+ / 5 |

---

## What PolicyTracker Becomes at V2

At V2, PolicyTracker is not a news feed. It is the **cannabis industry's only dedicated policy intelligence platform** — the tool a VP of Government Affairs opens on Monday morning before checking email, and the document a CCO attaches to board packets to show they have regulatory risk covered.

That is a product worth paying for.

---

*Spec prepared by Horsepower AI — April 26, 2026*

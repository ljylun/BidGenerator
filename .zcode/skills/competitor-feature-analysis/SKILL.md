---
name: competitor-feature-analysis
description: Product-focused competitor analysis — feature inventory, capability matrix, roadmap signals, and feature gap analysis to inform product strategy and prioritization. Renamed from product-management:competitive-brief on 2026-04-25 to resolve a name collision with marketing:competitive-brief (now marketing:competitor-positioning-brief). Make sure to use this skill whenever the user says compare features against [competitor], build a feature matrix, what does [competitor] have that we don't, where should we invest to reach parity, what features should we build next based on competitive gaps, or analyze [competitor]'s product roadmap. Do NOT use for: messaging/positioning analysis (use marketing:competitor-positioning-brief), interactive sales battlecards (use sales:competitive-intelligence), feature spec writing for build (use product-management:write-spec), or roadmap reprioritization (use product-management:roadmap-update — though this skill's output is often an INPUT to roadmap-update).
---

# Competitor Feature Analysis

Product-focused competitor analysis: feature parity, gap analysis, and roadmap inference.

## Rename note

This skill was previously named `product-management:competitive-brief`. Renamed on 2026-04-25 to resolve a name collision with `marketing:competitive-brief` (now `marketing:competitor-positioning-brief`). The old name still routes here for backward compatibility but new prompts should use the new name.

## When to use vs. adjacent skills

| Use this skill when... | Use a different skill when... |
|---|---|
| Comparing product features feature-by-feature | Comparing brand voice, messaging, content → `marketing:competitor-positioning-brief` |
| Building a feature parity matrix | Generating an HTML battlecard for live sales → `sales:competitive-intelligence` |
| Inferring competitor's roadmap from public signals | Writing the spec for a feature you've decided to build → `product-management:write-spec` |
| Identifying gaps to inform what to build next | Reordering an existing roadmap → `product-management:roadmap-update` (use this skill's output AS input) |

## Output structure

1. **Competitor snapshot** — Company, product line, market segment, pricing model, customer profile.

2. **Feature inventory** — Complete list of advertised features, organized by category. Each feature gets: present (Y/N), maturity (beta / GA / mature), depth (basic / intermediate / advanced), and source (site / docs / changelog / customer review).

3. **Parity matrix**

   | Feature | Us | Competitor | Status |
   |---|---|---|---|
   | Feature 1 | ✓ mature | ✓ mature | parity |
   | Feature 2 | — | ✓ GA | gap (we lack) |
   | Feature 3 | ✓ beta | — | lead (we have) |

4. **Roadmap signals** — What's their next 1-2 quarters look like? Inferred from: changelog cadence, beta announcements, conference talks, job postings, executive interviews, GitHub activity (if applicable).

5. **Strategic gap classification**
   - **Critical gaps** — features driving lost deals; build or buy
   - **Important gaps** — frequent customer requests; plan for next quarter
   - **Nice-to-have gaps** — table stakes for some segments; deprioritize unless segment matters
   - **Lead opportunities** — features only we have; invest in marketing them

6. **Recommended actions**
   - Build / buy / partner / ignore for each critical gap
   - Investment estimate (T-shirt size: S/M/L)
   - Suggested next step (e.g., "Run `product-management:write-spec` for Critical Gap #1")

## Research sources (in priority order)

1. Competitor's product docs and API reference
2. Pricing & packaging pages (reveals feature tiers)
3. Changelogs and release notes
4. G2/Capterra reviews — sort by 1-star and 5-star to see edge cases
5. Customer-facing sales decks if leaked
6. Trial the product if accessible
7. Patent filings (for hard tech areas)
8. Job postings (engineering roles by domain reveal investment areas)

## Output deliverables

- Feature inventory spreadsheet (CSV or .xlsx)
- Parity matrix (Markdown table + visual)
- Strategic gap classification with recommendations
- Suggested chained skills for follow-through
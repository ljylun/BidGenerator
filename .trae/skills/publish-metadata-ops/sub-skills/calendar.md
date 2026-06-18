# Content Calendar Generator

This sub-skill produces a fully structured monthly content calendar with per-video metadata, evergreen/trending balance checks, Shorts extraction opportunities, and seasonal awareness, translating a channel's content pillars and cadence into a ready-to-execute publishing schedule.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Content pillars | Yes | Pillar names, types (Hub/Hero/Help), and posting frequency from the strategy sub-skill |
| Upload cadence | Yes | Videos per week (long-form and Shorts) |
| Month/timeframe | Yes | Target month or date range for the calendar |
| Seasonal events/launches | No | Holidays, product launches, industry events, personal milestones relevant to content |
| Channel niche | No | For seasonal CPM and trending context (default: inferred from pillars) |
| Creator timezone | No | For publish time optimization (default: US Eastern) |

## Reference Files

- `references/algorithm-guide.md`
- `references/seo-playbook.md`

## DataForSEO Research (When Available)

Use live trend and volume data to optimise calendar timing:

1. **Seasonal trends**: Run `kw_data_google_trends_explore` with the channel's core keywords to identify seasonal peaks and valleys for the target month. Schedule high-demand topics during their peak periods.
2. **Volume prioritisation**: Use `kw_data_google_ads_search_volume` on all planned video keywords to prioritise higher-volume topics earlier in the month for maximum impact.
3. **Rising topic detection**: Run `kw_data_google_trends_explore` with broader niche keywords to spot rising trends that should be added to this month's calendar.

**Fallback:** If DataForSEO is unavailable, use WebSearch for seasonal trends and rely on reference file seasonality data.

**Efficiency:** Typical calendar planning costs ~$0.008 (3-5 API calls).

## Parallel Agents

Not required. This skill runs as a single sequential workflow.

## Execution Steps

1. **Load references**: Read `references/algorithm-guide.md` and `references/seo-playbook.md` for publishing timing data and SEO integration.
2. **Map the month**: If DataForSEO is available, use Google Trends data to identify seasonal peaks for the channel's keyword clusters. Identify the number of publishing weeks, any holidays or seasonal events (both provided and standard), and CPM-relevant periods (Q4 premium, January slump, etc.).
3. **Distribute pillars across weeks**: Assign video slots to each week based on the pillar frequencies and upload cadence. Ensure no single pillar dominates any week.
4. **Generate per-video entries**: For each slot, produce the working title variants, metadata, and production notes.
5. **Assign publish dates and times**: Default to Tuesday/Wednesday/Thursday at 14:00-16:00 local time unless the algorithm guide suggests niche-specific alternatives.
6. **Run balance checks**: Verify evergreen/trending ratio, pillar distribution, and format mix.
7. **Generate Shorts plan**: For each long-form video, identify 2-3 Short clip extraction opportunities.
8. **Add seasonal notes**: Flag CPM windows, holiday content lead times, and any seasonal adjustments.

## Output Template

```
## Calendar Overview: [Month Year]

### Month Context
- **Publishing weeks**: [X] (Week of [date] through Week of [date])
- **Total planned videos**: [X long-form] + [X Shorts] = [X total]
- **Seasonal factors**: [Q4 CPM premium / January slump / holiday lead time / none]
- **Key dates this month**: [Holidays, events, launches — both provided and standard]

---

## Monthly Grid

| Week | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|------|-----|-----|-----|-----|-----|-----|-----|
| Week 1 ([dates]) | — | [Video slot or —] | [Video slot or —] | [Video slot or —] | — | — | — |
| Week 2 ([dates]) | — | [Video slot or —] | [Video slot or —] | [Video slot or —] | — | — | — |
| Week 3 ([dates]) | — | [Video slot or —] | [Video slot or —] | [Video slot or —] | — | — | — |
| Week 4 ([dates]) | — | [Video slot or —] | [Video slot or —] | [Video slot or —] | — | — | — |
| Week 5 ([dates]) | — | [Video slot or —] | [Video slot or —] | [Video slot or —] | — | — | — |

**Legend**: LF = Long-form | SH = Short | LV = Live

---

## Per-Video Entries

### Video 1 — Week 1, [Day] [Date]

| Field | Detail |
|-------|--------|
| **Pillar** | [Pillar name] ([Hub/Hero/Help]) |
| **Format** | [Long-form / Short / Live] |
| **Traffic strategy** | [Search / Browse / Trending] |
| **Target keyword** | [Primary keyword for SEO] |
| **Hook type recommendation** | [Shock / Problem-Agitation / Story / Curiosity / Social Proof] |
| **Estimated production time** | [X hours: research + script + film + edit] |
| **Publish time** | [Day, Date at HH:MM timezone] |

**Working title variants**:
1. [Search-optimized title variant]
2. [Browse/curiosity-driven title variant]
3. [Hybrid title variant]

**Thumbnail concept note**: [One-sentence visual concept — focal point, emotion, text overlay idea]

**Content brief**: [2-3 sentences describing what this video covers and the viewer takeaway]

---

### Video 2 — Week 1, [Day] [Date]
[Same structure as above]

---

### Video 3 — Week 2, [Day] [Date]
[Same structure — continue for ALL videos in the month]

---

[Continue for every video slot in the month...]

---

## Evergreen / Trending Balance Check

| Video | Type | Classification |
|-------|------|---------------|
| [Video 1 title] | [Pillar] | [Evergreen / Trending / Hybrid] |
| [Video 2 title] | [Pillar] | [Evergreen / Trending / Hybrid] |
| ... | ... | ... |

**Balance summary**:
- Evergreen: [X%] of total videos
- Trending: [X%] of total videos
- Hybrid: [X%] of total videos

**Assessment**: [PASS if trending is 30% or less / WARNING if trending exceeds 30% — with specific swap recommendation if WARNING]

---

## Shorts Supplement Plan

### From Video 1: "[Long-form title]"
1. **Short 1**: [Clip concept — which segment, hook, 30-60 second scope]
2. **Short 2**: [Clip concept]
3. **Short 3**: [Clip concept] (optional)

### From Video 2: "[Long-form title]"
1. **Short 1**: [Clip concept]
2. **Short 2**: [Clip concept]

[Continue for each long-form video...]

**Shorts publishing cadence**: [When to publish relative to the long-form video — e.g., "1 Short on publish day, 1 Short two days later"]

---

## Seasonal & Timing Notes

### CPM Awareness
- **Current month CPM context**: [Is this a premium CPM period (Oct-Dec), average (Feb-Sep), or slump (January)?]
- **Implication**: [Adjust content — e.g., "Prioritize monetizable topics this month" or "Use January for experimental/growth content"]

### Holiday & Event Lead Times
| Event | Date | Lead Time Needed | Content Action |
|-------|------|-----------------|----------------|
| [Holiday/event] | [Date] | [X days/weeks before] | [Publish by date X to capture traffic] |

### January Slump Mitigation (if applicable)
- [Strategy for maintaining momentum during low-CPM period]
- [Content types that perform well in January despite lower ad rates]

### Q4 Premium Window (if applicable)
- [Strategy for maximizing revenue during Oct-Dec CPM spike]
- [Content topics with highest RPM potential this month]

---

## Production Timeline

| Week | Pre-Production | Production | Post-Production | Publish |
|------|---------------|------------|-----------------|---------|
| Week 1 | [What to research/script] | [What to film] | [What to edit] | [What goes live] |
| Week 2 | [What to research/script] | [What to film] | [What to edit] | [What goes live] |
| Week 3 | [What to research/script] | [What to film] | [What to edit] | [What goes live] |
| Week 4 | [What to research/script] | [What to film] | [What to edit] | [What goes live] |
```

## Quality Criteria

- Every video slot must have all fields filled — no blank entries or TBD placeholders
- Working title variants must include exactly 3 per video: search-optimized, browse-driven, and hybrid
- Publish times must default to Tuesday/Wednesday/Thursday 14:00-16:00 unless a niche-specific exception is justified
- The evergreen/trending balance must be calculated and flagged if trending content exceeds 30% of total videos
- Each long-form video must have 2-3 Short clip extraction ideas — no fewer than 2
- Seasonal notes must address CPM context for the target month specifically
- Holiday lead times must be calculated backwards from the event date (not just listed)
- The production timeline must be realistic for the stated resource level
- No two consecutive videos should be from the same pillar unless cadence requires it
- The monthly grid must accurately reflect the actual calendar dates for the target month

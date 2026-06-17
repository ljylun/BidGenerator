# Channel Positioning + Content Pillars

This sub-skill builds a complete 90-day channel strategy — positioning statement, content pillar framework, niche viability analysis, upload cadence recommendation, and milestone plan — giving creators a clear, actionable roadmap grounded in data from the reference files and matched to their channel type template.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Creator background | Yes | Skills, expertise, personality, on-camera comfort level |
| Target audience | Yes | Who they want to reach (demographics, interests, problems) |
| Niche | Yes | Content category or micro-niche |
| Current channel state | Yes | Subscriber count, video count, monthly views, upload frequency, time creating |
| Competitive landscape | No | Known competitors, gaps spotted, differentiation ideas |
| Resource level | No | Solo creator, small team (2-3), or full team (4+). Default: solo |
| Primary goal | No | Growth, monetisation, authority, community. Default: growth |

## Reference Files

- `references/algorithm-guide.md`
- `references/analytics-guide.md`
- Also load the relevant channel type template from `templates/` based on niche detection

## DataForSEO Research (When Available)

Ground strategy recommendations in live market data:

1. **Niche viability check**: Run `kw_data_google_ads_search_volume` with 10-15 niche keywords to assess real search demand. High volume + informational intent = strong YouTube niche signal.
2. **Competition depth**: Use `serp_youtube_organic_live_advanced` for 3-5 core niche keywords to see how saturated the YouTube landscape is. Check: are top results from mega-channels or is there diversity?
3. **Trend direction**: Use `kw_data_google_trends_explore` with core niche keywords (last 12 months) to confirm the niche is growing, stable, or declining.
4. **Keyword landscape**: Run `dataforseo_labs_google_keyword_ideas` with niche seeds to discover content pillar opportunities and long-tail keyword clusters.
5. **CPM/CPC validation**: Use CPC data from `kw_data_google_ads_search_volume` as a proxy for advertiser demand (higher CPC = higher YouTube RPM for that topic).

**Fallback:** If DataForSEO is unavailable, rely on reference file benchmarks and WebSearch for trend signals.

**Efficiency:** Typical strategy workflow costs ~$0.03 (8-12 API calls).

## Parallel Agents

Not required. This skill runs as a single sequential workflow.

## Execution Steps

1. **Load references**: Read `references/algorithm-guide.md` and `references/analytics-guide.md` in full.
2. **Detect channel type**: Based on the niche and creator background, identify the matching channel template from `templates/`. Load it for archetype-specific guidance.
3. **Craft positioning statement**: Distill the creator's unique angle into one sentence. Apply the micro-niche-then-expand framework: start specific, plan expansion milestones.
4. **Build content pillars**: Design 3-5 pillars using the Hub/Hero/Help framework. Each pillar gets a name, purpose, cadence, and example ideas.
5. **Assess niche viability**: If DataForSEO data is available, use real search volume, CPC, and trend data to ground viability estimates. Otherwise, estimate CPM range, competition density, content lifespan (evergreen vs trend), and months to monetisation.
6. **Set upload cadence**: Based on channel size tier, resource level, and the vidIQ 5M-channel study data referenced in the algorithm guide. Provide the specific reasoning.
7. **Define milestones**: Create concrete, measurable targets for 30, 60, and 90 days. Tie each to specific actions.

## Output Template

```
## Positioning Statement

> [One sentence: "[Creator] helps [target viewer] achieve [outcome] through [unique angle/format] that [differentiator from competitors]."]

### Positioning Breakdown
- **Unique angle**: [What makes this creator's perspective different]
- **Target viewer**: [Specific person, not a demographic — e.g., "first-time homebuyers overwhelmed by conflicting advice"]
- **Differentiation**: [What competitors do NOT offer that this channel will]
- **Micro-niche start**: [The narrow starting point]
- **Expansion path**: [How the niche broadens at 10K, 50K, 100K subscribers]

---

## Content Pillar Framework (Hub / Hero / Help)

### Pillar 1: [Pillar Name] — [Hub/Hero/Help]
- **Purpose**: [What this pillar does for the channel — audience building, authority, search traffic, etc.]
- **Format**: [Video format — tutorial, commentary, review, list, etc.]
- **Posting frequency**: [X per week/month]
- **Target traffic source**: [Search/Browse/Suggested]
- **Example videos**:
  1. [Working title + one-line concept]
  2. [Working title + one-line concept]
  3. [Working title + one-line concept]

### Pillar 2: [Pillar Name] — [Hub/Hero/Help]
- **Purpose**: [What this pillar does]
- **Format**: [Video format]
- **Posting frequency**: [X per week/month]
- **Target traffic source**: [Search/Browse/Suggested]
- **Example videos**:
  1. [Working title + one-line concept]
  2. [Working title + one-line concept]
  3. [Working title + one-line concept]

### Pillar 3: [Pillar Name] — [Hub/Hero/Help]
[Same structure]

### Pillar 4: [Pillar Name] — [Hub/Hero/Help] (if applicable)
[Same structure]

### Pillar 5: [Pillar Name] — [Hub/Hero/Help] (if applicable)
[Same structure]

### Pillar Balance Check
| Pillar | Type | Monthly Videos | % of Output |
|--------|------|---------------|-------------|
| [Name] | [Hub/Hero/Help] | [X] | [X%] |
| [Name] | [Hub/Hero/Help] | [X] | [X%] |
| [Name] | [Hub/Hero/Help] | [X] | [X%] |
| **Total** | — | **[X]** | **100%** |

**Balance assessment**: [Is the Hub/Hero/Help ratio appropriate for this channel's size and goals? Recommended: ~70% Hub, 15% Help, 15% Hero for growth-stage channels]

---

## Niche Viability Analysis

| Factor | Assessment | Detail |
|--------|-----------|--------|
| **Estimated CPM range** | $[X] — $[Y] | [Source: niche benchmarks from reference files] |
| **Competition density** | [Low/Medium/High/Saturated] | [How many established channels, barrier to entry] |
| **Content lifespan** | [Evergreen-heavy / Mixed / Trend-dependent] | [What % of content will drive views 6+ months later] |
| **Audience demand** | [Growing/Stable/Declining] | [Search trend direction, audience size signals] |
| **Monetisation timeline** | [X-Y months to YPP] | [Based on current state + proposed cadence] |
| **Sponsorship potential** | [Low/Medium/High] | [Brand interest level in this niche] |
| **Diversification options** | [List 2-3] | [Courses, products, affiliates, memberships, etc.] |

**Viability verdict**: [Strong/Moderate/Challenging] — [one-sentence summary with the single biggest risk and biggest opportunity]

---

## Upload Cadence Recommendation

**Recommended cadence**: [X long-form videos per week] + [Y Shorts per week]

### Justification
- **Channel size tier** ([tier]): [What the data says about optimal frequency for this tier]
- **Resource level** ([solo/small team/full team]): [Sustainable output at this resource level]
- **vidIQ 5M-channel study finding**: [Specific data point from algorithm guide supporting this cadence]
- **Quality threshold**: [Minimum quality bar — it's better to post less at higher quality than more at lower]

### Weekly Production Schedule
| Day | Activity | Output |
|-----|----------|--------|
| [Day] | [Activity] | [Deliverable] |
| [Day] | [Activity] | [Deliverable] |
| [Day] | [Activity] | [Deliverable] |
| [Day] | [Activity] | [Deliverable] |
| [Day] | [Activity] | [Deliverable] |

---

## 30/60/90 Day Milestones

### Day 30 Milestones
| Milestone | Target | Action Required |
|-----------|--------|----------------|
| Videos published | [X] | [Stick to cadence] |
| Subscribers | [+X from current] | [Specific growth action] |
| Avg views per video | [X] | [SEO + promotion strategy] |
| Avg CTR | [X%] | [Thumbnail/title optimization] |
| Channel identity | [Established] | [Consistent branding, banner, about page] |

### Day 60 Milestones
| Milestone | Target | Action Required |
|-----------|--------|----------------|
| Total videos | [X] | [Cumulative] |
| Subscribers | [+X from current] | [Growth compounds if content is consistent] |
| Top-performing video views | [X] | [Identify what works, double down] |
| Avg AVD | [X%] | [Script and pacing improvements] |
| Community signals | [X comments/video avg] | [Engagement strategy] |

### Day 90 Milestones
| Milestone | Target | Action Required |
|-----------|--------|----------------|
| Total videos | [X] | [Cumulative] |
| Subscribers | [+X from current] | [Growth target] |
| Monthly views | [X] | [Total monthly channel views] |
| Monetisation status | [YPP eligible / on track] | [Revenue readiness] |
| Content system | [Documented] | [Repeatable production workflow] |

---

## Channel Type Template Reference

**Detected channel type**: [Type name]
**Template file**: `templates/[filename]`
**Key template guidance applied**: [2-3 bullet points on how the template influenced this strategy]
```

## Quality Criteria

- The positioning statement must be exactly one sentence and include all four elements: creator, viewer, outcome, differentiator
- Content pillars must follow the Hub/Hero/Help framework with each pillar explicitly labeled
- Each pillar must include exactly 3 example video ideas with working titles
- The pillar balance check must flag imbalances (e.g., all Hub, no Help)
- Niche viability must include a CPM range estimate grounded in reference file data
- Upload cadence must cite the vidIQ 5M-channel study or equivalent data from the algorithm guide
- All 30/60/90 milestones must be numeric and measurable — no vague goals like "grow audience"
- Milestones must be realistic for the stated channel size and resource level
- The micro-niche expansion path must include specific subscriber thresholds for broadening
- The strategy must reference the detected channel type template with specific guidance pulled from it

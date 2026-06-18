# Ideate Sub-Skill

This sub-skill generates 10 data-informed video ideas ranked by a composite score of search demand, CTR potential, production feasibility, and niche fit. Each idea comes with a complete brief — keyword analysis, traffic strategy, hook angle, thumbnail concept, and revenue potential — so the creator can move directly from ideation to production without additional research.

## Inputs Required

- **Channel niche** (string): content category
- **Recent top-performing videos** (list, optional): titles and view counts of the creator's best recent videos
- **Audience pain points** (list, optional): known problems, frustrations, or questions from the target audience
- **Trending topics** (list, optional): current trends in the niche or broader culture
- **Competitor top videos** (list, optional): titles and view counts from competitor channels
- **Content the creator wants to avoid** (optional): topics or formats to exclude

## Reference Files to Load

- `references/algorithm-guide.md`
- `references/seo-playbook.md`
- `references/analytics-guide.md`

## DataForSEO Research (When Available)

Before generating ideas, gather live data to ground ideation in real demand:

1. **Trend discovery**: Use `kw_data_google_trends_explore` with 3-5 seed keywords from the niche to identify rising topics. Compare last 12 months. Rising trends = urgent ideas; declining = avoid.
2. **Keyword ideas**: Use `dataforseo_labs_google_keyword_ideas` and `dataforseo_labs_google_keyword_suggestions` with niche seed keywords to discover what people actually search for.
3. **YouTube SERP competition**: For each promising keyword, run `serp_youtube_organic_live_advanced` to check:
   - How many videos rank? What are their view counts?
   - Are top results from mega-channels or small creators? (opportunity signal)
   - What's the Shorts vs long-form ratio in results?
   - What title patterns dominate?
4. **Volume + difficulty**: Batch all candidate keywords into `kw_data_google_ads_search_volume` and `dataforseo_labs_bulk_keyword_difficulty` to get real numbers instead of estimated tiers.
5. **Intent classification**: Run `dataforseo_labs_search_intent` on candidates to match traffic strategy (informational → search-first, commercial → monetisation opportunity).

**Fallback:** If DataForSEO is unavailable, use WebSearch with queries like "[niche] trending topics 2025 2026" and rely on manual keyword assessment.

**Efficiency:** Batch all keywords into single calls. Typical ideation costs ~$0.01 (5-8 API calls).

## Parallel Agents

Not required. Execute sequentially.

## Step-by-Step Execution

1. Load all three reference files. Internalise keyword strategy, algorithm recommendation signals, traffic source mechanics, and content performance patterns.
2. Analyse the creator's top-performing videos (if provided) to identify what works: topic patterns, title structures, content formats, and audience signals. These inform ideas that build on proven success.
3. Map audience pain points to searchable topics. Each pain point represents validated demand — convert these into specific video concepts.
4. Assess trending topics for relevance and timing. Separate flash trends (must publish this week) from sustained trends (rising search interest over months). Flag seasonal deadlines.
5. Analyse competitor top videos (if provided) to identify proven topics with room for a better or different take.
6. Generate 10 video ideas. For each idea, determine the optimal traffic strategy: Search-first (targeting specific keyword intent), Browse-first (optimising for CTR and watch time to trigger algorithm recommendations), or Trending (capitalising on current interest spikes).
7. For each idea, assess keyword viability. If DataForSEO is available, use real volume and difficulty data from the research phase. Otherwise, assess competition level (Low/Medium/High based on existing content volume and channel authority of rankers), estimated monthly search volume tier (Low: under 1K, Medium: 1K-10K, High: 10K+), and Google Trends direction (Rising/Stable/Declining).
8. Craft a hook angle for each idea — one sentence that captures the curiosity gap or value proposition that will make viewers click and stay.
9. Design a thumbnail concept for each idea — a 15-word visual description specific enough for a designer to start working.
10. Estimate content length based on topic depth, niche norms, and search intent (how-to queries need completeness; opinion content can be shorter).
11. Assess revenue potential: estimate the RPM tier based on advertiser demand for the topic (some topics within a niche attract significantly higher CPMs).
12. Assign an urgency flag to each idea and rank all 10 by composite score.

## Output Template

```markdown
## Video Ideas: [Niche]

**Generated from**: [List data sources used — top videos, pain points, trends, competitor data]
**Ideas ranked by**: Search Demand x CTR Potential x Production Feasibility x Niche Fit

---

### Idea 1: [Working Title]

| Attribute | Value |
|-----------|-------|
| **Title** | [Keyword-optimised, max 100 chars] |
| **Traffic strategy** | [Search-first / Browse-first / Trending] |
| **Keyword** | [Primary keyword] |
| **Competition** | [Low / Medium / High] |
| **Search volume tier** | [Low (<1K) / Medium (1K-10K) / High (10K+)] |
| **Trends direction** | [Rising / Stable / Declining] |
| **Content length** | [Estimated minutes] |
| **RPM tier** | [Low ($2-5) / Medium ($5-12) / High ($12-30) / Premium ($30+)] |
| **Urgency** | [Trending: make this week / Evergreen: any time / Seasonal: deadline noted] |
| **Composite score** | [N/40] |

**Hook angle**: [One sentence — the curiosity gap or value proposition]

**Thumbnail concept**: [15-word visual description — subject, emotion, text, colours]

**Why this idea**: [1-2 sentences connecting it to the creator's data — what signal suggests this will perform]

**Source**: [What input data this idea came from — top video pattern, pain point, trend, competitor gap]

---

### Idea 2: [Working Title]

*(Same structure repeated for all 10 ideas)*

---

*(Ideas 3-10 follow the same format)*

---

### Ranking Summary

| Rank | Title | Strategy | Score | Urgency |
|------|-------|----------|-------|---------|
| 1 | [Title] | [Strategy] | [N/40] | [Flag] |
| 2 | [Title] | [Strategy] | [N/40] | [Flag] |
| 3 | [Title] | [Strategy] | [N/40] | [Flag] |
| 4 | [Title] | [Strategy] | [N/40] | [Flag] |
| 5 | [Title] | [Strategy] | [N/40] | [Flag] |
| 6 | [Title] | [Strategy] | [N/40] | [Flag] |
| 7 | [Title] | [Strategy] | [N/40] | [Flag] |
| 8 | [Title] | [Strategy] | [N/40] | [Flag] |
| 9 | [Title] | [Strategy] | [N/40] | [Flag] |
| 10 | [Title] | [Strategy] | [N/40] | [Flag] |

### Production Priority

**Make this week** (time-sensitive):
- [List any ideas flagged as Trending or Seasonal with approaching deadlines]

**Next in queue** (highest evergreen scores):
- [Top 2-3 evergreen ideas by composite score]

**Backlog** (solid ideas, no urgency):
- [Remaining ideas]

### Content Calendar Suggestion

| Week | Video | Strategy | Rationale |
|------|-------|----------|-----------|
| Week 1 | [Title] | [Strategy] | [Why this week] |
| Week 2 | [Title] | [Strategy] | [Why] |
| Week 3 | [Title] | [Strategy] | [Why] |
| Week 4 | [Title] | [Strategy] | [Why] |
```

## Quality Criteria

- All 10 ideas are distinct in topic and angle — no near-duplicates or minor variations
- Every title is under 100 characters and includes the target keyword
- Traffic strategies are justified by the topic type (how-to = search-first, opinion = browse-first, news = trending)
- Keyword competition assessment reflects realistic analysis, not arbitrary labels
- Search volume tiers use defined thresholds: Low (<1K), Medium (1K-10K), High (10K+)
- Trends direction is based on observable patterns, not guesses
- Hook angles create genuine curiosity gaps or clear value propositions — not generic statements
- Thumbnail concepts are specific enough for a designer to start (15 words, covering subject, emotion, text, colours)
- Content length estimates match niche norms and topic depth
- RPM tiers reflect advertiser demand for the specific topic, not just the niche average
- Urgency flags are used correctly: Trending only for genuinely time-sensitive topics, Seasonal only with a stated deadline
- Composite scores are internally consistent — higher-scored ideas are clearly stronger across dimensions
- Ideas draw from the provided input data with explicit attribution (not generic niche ideas)
- Content calendar accounts for production complexity and alternates between strategies
- At least 3 different traffic strategies are represented across the 10 ideas

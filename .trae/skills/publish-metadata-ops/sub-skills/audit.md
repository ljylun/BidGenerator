# Channel Health Audit

This sub-skill performs a comprehensive channel health audit by spawning four parallel analysis agents — Technical SEO, Performance, Content Strategy, and Monetisation — each loading dedicated reference material, then synthesizing their findings into a scored report card with prioritized fixes and a concrete 30-day action plan.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Channel URL/handle | Yes | YouTube channel URL or @handle |
| Channel niche | Yes | Primary content category (e.g., tech reviews, cooking, fitness) |
| Channel size tier | Yes | Nano (<1K), Micro (1K-10K), Small (10K-100K), Mid (100K-500K), Large (500K-1M), Mega (1M+) |
| Primary goal | Yes | Growth, monetisation, authority, community, or hybrid |

## Reference Files

- `references/seo-playbook.md` (Agent A)
- `references/analytics-guide.md` (Agent B)
- `references/algorithm-guide.md` (Agent C)
- `references/monetization-guide.md` (Agent D)

## DataForSEO Research (When Available)

DataForSEO significantly enhances audit depth with live YouTube and keyword data:

1. **YouTube SERP positioning**: For each of the channel's recent video topics, run `serp_youtube_organic_live_advanced` to check if the channel's videos actually appear in YouTube search results. This reveals SEO effectiveness.
2. **Video intelligence**: Use `serp_youtube_video_info_live_advanced` on the channel's recent videos to get full metadata including tags, category classification, and engagement ratios — richer than the YouTube Data API alone.
3. **Keyword coverage audit**: Extract keywords from the channel's video titles, batch into `kw_data_google_ads_search_volume` to see if the channel targets high-demand keywords or wastes effort on zero-volume terms.
4. **Keyword difficulty**: Run `dataforseo_labs_bulk_keyword_difficulty` on the channel's target keywords to assess if they're targeting achievable keywords for their authority level.
5. **Competitor benchmarking**: Use `serp_youtube_organic_live_advanced` on the channel's core keywords to see who else ranks — identify if competitors are dominating the same keyword space.

**Fallback:** If DataForSEO is unavailable, use `execution/fetch_channel_data.py` and WebSearch for competitive context.

**Efficiency:** Typical audit costs ~$0.04 (8-15 API calls). Use batch endpoints for keywords.

## Parallel Agent Architecture

This skill MUST use 4 parallel agents. Launch all four simultaneously using the Agent tool. Do NOT run them sequentially.

### Agent A: Technical SEO Audit
- **Loads**: `references/seo-playbook.md`
- **Scope**: Last 20 videos
- **Analyzes**: Title keyword placement and length, description structure (first 150 chars, links, hashtags), tag coverage and relevance, chapter/timestamp presence and keyword density, hashtag usage (count, relevance, branded vs generic), thumbnail text presence (inferred from titles), metadata completeness score per video
- **Outputs**: SEO score (A-F), list of specific deficiencies, top 5 quick metadata fixes

### Agent B: Performance Analysis
- **Loads**: `references/analytics-guide.md`
- **Scope**: Channel-level and per-video metrics
- **Analyzes**: CTR vs niche benchmarks (reference file provides benchmarks by category), average view duration vs 40% video length threshold, impressions-to-views funnel efficiency, traffic source distribution (Search/Browse/Suggested/External percentages), subscriber conversion rate, views-per-hour velocity in first 48h (if inferrable)
- **Outputs**: Performance score (A-F), funnel bottleneck identification, benchmark comparison table

### Agent C: Content Strategy Review
- **Loads**: `references/algorithm-guide.md`
- **Scope**: Last 30-60 days of uploads
- **Analyzes**: Upload cadence (actual vs recommended for tier), niche consistency vs topic drift, series vs standalone ratio, playlist structure and completeness, evergreen vs trending content balance, content format mix (long-form, Shorts, live)
- **Outputs**: Strategy score (A-F), cadence recommendation, content mix adjustment

### Agent D: Monetisation Assessment
- **Loads**: `references/monetization-guide.md`
- **Scope**: Channel monetisation posture
- **Analyzes**: YPP eligibility status and tier (standard vs expanded), revenue stream count and diversification, RPM estimate vs niche benchmarks, sponsorship readiness (media kit signals, contact info, audience size), affiliate and product integration gaps, membership/Super Chat utilization
- **Outputs**: Monetisation score (A-F), revenue gap analysis, top 2 untapped streams

## Execution Steps

1. **Collect channel data**: Run `execution/fetch_channel_data.py` with the provided channel URL/handle. Additionally, if DataForSEO is available, use `serp_youtube_video_info_live_advanced` on key videos for deeper metadata (tags, engagement, category). Capture channel metadata, recent video list, and available public metrics.
2. **Detect channel type**: From the collected data and stated niche, determine the channel archetype. Load the matching template from `templates/` for context-aware benchmarking.
3. **Launch 4 parallel agents**: Each agent receives the collected channel data plus its specific reference file. All four run simultaneously.
4. **Synthesize results**: Once all agents return, merge their findings into the unified output format below. Resolve any conflicting recommendations by prioritizing impact on the stated primary goal.
5. **Score calibration**: Cross-reference all scores against benchmarks in the reference files. No score may be assigned without a specific benchmark justification.
6. **Generate action plan**: Rank all recommended fixes by estimated impact (high/medium/low) crossed with effort (quick win/moderate/heavy lift). The 30-day plan prioritizes high-impact quick wins first.

## Output Template

```
## Executive Summary

[Three sentences maximum. Sentence 1: Channel's current position and strongest asset. Sentence 2: The single biggest bottleneck limiting growth. Sentence 3: The highest-leverage change available right now.]

## Score Card

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Technical SEO | [A-F] | [One-line justification referencing specific benchmark] |
| Performance | [A-F] | [One-line justification referencing specific benchmark] |
| Content Strategy | [A-F] | [One-line justification referencing specific benchmark] |
| Monetisation | [A-F] | [One-line justification referencing specific benchmark] |
| **Overall** | **[A-F]** | **[Weighted average explanation]** |

## Top 3 Critical Fixes

### 1. [Fix Title] — Impact: [High/Critical]
- **Problem**: [Specific issue with data point]
- **Benchmark gap**: [Current metric] vs [benchmark from reference file]
- **Action**: [Exact steps to implement]
- **Expected result**: [Projected improvement with timeframe]

### 2. [Fix Title] — Impact: [High/Critical]
[Same structure]

### 3. [Fix Title] — Impact: [High/Critical]
[Same structure]

## 30-Day Action Plan

### Week 1: Quick Wins
- [ ] [Specific action with measurable outcome]
- [ ] [Specific action with measurable outcome]
- [ ] [Specific action with measurable outcome]

### Week 2: Foundation Fixes
- [ ] [Specific action with measurable outcome]
- [ ] [Specific action with measurable outcome]

### Week 3: Optimization
- [ ] [Specific action with measurable outcome]
- [ ] [Specific action with measurable outcome]

### Week 4: Measurement & Adjustment
- [ ] [Specific action with measurable outcome]
- [ ] [Review metrics and adjust]

## 90-Day Growth Projection

| Metric | Current (Est.) | 30-Day Target | 60-Day Target | 90-Day Target |
|--------|---------------|---------------|---------------|---------------|
| Monthly views | [X] | [Y] | [Z] | [W] |
| Subscribers | [X] | [Y] | [Z] | [W] |
| Avg CTR | [X%] | [Y%] | [Z%] | [W%] |
| Avg AVD | [X%] | [Y%] | [Z%] | [W%] |
| Est. Monthly Revenue | [X] | [Y] | [Z] | [W] |

*Projections assume consistent implementation of the action plan and [X uploads/week] cadence.*

## Detailed Agent Reports

### Technical SEO Report
[Full Agent A output]

### Performance Report
[Full Agent B output]

### Content Strategy Report
[Full Agent C output]

### Monetisation Report
[Full Agent D output]
```

## Quality Criteria

- Every letter grade MUST cite a specific benchmark from the loaded reference file
- The executive summary must be exactly 3 sentences — no more, no less
- All 30-day actions must be specific and measurable (no vague advice like "improve thumbnails")
- Growth projections must be conservative and grounded in the channel's current trajectory plus benchmark improvement rates from reference files
- The top 3 fixes must be ranked strictly by impact, not by ease of implementation
- No recommendations may contradict each other across agent reports — resolve conflicts in synthesis
- Channel size tier must influence all benchmarks (do not compare a 5K channel against 500K benchmarks)
- If data is unavailable or estimated, mark it explicitly with [estimated] or [data unavailable]

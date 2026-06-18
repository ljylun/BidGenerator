# Analyze Sub-Skill

This sub-skill interprets raw YouTube channel analytics data — whether from screenshots, CSV exports, or verbally described metrics — and transforms it into a structured diagnosis of channel health with a prioritised action plan. It maps data points to known algorithm signals, identifies funnel leaks, classifies retention patterns, and produces maximum 5 high-impact actions the creator can execute immediately.

## Inputs Required

- **Channel analytics data** (any format): YouTube Studio screenshots, CSV/spreadsheet data, or described metrics (views, CTR, watch time, retention %, traffic sources, subscriber changes, revenue)
- **Time period** (optional): date range for the data (defaults to last 28 days)
- **Channel niche** (optional): for benchmarking against niche averages
- **Specific concerns** (optional): areas the creator wants focused attention on

## Reference Files to Load

- `references/analytics-guide.md`
- `references/algorithm-guide.md`

## DataForSEO Research (When Available)

Enhance analytics interpretation with external data:

1. **YouTube SERP check**: For the channel's key videos, run `serp_youtube_organic_live_advanced` with their target keywords to check if they appear in search results. A video with low views but no SERP presence = SEO problem; a video in top 5 SERP but low views = keyword demand problem.
2. **Video deep-dive**: Use `serp_youtube_video_info_live_advanced` on specific videos the user wants analysed to get full metadata, engagement metrics, and tags.
3. **Keyword validation**: If the user provides video topics, run `dataforseo_labs_google_keyword_overview` to check if those keywords have real search demand. Low-demand keywords explain low search traffic.

**Fallback:** If DataForSEO is unavailable, rely on user-provided analytics data and WebSearch for contextual benchmarks.

**Efficiency:** Typical analysis costs ~$0.008 (2-4 API calls).

## Parallel Agents

Not required. Execute sequentially.

## Step-by-Step Execution

1. Load both reference files. Internalise metric benchmarks, algorithm signals, retention pattern classifications, and traffic source implications.
2. Extract all available metrics from the provided data. Normalise into a consistent format regardless of input type (screenshot, CSV, or verbal).
3. Build the funnel diagnosis: Impressions to CTR to Views to Watch Time. Calculate each conversion step and identify where the biggest drop-off occurs. Cross-reference CTR and watch time benchmarks from the analytics guide.
4. Classify retention graph patterns. If retention data is available, match each video's curve to known types: cliff (hook failure within first 30 seconds), valley (pacing issue at a specific point), bump (rewatch segment), suspension bridge (strong open and close, dip in middle), sawtooth (repeated engagement spikes), steady decline (normal healthy pattern). Provide specific timestamps where issues occur if visible.
5. Analyse traffic source distribution. Calculate percentage from each source (Browse, Search, Suggested, External, Shorts feed, etc.). Flag over-reliance on any single source (above 60%). Map traffic source health to algorithm signals — is the algorithm actively recommending this channel? If DataForSEO is available, cross-reference with `serp_youtube_organic_live_advanced` to check whether the channel's videos appear in YouTube search results for their target keywords — this explains search traffic share.
6. Identify content performance outliers. Find the best and worst performing videos by views, CTR, and watch time. Extract patterns: what topic, format, length, thumbnail style, title structure, and upload timing correlate with high or low performance.
7. If revenue data is available, perform RPM analysis. Compare channel RPM to niche benchmarks. Identify which video types or topics earn disproportionately higher RPM and why.
8. Synthesise findings into a priority action list of maximum 5 items, ranked by impact-to-effort ratio.

## Output Template

```markdown
## Channel Analytics Report

**Period**: [Date range]
**Data sources**: [Screenshots / CSV / Described metrics]

---

### 1. Funnel Diagnosis

| Stage | Value | Benchmark | Status |
|-------|-------|-----------|--------|
| Impressions | [N] | — | [Trend: up/down/flat] |
| CTR | [X%] | [Niche avg: Y%] | [Above/Below/At benchmark] |
| Views | [N] | — | [Trend] |
| Avg Watch Time | [M:SS] | — | [Trend] |
| Avg % Viewed | [X%] | [Niche avg: Y%] | [Above/Below] |

**Primary funnel leak**: [Stage where biggest drop-off occurs]
**Diagnosis**: [Why this leak is happening — specific, evidence-based]

---

### 2. Retention Patterns

| Video | Pattern Type | Key Moment | Interpretation |
|-------|-------------|------------|----------------|
| "[Title]" | [Cliff/Valley/Bump/etc.] | [Timestamp] | [What happened and why] |
| ... | ... | ... | ... |

**Recurring pattern**: [If multiple videos share the same retention issue, call it out]
**Fix**: [Specific action to address the dominant retention pattern]

---

### 3. Traffic Source Health

| Source | Share | Trend | Health Signal |
|--------|-------|-------|---------------|
| Browse Features | [X%] | [Up/Down/Flat] | [Algorithm actively recommending / Not recommending] |
| YouTube Search | [X%] | ... | ... |
| Suggested Videos | [X%] | ... | ... |
| External | [X%] | ... | ... |
| Shorts Feed | [X%] | ... | ... |
| Other | [X%] | ... | ... |

**Over-reliance warning**: [Flag if any source exceeds 60%]
**Algorithm health**: [Overall assessment — is YouTube pushing this channel?]

---

### 4. Content Performance Outliers

**Top performers**:
| Video | Views | CTR | Watch Time | Why It Worked |
|-------|-------|-----|------------|---------------|
| "[Title]" | [N] | [X%] | [M:SS] | [Specific factors] |
| ... | ... | ... | ... | ... |

**Underperformers**:
| Video | Views | CTR | Watch Time | Why It Underperformed |
|-------|-------|-----|------------|----------------------|
| "[Title]" | [N] | [X%] | [M:SS] | [Specific factors] |
| ... | ... | ... | ... | ... |

**Patterns**: [Common traits of winners vs losers — topic, format, length, thumbnail, timing]

---

### 5. Revenue Analysis
> *(included only if revenue data is provided)*

| Metric | Value | Niche Benchmark |
|--------|-------|-----------------|
| Channel RPM | $[X.XX] | $[Y.YY] |
| Monthly Revenue | $[N] | — |
| Top Earning Video | "[Title]" — $[N] | — |

**High-RPM content types**: [Which formats/topics earn disproportionately more]
**Revenue opportunity**: [Untapped revenue potential based on current traffic]

---

### 6. Priority Action List

| # | Action | Why | How to Measure | Timeline |
|---|--------|-----|----------------|----------|
| 1 | [Highest impact action] | [Evidence from data] | [Specific metric to track] | [This week / This month] |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |
| 4 | ... | ... | ... | ... |
| 5 | ... | ... | ... | ... |

**Impact-to-effort ranking**: Actions are ordered by expected improvement per hour of effort.
```

## Quality Criteria

- Every diagnosis must be tied to specific data points, never generic advice
- Funnel diagnosis identifies exactly one primary leak with evidence
- Retention patterns use the correct classification names from the analytics guide
- Traffic source percentages must sum to approximately 100%
- Over-reliance warnings trigger at 60%+ from a single source
- Content outlier analysis explains WHY, not just WHAT
- Action list is capped at 5 items — no padding with low-impact actions
- Each action includes a measurable outcome and timeline
- Revenue analysis uses realistic niche RPM benchmarks from the monetization guide
- If data is incomplete, explicitly state what is missing and how it limits the analysis

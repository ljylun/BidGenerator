# Competitor Sub-Skill

This sub-skill performs a multi-dimensional competitor gap analysis by spawning four parallel agents that each investigate a distinct competitive dimension — top video patterns, keyword gaps, format gaps, and audience unmet needs. The combined output reveals specific, actionable content opportunities that competitors have validated with their audience but left gaps the creator can exploit.

## Inputs Required

- **Competitor channels** (list, max 3): channel names or URLs to analyse
- **User's channel niche** (string): the creator's content category
- **User's channel URL or name** (optional): for direct comparison
- **User's recent video titles** (optional): for keyword gap analysis

## Reference Files to Load

- `references/seo-playbook.md`
- `references/algorithm-guide.md`

## DataForSEO Research (When Available)

DataForSEO provides far richer competitor intelligence than the YouTube Data API alone. When available, use it as the PRIMARY data source for competitor analysis:

1. **YouTube SERP mapping**: For each competitor's known keywords (extracted from their titles), run `serp_youtube_organic_live_advanced` to see where competitors rank vs where they don't. This builds the keyword gap map with real ranking data.
2. **Video deep-dive**: Use `serp_youtube_video_info_live_advanced` on competitor top videos to get full metadata: tags, category, exact view/like/comment counts, duration, and publication date.
3. **Comment mining**: Use `serp_youtube_video_comments_live_advanced` on competitor videos (Agent D) to extract audience complaints, questions, and content requests without needing YouTube API OAuth.
4. **Transcript analysis**: Use `serp_youtube_video_subtitles_live_advanced` on competitor top videos to understand their content structure, talking points, and hooks.
5. **Keyword expansion**: Run `dataforseo_labs_google_keyword_ideas` with niche seed keywords to discover keyword opportunities neither the user nor competitors are targeting.
6. **Volume + difficulty for gaps**: Batch all identified keyword gaps into `kw_data_google_ads_search_volume` and `dataforseo_labs_bulk_keyword_difficulty` to quantify the opportunity.
7. **Trend validation**: Use `kw_data_google_trends_explore` on top keyword gaps to confirm they're rising, not declining.

**Fallback:** If DataForSEO is unavailable, use `execution/search_competitor_videos.py` (YouTube Data API, 100 units/search) and WebSearch.

**Efficiency:** Typical competitor analysis costs ~$0.02 (6-10 API calls). Use video_info in batches where possible.

## Parallel Agents

**Yes — spawn 4 parallel agents.** Each agent operates independently and produces its own section of the final output. Use DataForSEO YouTube tools (`serp_youtube_organic_live_advanced`, `serp_youtube_video_info_live_advanced`, `serp_youtube_video_comments_live_advanced`) as the primary data source. Fall back to `execution/search_competitor_videos.py` if DataForSEO is unavailable.

### Agent A: Top Video Analysis
- Retrieve each competitor's top 10 videos by view count
- Extract common title patterns (structures, power words, number usage)
- Categorise thumbnail styles (face vs no-face, text overlay patterns, colour schemes)
- Identify topic clusters that dominate their top content
- Note average video length of top performers

### Agent B: Keyword Gap
- Extract keywords and topics from competitor video titles and descriptions
- Cross-reference against the user's existing content
- Identify keywords and topics that competitors rank for but the user does not cover
- Assess keyword difficulty and search volume tier for each gap

### Agent C: Format Gap
- Catalogue content formats each competitor uses (tutorial, listicle, reaction, review, vlog, comparison, case study, interview, challenge, documentary-style)
- Identify formats that perform above channel average for competitors
- Compare against the user's format repertoire
- Flag high-performing formats the user has never attempted

### Agent D: Audience Gap
- Analyse competitor comment sections on recent videos (last 10-20 videos)
- Extract recurring complaints, unanswered questions, and content requests
- Identify audience frustrations that competitors are not addressing
- Catalogue specific video ideas that viewers are explicitly asking for

## Step-by-Step Execution

1. Load both reference files. Internalise SEO keyword analysis methods and algorithm signals that determine which content gets recommended.
2. Validate competitor channels. Confirm each is in the same or adjacent niche as the user.
3. Spawn all 4 agents in parallel. Each agent uses DataForSEO YouTube tools as the primary data source (`serp_youtube_organic_live_advanced`, `serp_youtube_video_info_live_advanced`, `serp_youtube_video_comments_live_advanced`, `serp_youtube_video_subtitles_live_advanced`). Fall back to `execution/search_competitor_videos.py` if DataForSEO is unavailable.
4. Agent A retrieves top 10 videos per competitor and analyses title/thumbnail/topic patterns.
5. Agent B extracts keywords from competitor content and identifies gaps against the user's existing videos.
6. Agent C catalogues content formats and identifies format opportunities.
7. Agent D scans comment sections for unmet audience needs.
8. Collect all 4 agent outputs and synthesise into the unified report.
9. Generate the content gap map, outlier analysis, quick win opportunities, and differentiation angles from the combined agent data.

## Output Template

```markdown
## Competitor Gap Analysis

**Competitors analysed**: [List of 1-3 competitor channels]
**User's niche**: [Niche]
**Analysis date**: [Date]

---

### 1. Competitor Profiles

| Attribute | [Competitor 1] | [Competitor 2] | [Competitor 3] |
|-----------|----------------|----------------|----------------|
| Subscribers | [N] | [N] | [N] |
| Size tier | [Micro/Small/Mid/Large/Mega] | ... | ... |
| Est. monthly views | [N] | ... | ... |
| Upload frequency | [N/week] | ... | ... |
| Primary strategy | [Search/Browse/Shorts/Mixed] | ... | ... |
| Monetisation approach | [Ads/Sponsors/Products/Mixed] | ... | ... |
| Avg video length | [M:SS] | ... | ... |

---

### 2. Top Video Analysis (Agent A)

**[Competitor 1] — Top 10 by views**:

| # | Title | Views | Length | Topic Cluster |
|---|-------|-------|--------|---------------|
| 1 | [Title] | [N] | [M:SS] | [Cluster] |
| ... | ... | ... | ... | ... |

*(Repeat for each competitor)*

**Title patterns detected**:
- [Pattern 1]: [Example — frequency across top videos]
- [Pattern 2]: [Example — frequency]
- [Pattern 3]: [Example — frequency]

**Thumbnail patterns**:
- [Style 1]: [Description — frequency]
- [Style 2]: [Description — frequency]

**Dominant topic clusters**: [List the 3-5 topic areas that dominate competitor top content]

---

### 3. Content Gap Map (Agent B)

| Topic / Keyword | [Comp 1] | [Comp 2] | [Comp 3] | User | Opportunity |
|-----------------|----------|----------|----------|------|-------------|
| [Keyword 1] | Yes | Yes | No | **No** | HIGH |
| [Keyword 2] | Yes | No | No | **No** | MEDIUM |
| ... | ... | ... | ... | ... | ... |

**Top keyword gaps** (competitor ranks, user does not):
1. **[Keyword]** — Search volume: [Tier], Difficulty: [Low/Med/High], Relevance: [High/Med]
2. ...
3. ...
4. ...
5. ...

---

### 4. Format Gap (Agent C)

| Format | [Comp 1] Avg Perf | [Comp 2] Avg Perf | [Comp 3] Avg Perf | User Uses? |
|--------|-------------------|-------------------|-------------------|------------|
| Tutorial | [Above/At/Below avg] | ... | ... | [Yes/No] |
| Listicle | ... | ... | ... | ... |
| Comparison | ... | ... | ... | ... |
| Case Study | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

**Format opportunities** (high competitor performance, user has not tried):
1. **[Format]** — Why it works: [Reasoning], Adaptation suggestion: [How user can make it their own]
2. ...
3. ...

---

### 5. Audience Gap (Agent D)

**Recurring complaints in competitor comments**:
1. "[Complaint/frustration]" — Frequency: [Common/Occasional], Opportunity: [Description]
2. ...
3. ...

**Unanswered questions**:
1. "[Question viewers keep asking]" — Video idea: [Title concept]
2. ...
3. ...

**Explicitly requested content**:
1. "[What viewers asked for]" — Times seen: [N], Competitor response: [Addressed/Ignored]
2. ...
3. ...

---

### 6. Outlier Video Analysis

Videos performing 3x+ above the competitor's channel average:

| Video | Channel | Views | Channel Avg | Multiple | Why It's an Outlier |
|-------|---------|-------|-------------|----------|-------------------|
| "[Title]" | [Comp] | [N] | [N] | [Xx] | [Specific factors] |
| ... | ... | ... | ... | ... | ... |

**Replicability assessment**: [Which outlier strategies can the user adapt, which are one-time events]

---

### 7. Quick Win Opportunities

Top 5 video ideas based on validated competitor demand with gaps:

| # | Video Idea | Source | Difficulty | Expected Impact |
|---|-----------|--------|------------|-----------------|
| 1 | [Title concept] | [Which gap: keyword/format/audience] | [Easy/Medium/Hard] | [High/Medium] |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |
| 4 | ... | ... | ... | ... |
| 5 | ... | ... | ... | ... |

---

### 8. Differentiation Angles

How to cover the same topics as competitors while standing out:

1. **[Angle]**: [Description — how this creates distinct positioning]
2. **[Angle]**: [Description]
3. **[Angle]**: [Description]
```

## Quality Criteria

- All 4 agents produce output; no section is left empty or marked as unavailable
- Competitor profiles include realistic estimates, not fabricated precision
- Content gap map shows clear opportunities where competitors have coverage and the user does not
- Keyword gaps include difficulty and search volume assessments, not just topic names
- Format gap analysis compares performance relative to channel average, not absolute views
- Audience gap findings come from comment analysis patterns, not assumptions
- Outlier videos must be 3x+ channel average to qualify; the threshold is not lowered
- Quick win opportunities are validated by at least two data points (keyword demand + audience request, or competitor success + format gap)
- Differentiation angles are specific and actionable, not generic advice like "be authentic"
- The analysis does not recommend copying competitors; it identifies gaps and unique positioning

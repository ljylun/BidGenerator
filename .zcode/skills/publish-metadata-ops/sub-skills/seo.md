# Video SEO Optimization

This sub-skill generates complete, search-optimized metadata for a YouTube video — titles, description, tags, chapters, hashtags, and structured data — all grounded in keyword strategy and algorithm best practices from the reference playbooks.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Topic/keyword | Yes | Primary topic or target keyword for the video |
| Channel niche | Yes | Channel's content category for contextual optimization |
| Target audience | Yes | Who the video is for (demographics, skill level, intent) |
| Video content summary | Yes | Brief overview of what the video covers (key points, structure) |
| Secondary keywords | No | Additional keywords to weave in |
| Video length | No | Approximate duration (affects chapter planning) |

## Reference Files

- `references/seo-playbook.md`
- `references/algorithm-guide.md`

## DataForSEO Research (When Available)

Use live keyword data to ground SEO recommendations in real metrics:

1. **Primary keyword validation**: Run `dataforseo_labs_google_keyword_overview` with the target keyword to get volume, difficulty, CPC, and intent in one call.
2. **Related keywords**: Use `dataforseo_labs_google_keyword_suggestions` and `dataforseo_labs_google_related_keywords` to expand secondary keyword and long-tail lists with real volume data.
3. **YouTube SERP check**: Run `serp_youtube_organic_live_advanced` with the primary keyword to see:
   - What titles/descriptions are working for top-ranking videos
   - Title length and keyword placement patterns of rank #1-5
   - Competition depth (how many high-view videos exist)
4. **Difficulty assessment**: Use `dataforseo_labs_bulk_keyword_difficulty` on all candidate keywords to prioritise achievable targets.
5. **Intent classification**: Run `dataforseo_labs_search_intent` to confirm whether keyword intent matches the video's content type.

**Fallback:** If DataForSEO is unavailable, proceed with keyword analysis based on reference file heuristics and WebSearch.

**Efficiency:** Batch keywords. Typical SEO metadata workflow costs ~$0.008 (3-5 API calls).

## Parallel Agents

Not required. This skill runs as a single sequential workflow.

## Execution Steps

1. **Load references**: Read `references/seo-playbook.md` and `references/algorithm-guide.md` in full before generating any output.
2. **Keyword analysis**: If DataForSEO is available, use live data from the research phase. Otherwise, from the provided topic/keyword, identify the primary keyword, 3-5 secondary keywords, and 2-3 long-tail variations. Consider search intent (informational, navigational, transactional).
3. **Title generation**: Write 3 title variants following the specifications below. Validate each against the rules in the SEO playbook.
4. **Description writing**: Build the full 5000-character description template following the exact structure specified.
5. **Tag generation**: Produce 10-15 tags within the 500-character limit, ranked by priority.
6. **Chapter timestamps**: Write 5 keyword-rich chapter labels.
7. **Hashtag selection**: Choose 3-5 hashtags with rationale.
8. **Schema markup**: Generate the VideoObject JSON-LD snippet.
9. **Self-check**: Verify all outputs against the quality criteria before returning.

## Output Template

```
## Keyword Strategy

- **Primary keyword**: [keyword] — Search intent: [informational/navigational/transactional]
- **Secondary keywords**: [keyword 2], [keyword 3], [keyword 4]
- **Long-tail variations**: [phrase 1], [phrase 2], [phrase 3]

## Title Variants

### Variant A: Search-Optimized
> [Title — 60-100 chars, primary keyword in first 40 chars, front-loaded for search]

- **Character count**: [X]
- **Keyword position**: Chars [X-Y]
- **Target traffic source**: Search
- **Rationale**: [Why this title works for search discovery]

### Variant B: Browse/Curiosity-Driven
> [Title — 60-100 chars, curiosity hook, emotional trigger, keyword present but not leading]

- **Character count**: [X]
- **Keyword position**: Chars [X-Y]
- **Target traffic source**: Browse/Home feed
- **Rationale**: [Why this title drives clicks from impressions]

### Variant C: Hybrid (Search + Browse)
> [Title — 60-100 chars, keyword front-loaded + curiosity element]

- **Character count**: [X]
- **Keyword position**: Chars [X-Y]
- **Target traffic source**: Search + Browse
- **Rationale**: [Why this balances both discovery paths]

**Recommended title**: [A, B, or C] — [one-sentence justification based on channel size and niche]

## Description

```
[First 150 characters: primary keyword + compelling hook — this is the visible preview text]

⏱ Timestamps:
00:00 - [Chapter 1: keyword-rich label]
XX:XX - [Chapter 2: keyword-rich label]
XX:XX - [Chapter 3: keyword-rich label]
XX:XX - [Chapter 4: keyword-rich label]
XX:XX - [Chapter 5: keyword-rich label]

[250-word body: natural keyword integration, context about the video, value proposition. Include secondary keywords organically. Break into 2-3 short paragraphs for readability.]

🔗 Resources & Links:
- [Mentioned resource 1]: [URL placeholder]
- [Mentioned resource 2]: [URL placeholder]

📱 Connect:
- [Social/website link placeholders]

👉 [Call-to-action: subscribe, comment prompt, or related video link]

#[Hashtag1] #[Hashtag2] #[Hashtag3]
```

**Description stats**: [X] characters | Primary keyword appears [X] times | Secondary keywords: [list with counts]

## Tags

| Priority | Tag | Characters | Rationale |
|----------|-----|------------|-----------|
| 1 | [exact primary keyword] | [X] | Primary target term |
| 2 | [secondary keyword] | [X] | [Rationale] |
| 3 | [long-tail variation] | [X] | [Rationale] |
| ... | ... | ... | ... |
| [10-15] | [broad niche tag] | [X] | Category signal |

**Total characters used**: [X] / 500

## Chapter Timestamps

| Timestamp | Label | Target Keyword |
|-----------|-------|----------------|
| 00:00 | [Keyword-rich intro label] | [keyword] |
| XX:XX | [Chapter 2 label] | [keyword] |
| XX:XX | [Chapter 3 label] | [keyword] |
| XX:XX | [Chapter 4 label] | [keyword] |
| XX:XX | [Chapter 5 label] | [keyword] |

## Hashtags

| Hashtag | Type | Rationale |
|---------|------|-----------|
| #[Hashtag1] | Niche-specific | [Why this hashtag] |
| #[Hashtag2] | Topic-specific | [Why this hashtag] |
| #[Hashtag3] | Broad discovery | [Why this hashtag] |
| #[Hashtag4] | (optional) | [Why this hashtag] |
| #[Hashtag5] | (optional) | [Why this hashtag] |

## VideoObject Schema (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "[Recommended title]",
  "description": "[First 150 chars of description]",
  "thumbnailUrl": "[placeholder]",
  "uploadDate": "[YYYY-MM-DD]",
  "duration": "[PT#M#S format]",
  "contentUrl": "[video URL placeholder]",
  "embedUrl": "[embed URL placeholder]",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": 0
  }
}
```
```

## Quality Criteria

- All three titles must be between 60-100 characters with the primary keyword appearing in the first 40 characters
- The description's first 150 characters must contain the primary keyword and a compelling hook (this is the search preview)
- Tags must total 500 characters or fewer; exactly 10-15 tags provided
- Each tag must include a clear rationale — no filler tags
- The 250-word description body must read naturally, not as keyword stuffing
- Chapter labels must each contain a relevant keyword while remaining descriptive
- Hashtags limited to 3-5; more than 5 triggers YouTube's spam filter
- JSON-LD must be valid schema.org VideoObject markup
- All keyword frequency claims must be verifiable by counting occurrences in the output
- Recommendations must align with the SEO playbook and algorithm guide principles

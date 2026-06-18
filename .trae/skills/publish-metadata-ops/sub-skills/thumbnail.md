# Thumbnail Brief + A/B Concepts

This sub-skill produces a detailed thumbnail design brief with three A/B test variants, a title-thumbnail synergy analysis, and niche-specific CTR benchmarks, giving creators or designers a complete specification for high-performing thumbnails without ambiguity.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Video title | Yes | The chosen title (or top candidate) |
| Topic | Yes | Video subject for visual concept ideation |
| Channel niche | Yes | Content category for benchmark context |
| Visual style | No | Existing brand style (colors, face prominence, text style) |
| Channel size | No | Helps set realistic CTR targets (default: small) |
| Competitor thumbnails | No | URLs or descriptions of competitor thumbnails for differentiation |

## Reference Files

- `references/thumbnail-ctr-guide.md`
- `references/seo-playbook.md`

## DataForSEO Research (When Available)

Analyse competitor thumbnails with live YouTube SERP data:

1. **Competitor thumbnail scan**: Run `serp_youtube_organic_live_advanced` with the video's target keyword to retrieve top-ranking videos with their `thumbnail_url` fields. This shows what visual styles currently dominate the SERP for this keyword.
2. **Channel context**: Use `serp_youtube_video_info_live_advanced` on the top 3-5 videos to get channel names and subscriber counts — understand whether top thumbnails come from authority channels or small creators.
3. **Differentiation check**: Compare the primary brief against competitor thumbnail patterns to ensure visual distinctiveness in the search results page.

**Fallback:** If DataForSEO is unavailable, use WebSearch for `[keyword] youtube` and manually review thumbnail patterns.

## Thumbnail Generation (When NanoBanana MCP Available)

When the NanoBanana MCP server is configured, generate actual thumbnail images using the `generate_image` tool:

**Tool:** `generate_image`

**Recommended settings for YouTube thumbnails:**
- `aspect_ratio`: `"16:9"` (YouTube standard)
- `resolution`: `"4k"` (maximum quality for 1280×720 YouTube requirement)
- `model_tier`: `"nb2"` (default — best balance of speed and quality for production assets)
- `output_path`: user's project directory or `~/nanobanana-images/`

**Workflow:**
1. After generating the primary thumbnail brief, convert it into a detailed image generation prompt
2. Generate the primary thumbnail: call `generate_image` with a prompt derived from the brief (focal point, expression, text overlay, colour palette, composition all specified)
3. Generate each A/B variant: call `generate_image` with the variant's modified prompt
4. Present all 4 images (primary + 3 variants) to the user for review
5. If the user requests refinements, use iterative prompting to adjust

**Prompt engineering tips for thumbnails:**
- Specify "YouTube thumbnail style" in the prompt
- Include text rendering instructions: `text "[WORD]" in bold white sans-serif with black stroke`
- Specify face expressions precisely: "genuine shocked expression with wide eyes and open mouth"
- Include background colour: "solid [colour] background" or "blurred [scene] background"
- Add "high contrast, vibrant colours, clean composition" for thumbnail aesthetics
- Mention "legible at small size" to encourage clear focal points

**Fallback:** If NanoBanana MCP is unavailable, deliver the text-based thumbnail brief only.
The brief is detailed enough for any designer to execute.

## Parallel Agents

Not required. This skill runs as a single sequential workflow.

## Execution Steps

1. **Load references**: Read `references/thumbnail-ctr-guide.md` and `references/seo-playbook.md` before generating output.
2. **Analyze the title**: Identify what information the title already communicates. The thumbnail must add NEW information — never duplicate the title.
3. **Determine focal strategy**: Based on niche and topic, decide the primary visual approach (face-driven, object-driven, text-driven, comparison, transformation).
4. **Build the primary brief**: Specify every visual element with enough detail that a designer can execute without questions.
5. **Create 3 A/B variants**: Each must change ONE meaningful variable from the primary concept.
6. **Run synergy check**: Verify title + thumbnail follow the information split rule.
7. **Set benchmarks**: Pull CTR benchmarks from the thumbnail-CTR guide for this niche and channel size.

## Output Template

```
## Title-Thumbnail Analysis

- **Title**: [the video title]
- **Title communicates**: [What information the title already provides]
- **Thumbnail must add**: [The complementary information/emotion the thumbnail needs to convey]
- **Information split**: [Title handles X, thumbnail handles Y — no overlap]

---

## Primary Thumbnail Brief

### Focal Point
- **Primary subject**: [What the eye should hit first — face, object, result, etc.]
- **Position**: [Where in the frame — rule of thirds placement, e.g., "Subject right-third, looking left toward text"]
- **Size**: [How much of the frame the focal point occupies — e.g., "60% of frame"]

### Expression/Emotion (if face-based)
- **Target emotion**: [Specific emotion — not just "surprised" but "genuine disbelief with raised eyebrows and open mouth"]
- **Eye direction**: [Looking at camera, looking at object, looking at text]
- **Avoid**: [What NOT to do — e.g., "No fake surprise, no closed-mouth smiles"]

### Text Overlay
- **Text**: [Maximum 3 words — ideally 1-2]
- **Font style**: [Bold sans-serif, handwritten, etc.]
- **Font size**: [Relative to frame — must be legible at 168x94px mobile size]
- **Position**: [Where the text sits — must not overlap the face/focal point]
- **Color**: [High contrast against background — specify exact pairing]
- **Stroke/shadow**: [Outline specifications for legibility]

### Color Palette
- **Primary color**: [Hex code + name] — [Role: background/dominant]
- **Secondary color**: [Hex code + name] — [Role: accent/text]
- **Contrast color**: [Hex code + name] — [Role: pop element that draws eye]
- **Color psychology**: [Why these colors work for this niche/emotion]

### Composition
- **Layout**: [Rule of thirds grid description]
- **Negative space**: [Where and how much — needed for text and visual breathing room]
- **Depth**: [Foreground/background relationship, blur, etc.]
- **Visual flow**: [How the eye moves through the thumbnail — entry point to exit point]

### Mobile Legibility Check
- **At 168x94px**: [What must still be visible — focal point, text, key element]
- **Remove at small size**: [Elements that become noise on mobile]
- **Text size minimum**: [Must pass the "arm's length phone" test]

### DO NOT Include
- [Specific element to avoid and why]
- [Specific element to avoid and why]
- [Specific element to avoid and why]

---

## A/B Test Variants

### Variant A: [Concept Name]
- **What changes from primary**: [One specific variable — color, text, expression, composition]
- **Why test this**: [Hypothesis for why this might outperform]
- **Target segment**: [Who this variant appeals to more — new viewers, returning, search, browse]
- **Predicted CTR direction**: [Higher/Lower than primary and why]

### Variant B: [Concept Name]
- **What changes from primary**: [One specific variable]
- **Why test this**: [Hypothesis]
- **Target segment**: [Who this appeals to]
- **Predicted CTR direction**: [Higher/Lower and why]

### Variant C: [Concept Name]
- **What changes from primary**: [One specific variable]
- **Why test this**: [Hypothesis]
- **Target segment**: [Who this appeals to]
- **Predicted CTR direction**: [Higher/Lower and why]

### A/B Testing Protocol
- **Minimum test duration**: [Hours/days before statistical significance]
- **Primary metric**: CTR (impressions click-through rate)
- **Secondary metric**: AVD (to ensure clicks aren't misleading)
- **Sample size note**: [Minimum impressions before drawing conclusions]

---

## Title + Thumbnail Synergy Check

| Rule | Status | Detail |
|------|--------|--------|
| Information split (no duplication) | [PASS/FAIL] | [What title says vs what thumbnail shows] |
| Emotional alignment | [PASS/FAIL] | [Title tone matches thumbnail emotion] |
| Curiosity amplification | [PASS/FAIL] | [Together they create more curiosity than either alone] |
| Text overlap check | [PASS/FAIL] | [Thumbnail text does not repeat title words] |
| Mobile readability | [PASS/FAIL] | [Both title and thumbnail work at mobile size] |

**Synergy verdict**: [Strong/Moderate/Weak] — [one-sentence assessment]

[If FAIL on any rule: specific fix recommendation]

---

## Benchmark Context

| Metric | This Niche Benchmark | Target for This Video | Source |
|--------|---------------------|----------------------|--------|
| Average CTR | [X%] | [Y%] | thumbnail-ctr-guide.md |
| Top 10% CTR | [X%] | — | thumbnail-ctr-guide.md |
| CTR by channel size ([tier]) | [X%] | [Y%] | thumbnail-ctr-guide.md |

**What the thumbnail must achieve**: [Specific CTR target with context — e.g., "Minimum 5.5% CTR to outperform niche average; 8%+ to reach top quartile for this channel size"]
```

## Quality Criteria

- Text overlay must be 3 words maximum — reject any brief with more
- Color palette must include exact hex codes, not just color names
- The primary brief must be specific enough for a designer to execute without follow-up questions
- Each A/B variant must change exactly ONE variable from the primary concept — not multiple changes
- The synergy check must evaluate all 5 rules and flag any failures with fixes
- Mobile legibility must be explicitly addressed (168x94px test)
- The "DO NOT Include" section must contain at least 3 specific items
- CTR benchmarks must reference the thumbnail-ctr-guide.md with niche-specific numbers
- No thumbnail brief may suggest duplicating information already in the title
- All composition directions must use spatial language a designer can act on (not "make it look good" but "subject occupies right third, 3px white stroke on text")

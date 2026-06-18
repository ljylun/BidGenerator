# Shorts Sub-Skill

This sub-skill generates a complete YouTube Shorts production package — from concept through script to SEO metadata — optimised for the Shorts algorithm's unique signals (Viewed vs Swiped Away, loop rate, replay rate). It handles both standalone Shorts concepts and repurposing clips from existing long-form content, tailoring output to the creator's goal: channel growth, Shorts monetisation, or funneling viewers to long-form videos.

## Inputs Required

- **Channel niche** (string): the creator's content category
- **Content idea OR existing long-form video** (string): either a new concept, or a video URL/description to repurpose
- **Shorts goal** (one of): `growth` | `monetisation` | `long-form funnel`
- **Target audience** (optional): demographic or viewer persona

## Reference Files to Load

- `references/shorts-playbook.md`
- `references/algorithm-guide.md`
- `references/monetization-guide.md`

## Parallel Agents

Not required. Execute sequentially.

## Step-by-Step Execution

1. Load all three reference files and internalise Shorts algorithm signals, format constraints, and monetisation rules.
2. Determine format: if the user provided an existing long-form video, identify the best repurpose-worthy moments (highest density of value or emotion in under 60 seconds). If a standalone idea, proceed to concept design.
3. Design the hook (first 1-3 seconds). This is the single highest-impact element. The hook must create an open loop, pattern interrupt, or immediate curiosity gap. Refer to the shorts playbook for proven hook formulas.
4. Write the full script/outline with visual change markers every 3 seconds minimum. Structure: Hook (1-3s) then Value bomb (remaining time) then Loop setup (final 1-2s that mirrors or callbacks to the opening frame for seamless replay).
5. Select optimal length. Use the 13-second or 60-second sweet spots from the playbook. Choose 13s for punchy hooks/reveals and 60s for tutorials or storytelling. Avoid 30-45s dead zone unless content demands it.
6. Write SEO metadata: title (4-6 words, 20-40 characters, front-load keyword), description (first 125 characters carry all weight), and 3-5 hashtags.
7. Predict performance using the Viewed vs Swiped Away framework. Flag any Short predicted below 60% viewed rate and suggest fixes.
8. Calculate monetisation context: Shorts ad revenue share RPM for the niche, and flag music licensing impact (using 1 track = 50% revenue share rule).
9. If the goal is `long-form funnel`, design a bridge element: verbal CTA, pinned comment, or visual teaser that drives viewers to a specific long-form video.

## Output Template

```markdown
## YouTube Short: [Working Title]

### Concept Brief
- **Format**: [Standalone / Repurposed from: "Video Title"]
- **Length**: [Xs] — Rationale: [why this length]
- **Goal**: [Growth / Monetisation / Long-Form Funnel]
- **Hook Strategy**: [1-sentence description of the hook approach]

### Script / Outline

| Timestamp | Visual | Audio / Script | Notes |
|-----------|--------|----------------|-------|
| 0:00-0:01 | [HOOK visual — pattern interrupt] | "[Hook line]" | First frame must stop scroll |
| 0:01-0:03 | [Visual change] | "[Setup]" | Open loop established |
| 0:03-0:06 | [Visual change] | "[Value point 1]" | |
| ... | ... | ... | Visual change min every 3s |
| 0:XX-0:XX | [LOOP SETUP — mirrors opening] | "[Callback/loop line]" | Seamless replay trigger |

**Total visual changes**: [N] (minimum 1 per 3 seconds)

### SEO Metadata
- **Title**: [4-6 words, 20-40 chars, keyword front-loaded]
- **Description** (first 125 chars matter):
  > [Description text]
- **Hashtags**: #tag1 #tag2 #tag3 [#tag4] [#tag5]

### Performance Prediction
- **Predicted Viewed vs Swiped Away**: [X%] viewed
- **Status**: [PASS: above 60% / WARNING: below 60% — fix recommended]
- **Risk factors**: [list any weaknesses]
- **Suggested fixes** (if below 60%): [specific changes]

### Monetisation Context
- **Niche Shorts RPM**: $[X.XX] estimated
- **Music licensing**: [No music / Original sound / Licensed track — 50% revenue share applies]
- **Estimated revenue per 1M views**: $[X]

### Long-Form Funnel Bridge
> *(included only when goal = long-form funnel)*
- **Target long-form video**: "[Title]"
- **Bridge method**: [Verbal CTA / Pinned comment / Visual teaser / Cliffhanger]
- **CTA script**: "[Exact words to say/show]"
- **Pinned comment text**: "[Comment text with link context]"
```

## Quality Criteria

- Hook must be completable in 1-3 seconds and create genuine curiosity or pattern interrupt
- Visual change markers appear at minimum every 3 seconds throughout the script
- Loop setup in final 1-2 seconds must logically connect back to the opening
- Title is 4-6 words, 20-40 characters, with primary keyword in first position
- Description front-loads critical information in first 125 characters
- Performance prediction is justified with specific reasoning, not arbitrary
- Monetisation RPM estimate is realistic for the stated niche (cross-reference monetization guide)
- If music is suggested, the 50% revenue share warning is always included
- Long-form funnel bridge is only included when goal is `long-form funnel`
- Total output is actionable: a creator could produce the Short using only this document

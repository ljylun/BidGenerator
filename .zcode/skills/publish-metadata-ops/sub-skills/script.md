# Retention-Engineered Script

This sub-skill generates a full video script engineered for maximum audience retention, using proven structural patterns — hook-promise-stakes openings, pattern interrupts, forward hooks, and strategic CTAs — all calibrated to the target video length and audience type.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Topic | Yes | Video subject matter |
| Target length | Yes | Desired video duration in minutes |
| Channel type | Yes | Educational, entertainment, vlog, review, tutorial, commentary, etc. |
| Audience persona | Yes | Who is watching (age range, knowledge level, why they clicked) |
| Key points | Yes | Core information/arguments to cover (bullet list) |
| Tone | No | Casual, professional, energetic, conversational (default: conversational) |
| CTA goal | No | Subscribe, product, community, or custom (default: subscribe) |

## Reference Files

- `references/retention-scripting-guide.md`
- `references/algorithm-guide.md`

## Parallel Agents

Not required. This skill runs as a single sequential workflow.

## Execution Steps

1. **Load references**: Read `references/retention-scripting-guide.md` and `references/algorithm-guide.md` fully before writing.
2. **Calculate structure**: Based on target length, compute section durations. Hook: 0:00-0:30. Intro: 0:30-2:00. Mid-CTA: ~25% mark. Retention re-hook: ~60% mark. Outro: final 60 seconds. Remaining time divided among content blocks.
3. **Map key points to chapters**: Assign the provided key points to content blocks. Order them by engagement potential — strongest points early and late, weaker points in the middle (surrounded by pattern interrupts).
4. **Write the hook block**: Produce the 3-part hook (Grab, Promise, Stakes) targeting >70% retention at the 30-second mark.
5. **Write the intro**: Bridge from hook to content. Establish context, stakes, and viewer outcome.
6. **Write content blocks**: Each block opens with a pattern interrupt, delivers value, ends with a micro-summary and forward hook to the next section.
7. **Insert pattern interrupts**: Place one every 60-90 seconds. Mark each with its type tag.
8. **Place CTAs**: Soft mid-CTA at ~25%, hard CTA in outro.
9. **Write outro**: Hard CTA, end screen cue, next video tease.
10. **Annotate retention risks**: Scan the full script for drop-off danger zones. Mark each with a warning symbol and mitigation note.
11. **Add pacing notes**: Insert editor directions throughout.

## Output Template

```
## Script Metadata

- **Topic**: [topic]
- **Target length**: [X] minutes ([Y] words at ~150 words/minute)
- **Channel type**: [type]
- **Audience**: [persona summary]
- **Estimated word count**: [total words]

---

## HOOK (0:00 — 0:30) | Target: >70% retention at 0:30

### Grab (0:00 — 0:05)
[Opening line — the single most important sentence in the video]

[PACING: Deliver fast. No intro graphics. Start mid-thought or mid-action.]

### Promise (0:05 — 0:15)
[What the viewer will get from watching. Specific, tangible outcome.]

### Stakes (0:15 — 0:30)
[Why it matters. What they lose by clicking away. Emotional or practical consequence.]

⚠️ RETENTION RISK: [If applicable — e.g., "Generic promise language. Make the outcome hyper-specific."]

---

## INTRO (0:30 — 2:00) | Context + Credibility

[CAMERA CHANGE]

[Context paragraph: Why this topic, why now, why from this creator.]

[Viewer outcome restatement: "By the end of this video, you'll..."]

[PACING: Moderate. Establish trust but don't linger. Viewers who survived the hook want content.]

---

## CONTENT BLOCK 1: [Chapter Title] (2:00 — X:XX)

[GRAPHIC: Chapter title card]
[Pattern interrupt: opening line that resets attention]
[Core content — spoken-word style: short sentences, direct address ("you"), rhetorical questions.]
[B-ROLL CUE: Describe what should appear on screen]
[Micro-summary: One sentence recap] → [Forward hook: "But that's only half the picture..."]
⚠️ RETENTION RISK: [If applicable — e.g., "Dense info block. Break with visual at 4:30."]

---

## CONTENT BLOCK 2: [Chapter Title] (X:XX — X:XX)

[SOUND EFFECT: Transition sting]
[Pattern interrupt] → [Content delivery] → [UNEXPECTED STAT]
[Micro-summary] → [Forward hook]

---

## MID-CTA (~25% mark, approximately X:XX)

[CAMERA CHANGE] [Soft CTA — conversational, tied to content just delivered. 10-15 seconds max.]
> "If you're finding this useful, hit subscribe — I break down [niche topic] like this every [cadence]."

---

## CONTENT BLOCKS 3+: [Chapter Titles] (X:XX — X:XX)

[Continue pattern: interrupt → content → B-ROLL → micro-summary → forward hook]

## RETENTION RE-HOOK (~60% mark, approximately X:XX)

[CAMERA CHANGE] [Why the remaining content is the most valuable part.]
⚠️ RETENTION RISK: [60% mark is a common drop-off cliff. This re-hook must feel like a second hook.]

---

## OUTRO (final 60 seconds, X:XX — end)

### Hard CTA (15 seconds)
[Direct call-to-action tied to the video's value delivery.]

> "[Specific CTA: subscribe, comment a specific thing, check link in description]"

### End Screen Cue (15 seconds)
[GRAPHIC: End screen overlay]

> "If you liked this, you'll want to watch [related video topic] — I'll put it right here."

[Point to end screen card position]

### Next Video Tease (15 seconds)
[Brief, compelling preview of the suggested next video. Create a mini curiosity gap.]

[PACING: Keep energy up through the final second. No "thanks for watching" wind-down.]

---

## Pattern Interrupt Log

| Timestamp | Type | Description |
|-----------|------|-------------|
| X:XX | [CAMERA CHANGE] | [Brief note] |
| X:XX | [B-ROLL CUE] | [Brief note] |
| X:XX | [GRAPHIC] | [Brief note] |
| X:XX | [SOUND EFFECT] | [Brief note] |
| X:XX | [UNEXPECTED STAT] | [Brief note] |

**Total pattern interrupts**: [X] | **Average interval**: [X] seconds

## Retention Risk Map

| Timestamp | Risk Level | Issue | Mitigation |
|-----------|------------|-------|------------|
| X:XX | ⚠️ High | [Description] | [Solution] |
| X:XX | ⚠️ Medium | [Description] | [Solution] |

## Editor Notes

- [Pacing guidance for specific sections]
- [Music/sound design suggestions]
- [Cut rhythm recommendations]
- [Thumbnail moment candidates with timestamps]
```

## Quality Criteria

- Word count must match target length at ~150 words per minute (within 10% tolerance)
- The hook must contain all three elements: Grab (0-5s), Promise (5-15s), Stakes (15-30s)
- Pattern interrupts must appear every 60-90 seconds — verify by checking the interrupt log timestamps
- Every content block must end with both a micro-summary AND a forward hook
- Mid-CTA must appear at approximately the 25% mark, not earlier
- Retention re-hook must appear at approximately the 60% mark
- All production cue tags must use the exact bracket format: [CAMERA CHANGE], [B-ROLL CUE], [GRAPHIC], [SOUND EFFECT], [UNEXPECTED STAT]
- At least 3 retention risk points must be identified and marked with mitigations
- The script must read as natural spoken language, not written prose — short sentences, contractions, direct address
- The outro must never contain filler phrases like "thanks for watching" or "don't forget to" — maintain energy to the final second

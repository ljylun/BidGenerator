# First-30-Second Hook Writer

This sub-skill generates five distinct hook variants for a video's opening 30 seconds, each using a different psychological mechanism, rated for drop-off risk and optimized traffic source, giving creators a tested menu of openings to choose from based on their channel size and content type.

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Topic | Yes | Video subject matter |
| Channel niche | Yes | Content category (tech, fitness, finance, etc.) |
| Hook style preference | No | If creator wants to bias toward a specific style |
| Channel size | No | Helps calibrate the decision guide (default: small) |
| Video format | No | Long-form, Short, tutorial, commentary, etc. (default: long-form) |

## Reference Files

- `references/retention-scripting-guide.md`

## Parallel Agents

Not required. This skill runs as a single sequential workflow.

## Execution Steps

1. **Load reference**: Read `references/retention-scripting-guide.md` fully before generating hooks.
2. **Analyze the topic**: Identify the core tension, surprising angle, common misconception, emotional stakes, and audience pain point related to the topic.
3. **Generate 5 hook variants**: Write each variant following the exact structure below. Each hook must be a complete 30-second script (approximately 75 words at spoken pace).
4. **Rate each hook**: Assign drop-off risk, optimal traffic source, and identify the psychological mechanism.
5. **Build the decision guide**: Based on reference file principles, map hook types to channel sizes and content types.
6. **Apply preference weighting**: If a hook style preference was provided, note which variant aligns and explain tradeoffs of the preferred vs recommended style.

## Output Template

```
## Topic Analysis

- **Core tension**: [The fundamental conflict or question in this topic]
- **Surprising angle**: [What most people get wrong or don't expect]
- **Audience pain point**: [The problem viewers are trying to solve]
- **Emotional stakes**: [What viewers stand to gain or lose]

---

## Hook Variant 1: Shock/Contradiction

**Mechanism**: Cognitive dissonance — presents a counterintuitive statement that conflicts with the viewer's existing belief, creating an information gap they must resolve.

> [Full 30-second spoken script, approximately 75 words]
>
> [Line 1: The counterintuitive claim — delivered with confidence, no hedging]
> [Line 2-3: Brief evidence or framing that makes the claim credible]
> [Line 4-5: Pivot to promise — "and in this video, I'll show you exactly why..."]

- **Word count**: [X] words (~30 seconds)
- **Drop-off risk**: [Low/Medium/High] — [one-sentence explanation]
- **Optimized for**: [Browse/Search/Suggested] — [why this traffic source]
- **Best when**: [Scenario where this hook type excels]
- **Avoid when**: [Scenario where this hook type backfires]

---

## Hook Variant 2: Problem-Agitation

**Mechanism**: Pain amplification — names a problem the viewer already recognizes, then intensifies the emotional weight before offering the video as relief.

> [Full 30-second spoken script, approximately 75 words]
>
> [Line 1: Name the pain directly — "You've tried X and it didn't work"]
> [Line 2-3: Twist the knife — show the consequences of the unsolved problem]
> [Line 4-5: Relief signal — "Here's what actually works..."]

- **Word count**: [X] words (~30 seconds)
- **Drop-off risk**: [Low/Medium/High] — [one-sentence explanation]
- **Optimized for**: [Browse/Search/Suggested] — [why this traffic source]
- **Best when**: [Scenario]
- **Avoid when**: [Scenario]

---

## Hook Variant 3: Story-Open

**Mechanism**: Narrative transportation — drops the viewer into the middle of an action or scene, activating the brain's story-processing mode which naturally resists disengagement.

> [Full 30-second spoken script, approximately 75 words]
>
> [Line 1: Mid-action scene — start in medias res, no setup]
> [Line 2-3: Sensory details or stakes that make the scene vivid]
> [Line 4-5: Bridge to topic — connect the story to the video's core content]

- **Word count**: [X] words (~30 seconds)
- **Drop-off risk**: [Low/Medium/High] — [one-sentence explanation]
- **Optimized for**: [Browse/Search/Suggested] — [why this traffic source]
- **Best when**: [Scenario]
- **Avoid when**: [Scenario]

---

## Hook Variant 4: Curiosity-Gap

**Mechanism**: Information gap theory — reveals enough to make the viewer aware of what they don't know, creating psychological tension that can only be resolved by watching.

> [Full 30-second spoken script, approximately 75 words]
>
> [Line 1: Tease the answer without giving it — "There's one thing that..."]
> [Line 2-3: Build the gap — add specificity that makes the unknown feel important]
> [Line 4-5: Promise the payoff — signal exactly when the answer comes]

- **Word count**: [X] words (~30 seconds)
- **Drop-off risk**: [Low/Medium/High] — [one-sentence explanation]
- **Optimized for**: [Browse/Search/Suggested] — [why this traffic source]
- **Best when**: [Scenario]
- **Avoid when**: [Scenario]

---

## Hook Variant 5: Social Proof

**Mechanism**: Authority bias + stakes — leads with credibility (results, credentials, or third-party validation) to earn trust instantly, then pivots to what's at stake.

> [Full 30-second spoken script, approximately 75 words]
>
> [Line 1: Credibility statement — specific result, number, or proof point]
> [Line 2-3: Stakes — what this means for the viewer]
> [Line 4-5: Promise — "I'm going to break down exactly how..."]

- **Word count**: [X] words (~30 seconds)
- **Drop-off risk**: [Low/Medium/High] — [one-sentence explanation]
- **Optimized for**: [Browse/Search/Suggested] — [why this traffic source]
- **Best when**: [Scenario]
- **Avoid when**: [Scenario]

---

## Decision Guide

### By Channel Size

| Channel Size | Recommended Hook | Reasoning |
|-------------|-----------------|-----------|
| Nano (<1K) | [Type] | [Why — e.g., "No established authority, so social proof is weak"] |
| Micro (1K-10K) | [Type] | [Why] |
| Small (10K-100K) | [Type] | [Why] |
| Mid (100K-500K) | [Type] | [Why] |
| Large (500K+) | [Type] | [Why] |

### By Content Type

| Content Type | Primary Hook | Secondary Hook | Avoid |
|-------------|-------------|----------------|-------|
| Tutorial/How-to | [Type] | [Type] | [Type + why] |
| Commentary/Opinion | [Type] | [Type] | [Type + why] |
| Review | [Type] | [Type] | [Type + why] |
| Entertainment | [Type] | [Type] | [Type + why] |
| Educational | [Type] | [Type] | [Type + why] |
| Vlog | [Type] | [Type] | [Type + why] |

### By Traffic Source Goal

| Traffic Source | Best Hook Types | Why |
|---------------|----------------|-----|
| Search | [Types] | [Explanation] |
| Browse/Home | [Types] | [Explanation] |
| Suggested | [Types] | [Explanation] |

## Recommendation

**For this video**: [Recommended variant number and name] — [2-sentence justification based on topic, niche, and channel context]

**Runner-up**: [Second choice] — [When to use this instead]
```

## Quality Criteria

- Each hook must be a complete, speakable 30-second script — approximately 75 words (65-85 acceptable range)
- All five hook types must be represented: Shock/Contradiction, Problem-Agitation, Story-Open, Curiosity-Gap, Social Proof
- Each hook must name its specific psychological mechanism with a one-sentence explanation of how it works
- Drop-off risk ratings must be justified, not arbitrary
- Traffic source recommendations must align with the retention scripting guide's principles
- The decision guide must cover all channel sizes AND all listed content types
- No two hooks may use the same opening structure or first sentence pattern
- Hooks must be written in natural spoken language — no written-prose phrasing
- The curiosity-gap hook must NOT give away the answer within the 30 seconds
- The story-open hook must start in medias res — no "Let me tell you about a time when..."

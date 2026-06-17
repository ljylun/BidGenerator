# Monetize Sub-Skill

This sub-skill produces a comprehensive monetisation strategy by auditing all seven YouTube revenue streams against the creator's current channel size, niche, and audience — then building a 90-day activation roadmap with specific revenue targets. It bridges YouTube-native monetisation (AdSense, memberships, Super Chat) with external revenue (brand deals, digital products, funnels) to maximise total creator income.

## Inputs Required

- **Channel size** (number): current subscriber count
- **Niche** (string): content category
- **Current revenue streams** (list): which monetisation methods are currently active
- **Monthly views** (number): approximate total monthly views across all content
- **Audience demographics** (optional): age range, geography, gender split, interests
- **Existing products or services** (optional): anything the creator already sells

## Reference Files to Load

- `references/monetization-guide.md`
- `references/analytics-guide.md`

## Parallel Agents

Not required. Execute sequentially.

## Step-by-Step Execution

1. Load both reference files. Internalise YPP tier thresholds, RPM benchmarks by niche, revenue stream requirements, and brand deal rate calculations.
2. Determine the creator's current YPP tier: none (below thresholds), expanded (500 subs + 3K watch hours or 3M Shorts views), or full (1K subs + 4K watch hours or 10M Shorts views). List which features are unlocked at their tier.
3. Estimate current monthly ad revenue using the formula: monthly views multiplied by niche-specific RPM divided by 1000. Use the RPM benchmarks from the monetization guide for the stated niche.
4. Perform a revenue gap analysis across all 7 streams: AdSense display ads, Shorts ad revenue share, Channel Memberships, Super Chat and Super Thanks, YouTube Shopping affiliate, Brand Deals, and External Funnels (courses, communities, digital products, consulting). For each stream, assess: current status (active/available/locked), revenue potential at the creator's current scale, and the gap between current and potential.
5. Build a priority activation roadmap. Rank streams by: revenue potential at current scale, effort to activate, time to first dollar. Small channels should prioritise brand deals and external funnels over ad revenue. Large channels should optimise ad revenue while layering memberships and shopping.
6. Calculate a brand deal rate card. Use CPM-equivalent pricing (cost per 1000 views on a sponsored video). Establish a negotiation floor (minimum acceptable rate) and ceiling (aspirational rate for high-demand niches). Include the FTC disclosure checklist.
7. Design an external funnel architecture. Recommend the best product type for the niche (course, community, digital download, or consulting). Map the funnel: YouTube video to landing page to email capture to offer. Estimate conversion rates at each stage using industry benchmarks.
8. Build the 90-day revenue action plan with specific milestones and revenue targets for Month 1, Month 2, and Month 3.

## Output Template

```markdown
## Monetisation Strategy: [Niche] Channel

**Channel size**: [N] subscribers
**Monthly views**: [N]
**Current streams**: [List of active revenue sources]

---

### 1. Current State

| Metric | Value |
|--------|-------|
| YPP Tier | [None / Expanded / Full] |
| Active streams | [List] |
| Available (not activated) | [List] |
| Locked (requirements not met) | [List + what is needed] |
| Estimated monthly ad revenue | $[N] ([N] views x $[RPM] RPM) |

---

### 2. Revenue Gap Analysis

| Stream | Status | Current $/mo | Potential $/mo | Gap | Priority |
|--------|--------|-------------|----------------|-----|----------|
| AdSense (long-form) | [Active/Available/Locked] | $[N] | $[N] | $[N] | [High/Med/Low] |
| Shorts ad share | ... | ... | ... | ... | ... |
| Memberships | ... | ... | ... | ... | ... |
| Super Chat / Thanks | ... | ... | ... | ... | ... |
| Shopping affiliate | ... | ... | ... | ... | ... |
| Brand deals | ... | ... | ... | ... | ... |
| External funnels | ... | ... | ... | ... | ... |
| **Total** | | **$[N]** | **$[N]** | **$[N]** | |

---

### 3. Priority Activation Roadmap

**Activate first** (highest ROI at current scale):
1. **[Stream]** — [Why now, what to do, expected revenue timeline]

**Activate second**:
2. **[Stream]** — [Why, what, when]

**Activate third**:
3. **[Stream]** — [Why, what, when]

**Hold for later** (requires more scale):
- [Stream] — unlock at [N] subscribers / [N] monthly views

---

### 4. Brand Deal Rate Card

| Metric | Value |
|--------|-------|
| Average views per video | [N] |
| CPM rate (niche benchmark) | $[N] |
| **Negotiation floor** | $[N] per integration |
| **Target rate** | $[N] per integration |
| **Ceiling** (premium placement) | $[N] per integration |

**Rate justification**: [Why this rate is appropriate for the channel's niche, engagement, and audience]

**FTC Disclosure Checklist**:
- [ ] "Paid promotion" toggle enabled in YouTube Studio
- [ ] Verbal disclosure within first 30 seconds of video
- [ ] "#ad" or "Sponsored by [Brand]" in title or first line of description
- [ ] Disclosure visible before "Show More" fold
- [ ] Separate disclosure for each sponsored element (if multiple brands)

---

### 5. External Funnel Design

**Recommended product**: [Course / Community / Digital download / Consulting]
**Why this product**: [Fit with niche and audience needs]

**Funnel architecture**:
```
YouTube Video (awareness)
  -> Link in description / pinned comment
    -> Landing Page (interest)
      -> Email Capture (lead)
        -> Email Sequence (nurture, 3-5 emails)
          -> Offer Page (conversion)
```

**Estimated conversion rates**:
| Stage | Rate | Monthly volume |
|-------|------|----------------|
| Video viewers to landing page | [1-3%] | [N] |
| Landing page to email | [20-40%] | [N] |
| Email to purchase | [2-5%] | [N] |
| **Estimated monthly product revenue** | | **$[N]** |

**Price point recommendation**: $[N] — [Rationale]

---

### 6. 90-Day Revenue Action Plan

**Month 1: Foundation**
- [ ] [Action item 1] — target: $[N]
- [ ] [Action item 2]
- [ ] [Action item 3]
- **Month 1 revenue target**: $[N]

**Month 2: Activation**
- [ ] [Action item 1] — target: $[N]
- [ ] [Action item 2]
- [ ] [Action item 3]
- **Month 2 revenue target**: $[N]

**Month 3: Optimisation**
- [ ] [Action item 1] — target: $[N]
- [ ] [Action item 2]
- [ ] [Action item 3]
- **Month 3 revenue target**: $[N]

**Total 90-day revenue target**: $[N] (up from $[current] — [X%] increase)
```

## Quality Criteria

- YPP tier classification is accurate based on the stated subscriber count and watch hours
- RPM estimates use realistic niche-specific benchmarks, not inflated averages
- All 7 revenue streams are analysed, even those that are locked (with unlock requirements stated)
- Revenue potential estimates are conservative and based on channel's actual scale
- Brand deal rates use CPM-equivalent calculation, not arbitrary numbers
- FTC disclosure checklist is complete and current
- External funnel conversion rates use industry benchmarks, not optimistic projections
- 90-day plan has specific, measurable targets — not vague goals
- Priority order accounts for channel size: small channels prioritise brand deals and products over ad revenue
- Revenue gap table clearly shows the difference between current and potential income

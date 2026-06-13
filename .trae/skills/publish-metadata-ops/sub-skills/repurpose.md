# Repurpose Sub-Skill

This sub-skill transforms a single YouTube video into a complete cross-platform content distribution package. It extracts the highest-value moments for Shorts, restructures the core message for blog posts, social media, email, podcast, and community posts — each adapted to the native format and audience expectations of the target platform rather than simply copy-pasting the transcript.

## Inputs Required

- **Video title** (string): the published or working title
- **Video description or full script** (string): either the YouTube description, bullet-point summary, or complete transcript/script
- **Target platforms** (list): which platforms to generate content for (defaults to all)
- **Available resources** (optional): what the creator has access to (e.g., video editor, blog, email list, podcast feed)
- **Video duration** (optional): total length for timestamp calculations
- **Video chapters/timestamps** (optional): existing chapter markers

## Reference Files to Load

- `references/repurposing-guide.md`
- `references/shorts-playbook.md`

## Parallel Agents

Not required. Execute sequentially.

## Step-by-Step Execution

1. Load both reference files. Internalise platform-specific formatting rules, Shorts extraction criteria, and the repurposing best practices.
2. Analyse the video content to identify the core message, key insights, quotable moments, emotional peaks, and standalone segments that work without full context.
3. Extract 3-5 Shorts candidates. For each, identify the timestamp range, rate the hook quality (does the first 1-3 seconds work standalone?), write a Shorts-native title, and rewrite the hook for vertical scroll-stop format. Determine posting order based on hook strength and topic independence.
4. Generate a blog post outline. Map video chapters or major sections to H2/H3 headings. Design an SEO-optimised structure with a target keyword. Plan YouTube embed placement with timestamp parameters for Google Key Moments markup.
5. Write a LinkedIn post. Extract the professional or industry angle. Write a 150-word hook paragraph plus 3 key takeaways. Match LinkedIn's native tone (insight-driven, no clickbait).
6. Write an X/Twitter thread. Create a hook tweet that stands alone, 4-6 insight tweets that each deliver independent value, and a CTA tweet linking back to the video. Each tweet must be under 280 characters.
7. Write an email newsletter block. Generate 2 subject line A/B variants, preview text (40-90 characters), a 200-word distillation of the video's core value, and a link CTA.
8. Create a podcast episode outline. Restructure the video content for audio-only consumption: remove visual-dependent segments, add verbal context where the video relied on screen content, and suggest a discussion or interview framing.
9. Write a YouTube Community post. Describe an image concept (poll, behind-the-scenes, or key frame), write caption text, and include a CTA driving views to the video. This should publish same-day as the video for maximum algorithm signal.

## Output Template

```markdown
## Repurposing Package: "[Video Title]"

---

### 1. Shorts Extraction (3-5 clips)

| # | Timestamp | Hook Quality | Post Order | Title |
|---|-----------|-------------|------------|-------|
| 1 | [MM:SS-MM:SS] | [Strong/Medium/Weak] | [1st/2nd/etc.] | [Shorts title, 20-40 chars] |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |

**Clip 1 — "[Title]"**
- **Hook rewrite** (first 1-3s): "[Scroll-stopping opening line]"
- **Why this clip**: [What makes it standalone-worthy]
- **Loop setup**: [How final 1-2s connects back to opening]

*(Repeat for each clip)*

**Posting schedule**: Post Clip [N] first (strongest hook), space remaining clips 2-3 days apart.

---

### 2. Blog Post

**Target keyword**: [Primary SEO keyword]
**Estimated word count**: [N words]

#### Outline:
1. **[H2: Introduction]** — [2-sentence summary, embed video here]
2. **[H2: Section from chapter]** — [Key points, embed at ?t=XXs]
3. **[H2: Section]** — [Key points]
4. ...
5. **[H2: Conclusion / CTA]** — [Summary + link to related content]

**Embed strategy**: Place YouTube embeds with `?t=` timestamps at each major section. Use structured data for Google Key Moments.
**Internal links**: [Suggest 2-3 related posts to link to/from]

---

### 3. LinkedIn Post

> [150-word hook paragraph — professional angle, insight-driven]
>
> 3 Key Takeaways:
> 1. [Takeaway with professional context]
> 2. [Takeaway]
> 3. [Takeaway]
>
> [CTA: link to video or ask engagement question]

**Best posting time**: [Weekday, time range for LinkedIn engagement]

---

### 4. X/Twitter Thread

**Tweet 1 (Hook)**:
> [Hook tweet — standalone insight, under 280 chars]

**Tweet 2-N (Insights)**:
> [Insight tweet — independent value, under 280 chars]

*(4-6 insight tweets)*

**Final Tweet (CTA)**:
> [CTA tweet with video link, under 280 chars]

**Thread length**: [N] tweets
**Best posting time**: [Day/time recommendation]

---

### 5. Email Newsletter

**Subject Line A**: [Variant A — curiosity-driven]
**Subject Line B**: [Variant B — benefit-driven]
**Preview text**: [40-90 characters]

> [200-word distillation of video value]
>
> [CTA button text]: Watch the full breakdown -> [video link]

---

### 6. Podcast Episode Outline

**Episode title**: [Audio-optimised title]
**Estimated duration**: [N minutes]

1. **Intro** ([M:SS]): [Context setting — what listeners will learn]
2. **Segment 1** ([M:SS]): [Topic — add verbal context for visual-dependent parts]
3. **Segment 2** ([M:SS]): [Topic]
4. ...
5. **Outro** ([M:SS]): [Key takeaway + CTA to YouTube video for visual content]

**Adaptation notes**: [What was changed from video format and why]

---

### 7. Community Post (Same-Day Publish)

**Image concept**: [Description — poll option / key frame / behind-the-scenes]
**Caption**:
> [Caption text — 2-3 sentences max]
> [CTA driving to video]

**Post type**: [Image / Poll / Text]
**Timing**: Publish within 1 hour of video going live.
```

## Quality Criteria

- Each platform's content is natively formatted, not a copy-paste of the transcript
- Shorts clips have genuine standalone value — they make sense without watching the full video
- Shorts hooks are rewritten for vertical scroll-stop, not just lifted from the video
- Blog post includes specific embed timestamps and targets a real SEO keyword
- LinkedIn tone is professional and insight-driven, never clickbaity
- Every tweet in the thread is under 280 characters and delivers independent value
- Email newsletter is a distillation (200 words), not a summary of the entire video
- Podcast outline explicitly addresses visual-dependent segments with verbal alternatives
- Community post is designed for same-day publishing to boost algorithm signals
- All CTAs link back to the original video with appropriate context per platform

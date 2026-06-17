# YouTube Content Repurposing & Strategy Guide

## Table of Contents

1. [Hub/Hero/Help Model](#hubherohelp-model)
2. [Evergreen vs Trending Mix](#evergreen-vs-trending-mix)
3. [Playlist Strategy](#playlist-strategy)
4. [Series Strategy](#series-strategy)
5. [Channel Positioning & Niche](#channel-positioning--niche)
6. [Repurposing Workflows](#repurposing-workflows)
7. [Competitor Keyword Gap Analysis](#competitor-keyword-gap-analysis)
8. [Integration Architecture](#integration-architecture)
9. [Key Constraints & Gotchas](#key-constraints--gotchas)

---

## Hub/Hero/Help Model

`[2025]` Updated content pillar framework:

| Pillar | Frequency | Purpose | Examples |
|--------|-----------|---------|----------|
| **Hero** | 1-2x/year | Mass awareness, tentpole | Collabs, launches, events |
| **Hub** | Regular/episodic | Consistent audience building | Series, podcasts, weekly shows, behind-scenes |
| **Help/Hygiene** | Always-on | SEO capture, search traffic | Tutorials, how-tos, FAQs |

- Recommended mix: primarily **Hub + Help**, reserve Hero for **2-3 major moments/year**
- `[2025]` Edelman: **59% of consumers** want brands to teach them

## Evergreen vs Trending Mix

| Content Type | Target Share | Key Characteristics |
|-------------|-------------|---------------------|
| Evergreen | **70-80%** | Stays Google top 10 for **2+ years** |
| Trending | **20-30%** | Spikes views, decays fast |

- Updating evergreen content = **106%+ traffic increase**
- Educational how-tos = **42.1% retention** (highest of any format)
- Shorts freshness: older Shorts drop after **~30 days**
- Long-form evergreen is **unaffected** by freshness decay

## Playlist Strategy

| Metric | Impact |
|--------|--------|
| Watch time increase | **40%** vs unoptimized channels |
| Channel growth | **20-30%** from playlist SEO |
| Ideal playlist size | **5-10 videos** |

- Playlists rank independently in **YouTube and Google Search**
- Use **Series Playlists** feature (enforces watch order)
- Start each playlist with the **highest-performing video**
- Case study: reorganizing from "All My Content" to themed playlists = views per start from **1.2 to 3.8** within a month

## Series Strategy

- Optimal cycle: **5-7 video** series
- `[2025]` Connected content chains valued by 2025 algorithms
- Elements: consistent branding, numbering, cliffhangers, series playlists

## Channel Positioning & Niche

- **Niche-first, expand later** -- broad topics dead in 2025
- Micro-niche example: "cosmetics for everyone" narrowed to "skincare for rosacea" = audience **5x smaller** but **revenue increased**

### Phased Expansion

| Phase | Timeline | Focus |
|-------|----------|-------|
| Authority | Months 1-6 | Core niche dominance |
| Expansion | Months 7-12 | Adjacent topics |
| Diversification | Year 2+ | Broader audience |

### High-CPM Niches

| Niche | CPM Range |
|-------|-----------|
| Finance | $12+ |
| Business / SaaS | $8-$14 |
| Education | $5-$12 |
| Tech | $4-$8 |

## Repurposing Workflows

### YouTube Long-Form to Shorts

- Extract self-contained **"aha" moments**
- **"Hook-value bomb-CTA"** structure = **74% better** than continuous clips
- One **20-30 min** video = **10-20 Shorts**
- AI clipping tools reduce time **70-90%**
- **No TikTok watermarks** (algorithm suppresses them)

### YouTube to Blog

- Embed video for Google SEO value
- Add **Key Moments** via schema markup
- SEO synergy between video and written content

### YouTube to LinkedIn

- Professional angle reframe
- **150-word hook** + 3 key takeaways format

### YouTube to X (Twitter) Thread

- Hook tweet + **4-6 insight tweets** + CTA tweet

### YouTube to Email Newsletter

- Subject line A/B test
- Preview text optimization
- **200-word distillation** + video link

### YouTube to Podcast

- Works for **interview/discussion format only**
- Extract to standalone audio file

### Community Post (Same-Day)

- Image + caption + CTA
- Publish same day as video for cross-promotion

### Universal Rules

- AI tools reduce repurposing time by **70-90%**
- **No watermarks** when cross-posting between platforms
- Each platform gets a **native-format** adaptation, not a copy-paste

## Competitor Keyword Gap Analysis

### Workflow

1. Identify **3-5 competitors** in your niche
2. Export their top-performing videos
3. Identify **outliers** (3-10x their average views)
4. Reverse-engineer why outliers performed
5. Check comments for **unaddressed questions**
6. Use YouTube Analytics **"What your audience watches"** report

### Tools

| Tool | Price | Use Case |
|------|-------|----------|
| vidIQ | Free-$49/mo | Keyword research, competitor tracking |
| OutlierKit | **$9/mo** | Outlier video detection |
| TubeBuddy | Free-$49/mo | Keyword explorer, A/B testing |

## Integration Architecture

### API Access Tiers

| Data Type | API | Auth | Notes |
|-----------|-----|------|-------|
| Public data | Data API v3 | API key | **10K units/day** quota |
| Search queries | Data API v3 | API key | **100 units** per search call |
| Own analytics | Analytics API | OAuth | Channel owner only |
| Bulk export | Reporting API | OAuth | Channel owner only |
| Competitor public data | Data API + Social Blade | API key | No private metrics |
| Keyword trends | DataForSEO Google Trends | API key | `type: youtube` parameter |
| SERP data | DataForSEO YouTube SERP API | API key | -- |
| Transcripts | MCP servers | Varies | Third-party tools |

### Limitations

- **No competitor private data** accessible via any API
- **TubeBuddy and vidIQ have zero public APIs**
- Data API quota resets daily at Pacific midnight

---

## Key Constraints & Gotchas

- Broad/general channels are dead in 2025 -- niche-first is mandatory
- Shorts older than ~30 days lose algorithmic push; long-form evergreen is unaffected
- Playlists rank independently -- treat them as SEO assets, not just organization
- "Hook-value bomb-CTA" structure for Shorts outperforms raw clips by 74%
- No TikTok watermarks on any cross-posted content
- TubeBuddy and vidIQ have no APIs -- cannot automate their data
- Data API quota is 10K units/day; search costs 100 units per call (max 100 searches/day)
- Competitor private analytics (retention, RPM, CTR) are never accessible
- Updating old evergreen content can yield 106%+ traffic increase -- do not just publish and forget
- Micro-niching can shrink audience 5x but increase revenue -- smaller is often better
- Series playlists enforce watch order; regular playlists do not

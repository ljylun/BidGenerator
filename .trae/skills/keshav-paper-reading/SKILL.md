---
name: keshav-paper-reading
description: >
  Apply Keshav's three-pass method to read, analyze, summarize, or review any research paper.
  Use this skill whenever the user uploads or references a research paper, academic article, or
  conference paper and asks to read it, summarize it, review it, explain it, critique it, or
  extract insights from it. Also trigger when the user asks how to do a literature survey, wants
  to compare multiple papers, or asks questions like "what does this paper argue?", "is this paper
  good?", or "what are the main contributions?". Even if the user just says "read this paper" or
  "tell me about this paper", use this skill — don't just skim and summarize freehand.
---

# Paper Reading Skill (Keshav's Three-Pass Method)

This skill guides structured reading and analysis of research papers using the three-pass approach.
Choose how many passes to apply based on the user's goal (see Pass Selection below).

---

## Pass Selection Guide

| User Goal | Passes to Apply |
|---|---|
| Quick triage / "is this relevant?" | Pass 1 only |
| General understanding / summary | Passes 1 + 2 |
| Deep review / critique / reproduce | All 3 passes |
| Literature survey | Pass 1 on all; Passes 1+2 on key papers |

Always state which passes you are applying and why before beginning.

---

## Pass 1 — Bird's-Eye View (~5–10 minutes of reading)

**What to read:**
1. Title, abstract, introduction
2. Section and sub-section headings (scan only)
3. Conclusions
4. References (note which ones you recognize)

**Output the Five Cs:**

1. **Category** — What type of paper is this?
   - Measurement / empirical study
   - Analysis of an existing system
   - Description of a new system or prototype
   - Theoretical / proof-based
   - Survey / literature review

2. **Context** — Which papers/fields does it relate to? What theoretical basis does it use?

3. **Correctness** — Do the stated assumptions appear valid at first glance?

4. **Contributions** — What does the paper claim to contribute? (List 2–5 bullet points)

5. **Clarity** — Is the paper well-written? Are the abstract and headings coherent?

**Decision point after Pass 1:**
- If the paper is not relevant → stop here and say so.
- If the paper is relevant but outside the user's specialty → Pass 1 output may be sufficient.
- If the user needs to grasp the content → proceed to Pass 2.

---

## Pass 2 — Content Grasp (~up to 1 hour of reading)

**What to do:**
- Read carefully but skip proofs and deep technical derivations.
- Note key points and supporting evidence.
- Examine every figure, diagram, and graph:
  - Are axes labeled correctly?
  - Are error bars present where needed?
  - Do the visuals actually support the claims?
- Mark important unread references for follow-up.

**Output:**
- **Main Thesis**: One or two sentences capturing the paper's central argument.
- **Evidence & Methods**: How do the authors support their claims? (experiments, proofs, case studies?)
- **Key Figures**: Note which figures are most important and what they show.
- **Gaps / Questions**: What is unclear, unproven, or requires background reading?
- **References to Follow**: List any cited works flagged as important for deeper understanding.

**Decision point after Pass 2:**
- If the paper remains unclear (unfamiliar domain, complex proofs) → note this explicitly.
  Options: (a) set aside, (b) read background first, (c) proceed to Pass 3.
- If the user needs only to understand the paper, not critique it → stop here.

---

## Pass 3 — Deep Understanding (~1–5 hours; use for reviews and deep dives)

**Approach — Virtual Re-implementation:**
Attempt to mentally re-create the work from scratch, making the same assumptions as the authors.
Compare your re-creation to what the paper actually does.

**What to examine:**
- Challenge **every assumption** in every statement.
- Identify the innovations: what is genuinely new vs. incremental?
- Spot **hidden failings**: unstated assumptions, missing baselines, cherry-picked results.
- Evaluate proof and presentation techniques — could they be done better?
- Note ideas for **future work** or extensions.

**Output:**
- **Structural Reconstruction**: Outline the paper's architecture from memory.
- **Innovations**: What is genuinely novel? (Be specific.)
- **Implicit Assumptions**: List assumptions the authors make but do not state.
- **Weaknesses**: Missing citations, questionable experimental design, unsubstantiated claims.
- **Strong Points**: What the paper does particularly well.
- **Future Directions**: What experiments or follow-up work would you suggest?
- **Overall Verdict**: If writing a review, give a clear recommendation with justification.

---

## Literature Survey Mode

Use when the user wants to survey a research area rather than read a single paper.

### Step 1 — Seed Search
- Use Google Scholar / Semantic Scholar with well-chosen keywords.
- Find 3–5 recent papers in the area.
- Do **Pass 1** on each.
- Read their **Related Work** sections carefully.
- Look for a recent **survey paper** — if found, read it (Pass 2) and use it as the backbone.

### Step 2 — Identify Key Work
- Find **shared citations** and **repeated author names** across the seed papers.
- These are the landmark papers and leading researchers in the field.
- Download and set aside the key papers.
- Visit key researchers' websites → identify **top conferences** in the field.

### Step 3 — Conference Proceedings Scan
- Go to the top conference websites.
- Scan recent proceedings (Pass 1 on each relevant paper).
- Identify high-quality recent work not already in your set.

### Step 4 — Synthesis
- Do **Pass 1 + 2** on all collected papers.
- If a key paper is repeatedly cited but missing → obtain and read it.
- Iterate until citations converge (no new key papers appear).

**Output for a survey:**
- Thematic grouping of papers (by approach, by year, by problem type)
- Timeline of key contributions
- Open problems and research gaps
- Recommended reading order for a newcomer

---

## Output Formatting

- **Always label** which pass you are completing.
- Use the structured headers above for each pass.
- Be explicit about what was **read** vs. **inferred** vs. **unclear**.
- If the paper is long and only partially processed in a pass, note what was covered.
- For Pass 1, keep output concise (half a page or less).
- For Pass 2, a full structured summary is appropriate.
- For Pass 3, a detailed critique matching conference review format is appropriate.

---

## Reference

Based on: S. Keshav, "How to Read a Paper," ACM SIGCOMM CCR, 2007.
See `/references/keshav-summary.md` for a condensed reference card.

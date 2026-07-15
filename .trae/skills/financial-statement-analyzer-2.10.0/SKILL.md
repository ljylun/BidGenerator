---
name: financial-statement-analyzer
description: >-
  Deep analysis of corporate balance sheets, income statements, and cash flow
  statements. Quantifies fraud probability (Beneish M-Score, Piotroski F-Score),
  identifies earnings manipulation and operational pathologies, and generates
  illustrated expert diagnostic reports with prioritized management recommendations.
  Supports .xlsx/.xls/.csv/.pdf/.png/.jpg/.docx inputs. This skill should be used
  when the user uploads financial statement files, mentions keywords like
  "分析报表"/"财务报表"/"分析财报"/"三张表"/"财务造假"/"勾稽"/"M-Score"/"杜邦分析",
  or issues commands like `/analyze` or `@财务报表分析专家`.
agent_created: true
---

# 财务报表分析专家 (Financial Statement Analyzer)

## Purpose

Analyze corporate financial statements through a three-tier funnel diagnostic engine,
producing structured HTML reports with Chart.js visualizations, risk scoring, and
actionable management recommendations.

## Trigger Conditions

Automatically activate when ANY of the following occurs:

- **File upload**: `.xlsx`, `.xls`, `.csv`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`, `.docx`
- **Keywords**: "分析报表", "财务报表", "分析一下财报", "分析一下财务报表", "分析财报", "分析财务报告", "帮我分析报表", "三张表", "报表分析", "财务造假", "粉饰", "虚增", "舞弊", "勾稽", "科目异常", "财务风险", "红灯信号", "M-Score", "F-Score", "存贷双高", "应收膨胀", "商誉减值", "现金流分析", "杜邦分析", "比率分析"
- **Commands**: `@财务报表分析专家`, `/analyze`, `/quick-diagnosis`
- **Combined**: File path + any analysis-related phrase → immediate deep diagnosis

## Diagnostic Modes

### Quick Diagnosis (≤5 seconds)
Parse surface data → data validation → account mapping → parallel computation → summary card.
Output: health indicator + Z/M/F-Score + top-3 risks + one-sentence diagnosis.

### Deep Diagnosis (6-step interactive)
1. **Structure confirmation**: Show detected report structure, industry, accounting standard
2. **Data confirmation**: Display extracted historical values
3. **Income statement diagnosis**: Red flags + ratios + attribution
4. **Balance sheet diagnosis**: Balance check + red flags + asset quality
5. **Cash flow diagnosis**: Cash reconciliation + 8 patterns + CCC *(skip if no CF statement)*
6. **Comprehensive report**: Full three-tier report + action plan + recommendations

## Three-Tier Funnel Engine

| Tier | Name | Content | Typical Time |
|------|------|---------|-------------|
| L1 | Emergency Triage | Health lights, Z/M/F-Score, 21 red flags, cash flow patterns, one-line diagnosis | ≤5s |
| L2 | Specialist Clinic | 6-dim radar chart, DuPont waterfall, industry percentile, risk heatmap, 3 scenarios | 30-90s |
| L3 | Expert Consultation | 8 cross-checks, accounting policy analysis, fraud risk, related-party penetration, compliance redlines, root-cause analysis + action plan | 60-180s |

## Input Formats

| Format | Extensions | Parser | Notes |
|--------|-----------|--------|-------|
| Excel | `.xlsx`, `.xls`, `.csv` | openpyxl + pandas | Direct extraction |
| PDF | `.pdf` | pdfplumber | Auto-detect audit reports |
| Image | `.png`, `.jpg`, `.tiff`, `.bmp`, `.webp` | pytesseract OCR | Light preprocessing (contrast + sharpen) |
| Word | `.docx` | python-docx | Table extraction + merged cells |
| Paste | tab/CSV | pandas | Auto-detect delimiter |

All file parsing routes through `scripts/parse_router.py` → `parse_financial_document(filepath)`.
See `references/account-mapping.yaml` for the three-level account mapping dictionary.

### 🈶 Chinese Encoding Recovery Protocol (v2.10, MANDATORY)

When reading Chinese text from `.xls` files via bash/PowerShell, console output may display
garbled characters (`��`). **NEVER guess content from garbled output.**

**Required verification procedure:**
```python
v = str(sh.cell_value(r, c)).strip()
print(f'hex: {v.encode("utf-8").hex()}')
# Then decode: bytes.fromhex(hex_str).decode('utf-8')
```

**Company name confirmation checklist** (complete before generating ANY report):
- [ ] Extract and hex-decode company full names from every sheet containing them
- [ ] Cross-reference with Sheet 0 (summary) abbreviations
- [ ] Verify consistency across years (e.g., 2024="工程公司", 2025="水公司")
- [ ] Use hex-decoded names in reports — never guessed names

## Data Quality Validation (4 Levels)

| Level | Scope | Action on Failure |
|-------|-------|-------------------|
| L1 Completeness | Three statements present, BS balanced (<1% tolerance), currency unit identified | Fatal — block analysis |
| L2 Consistency | Period consistency, currency consistency, sign conventions | Auto-correct |
| L3 Reasonability | Extreme values, jumps, negative/zero checks | Flag as warning |
| L4 Standard Version | New revenue/lease/financial instrument standards | Record version |

Execute `scripts/data_validator.py` → `DataValidator.validate_all()` before generating reports.

## Output Report System (v2.6, Enforced)

### Decision Matrix

```
                   Single Company                    Multi-Company / Group
        ┌──────────────────────────┐    ┌──────────────────────────────┐
  Single│ Scenario A: Single+Single │    │ Scenario B: Group+Single      │
   Year │ Report → L1/L2/L3        │    │ Group rpt → Sub rpts → L1/L2/L3│
        ├──────────────────────────┤    ├──────────────────────────────┤
  Multi │ Scenario C: Single+Multi  │    │ Scenario D: Group+Multi (full) │
   Year │ Multi rpt → Yrly → L1/L2/L3│   │ Multi → Yrly Grp → Subs → L1/L2/L3│
        └──────────────────────────┘    └──────────────────────────────┘
```

### Data Recognition Rules

| Condition | Classification |
|-----------|---------------|
| Multiple BS/IS sheets in Excel, or user states parent-subsidiary | Group / Multi-company |
| Data spans multiple years/periods | Multi-year |
| User provides multiple year files at once | Multi-year |
| Single file, single company, single year | Single company single year |

### Output Order (Iron Rule)

```
Multi-year + Group → Multi-year summary → Yearly group → Per-company yearly → L1/L2/L3
Multi-year + Single → Multi-year summary → Yearly reports → L1/L2/L3
Single-year + Group → Group report → Per-company reports → L1/L2/L3
Single-year + Single → Comprehensive report → L1/L2/L3
```

### Report Templates

**Comprehensive Report (.html)** — Hand-generated, Chart.js charts:
Header + KPI cards (4-col grid) + P&L waterfall + BS structure + ratio cards (6-9 items) +
Findings (P0/P1/P2, ≥5 items) + Diagnosis + Data verification.

**Multi-Year Report (.html)** — Hand-generated, comparison focus:
Executive summary + KPI comparison table + Per-company cross-year + Ratio trends +
Risk assessment matrix + Strategic recommendations.

**L1/L2/L3 Reports** — Pipeline auto-generated (ECharts):
L1: health lights, Z/M/F-Score, top-5 risks, cash patterns. L2: radar, DuPont, box plots.
L3: cross-checks, accounting policy, fraud risk, compliance.

Full report content templates → `references/report-templates.md`

### Naming Convention

| Type | Format | Example |
|------|--------|---------|
| Multi-year summary | `{Group/Co}_YYYY-YYYY_两年综合财务分析报告.html` | `哈尔滨优方集团_2024-2025_两年综合财务分析报告.html` |
| Annual comprehensive | `{Co}_YYYY年_财务分析报告.html` | `科技公司_2025年_财务分析报告.html` |
| Group annual | `{Group}_YYYY年_财务分析报告.html` | `哈尔滨优方集团_2025年_财务分析报告.html` |
| L1/L2/L3 | `{Co}_YYYY_L{N}_{Name}.html` | `科技公司_2025_L1_急诊初筛.html` |

## Core Capability Matrix

| # | Capability | Implementation |
|---|-----------|---------------|
| 1 | Cross-check verification | 8 categories, `scripts/verify_crosschecks.py` + `references/verification-rules.yaml` |
| 2 | Accounting estimate aggressiveness | Depreciation/bad-debt/capitalization vs. industry, `references/industry-benchmarks.json` |
| 3 | Operational reality reconstruction | Suspicious entries → operational actions mapping |
| 4 | Illustrated reports | Three-tier + Chart.js/ECharts, `scripts/render_charts.py` |
| 5 | Fraud quantification | Beneish M-Score (`scripts/compute_mscore.py`) + Piotroski F-Score |
| 6 | Audit procedure mapping | Red flags → simulated procedures → checklist (`templates/audit_checklist.md`) |
| 7 | Case pattern matching | Cosine similarity against `references/case-library.json` |
| 8 | Related-party penetration | 6-dim detection matrix, `scripts/related_party_matcher.py` |
| 9 | Practical management advice | `scripts/generate_advice.py` + `references/advice-templates.yaml` |
| 10 | Data quality scoring | 4-dim scorecard, `scripts/data_quality_scorer.py` |
| 11 | AR aging estimation | BS/IS → aging distribution, `scripts/ar_aging_estimator.py` |
| 12 | Multi-period merging | `scripts/multi_period_merger.py` |
| 13 | Excel export | 4-sheet summary, `scripts/excel_exporter.py` |

## Key Technical Specifications

### Formula-First Principle
- All ratios/indicators computed in real-time via Python functions in `scripts/compute_ratios.py`
- Never use pre-computed or hardcoded values
- Generate configuration snapshot (JSON) for each analysis, enabling exact reproduction

### Unit Management (v2.0, Enforced)
- Store all raw data in **yuan** (元), never convert mid-pipeline
- Use `to_wan()` / `to_wan_array()` for display conversion — **never manual division**
- Table data and chart data must source from the same data object

### Chart Container Rules (v2.1.1, Enforced)
- **Use `height` not `min-height`** for chart containers
- Correct: `.chart-box { height: 300px; }` + `.chart-box canvas { flex: 1; min-height: 0; }`
- Wrong: `.chart-box { min-height: 300px; }`

### Print/PDF Export (v2.1, Enforced)
- All reports must include `@media print` with `-webkit-print-color-adjust: exact !important`
- Header backgrounds preserved in print
- `break-inside: avoid` on cards, findings, chart boxes
- `@page { size: A4; margin: 15mm 12mm; }`
- `Chart.defaults.animation = { duration: 0 }`

### Common Pitfalls

| Error Type | Manifestation | Prevention |
|-----------|---------------|------------|
| Unit ×10 error | Chart shows 4088万 (actual 408.8万) | Use `to_wan()`, never manual ÷10000 |
| Column swap | AR year-start/year-end reversed | Auto-alert on >500% change + row-number cross-check |
| Missing line items | Omitted investment income | Completeness check via REQUIRED_IS_ITEMS |
| Data entry error | Wrong retained earnings value | BS balance check + total cross-validation |
| Name misattribution | 哈尔滨→绍兴, 水务→水利 | Hex-decode verification (see Encoding Protocol above) |

## Risk Classification

| Score | Grade | Action |
|-------|-------|--------|
| 0-20 | A 🟢 | Routine monitoring |
| 21-40 | B 🟡 | Track trends |
| 41-60 | C 🟠 | Targeted investigation |
| 61-80 | D 🔴 | Recommend external audit |
| 81-100 | E 💀 | Suspend cooperation/investment |

## Diagnosis Label System

- **Manipulation Risk**: Revenue / Cost-Expense / Asset / Off-BS Liability
- **Operational Pathology**: Profit / Working Capital / Cash / Growth
- **Financial Risk**: Debt Service / Leverage / FX-Interest Rate

## Bundled Resources

### Scripts (`scripts/`)
- `parse_router.py` — Unified parsing entry (Excel/PDF/Image/DOCX/Paste)
- `parse_excel.py`, `parse_pdf.py`, `parse_image.py`, `parse_docx.py`, `parse_paste.py`, `parse_audit_report.py` — Format-specific parsers
- `data_validator.py` — Data validation engine (Unit class, DataValidator class)
- `compute_ratios.py` — Ratio computation
- `compute_mscore.py` — Beneish M-Score
- `scan_redflags.py` — 21 red flag scanning
- `verify_crosschecks.py` — 8-category cross-check verification
- `detect_anomalies.py` — Anomaly detection
- `generate_report.py`, `render_charts.py` — Report and chart generation
- `generate_advice.py` — Management advice generation
- `match_cases.py` — Case library matching
- `run_pipeline.py` — End-to-end pipeline entry (v2.3+)
- `multi_period_merger.py`, `data_quality_scorer.py`, `ar_aging_estimator.py`, `related_party_matcher.py`, `excel_exporter.py`, `rd_capitalization_detector.py` — v2.8+ modules

### References (`references/`)
- `account-mapping.yaml` — Three-level account mapping
- `red-flags.yaml` — 21 red flag rules
- `verification-rules.yaml` — 8-category cross-check rules
- `compliance-redlines.yaml` — 14 compliance redlines
- `industry-benchmarks.json` — Industry benchmark parameters
- `case-library.json` — Case feature vector library
- `question-templates.yaml` — 20 preset question templates
- `advice-templates.yaml` — Advice template library
- `report-templates.md` — Detailed report content templates

### Templates (`templates/`)
- `audit_checklist.md` — 7-stage audit checklist
- `report_comprehensive.html`, `report_level1.html`, `report_level2.html`, `report_level3.html` — HTML report templates

### Tests (`tests/`)
- `test_ratios.py`, `test_mscore.py`, `test_redflags.py`, `test_parse_router.py`, `test_parse_image.py`, `test_integration.py` — Unit and integration tests
- `fixtures/sample_manufacturer.json` — Test fixture

## Error Handling Strategy

| Level | Condition | Action |
|-------|-----------|--------|
| 🔴 Fatal | Missing all 3 statements, undetermined currency unit, <2 periods of data | Block analysis |
| 🟠 Warning | Partial missing items, BS imbalance >0.1% | Continue with degraded output, note limitations |
| 🟡 Info | Old standard accounts, LLM unavailable | Continue, annotate |

## Security & Privacy

- All data processed in memory, cleared after analysis
- Auto-redact before LLM calls: remove entity names, replace exact amounts with ranges
- Supports private deployment for on-premise data boundaries

---

> **Disclaimer**: Reports generated by AI analysis based on accounting data, for internal reference only.
> "Abnormal", "suspicious" and similar terms indicate financial metric deviations from norms, not legal determinations.
>
> © 2026 优方皑尔 Uform Ai

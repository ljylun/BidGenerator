# Report Content Templates

Detailed content specifications for each report type.

## A. Comprehensive Financial Analysis Report (.html)

Manually generated, Chart.js charts.

| Section | Required Content |
|---------|-----------------|
| Header | Full company/group name, period, standard, generation date |
| KPI Cards | 4-column grid: revenue, net profit, gross/net margin, assets/debt ratio |
| Income Statement | Full P&L + revenue/expense waterfall chart (Chart.js bar) |
| Balance Sheet | Asset structure bar + liability/equity comparison |
| Ratio Analysis | 6-9 ratio cards (color-coded ratings) + trend chart |
| Key Findings | P0(red)/P1(yellow)/P2(blue) tiered, each with tag+title+detail |
| Comprehensive Diagnosis | Risk grade + prioritized actions (P0 this week / P1 this month) |
| Data Verification | Source files + BS balance status + data limitations |

## B. Multi-Year Comprehensive Report (.html)

Manually generated, comparison-focused.

| Section | Required Content |
|---------|-----------------|
| Executive Summary | One-line core conclusion + 4 key changes |
| KPI Comparison Table | Yearly values + change rate (green=improve, red=deteriorate) |
| Per-Company/Item Comparison | Two-year P&L side-by-side + change rate + trend interpretation |
| Ratio Trend Chart | Gross/net margin/ROE/debt ratio 2-year bar comparison |
| Risk Assessment Matrix | 3-col × 2-row matrix (Resolved/Watching/New Risk vs Improving/Optimizing/Watch) |
| Strategic Recommendations | Deep recommendations based on 2-year trends |

## C. L1/L2/L3 Tiered Reports

Pipeline auto-generated (ECharts charts).

| Level | Content |
|-------|---------|
| L1 Emergency Triage | Health lights, Z/M/F-Score, Top-5 risks, cash flow pattern, one-line diagnosis |
| L2 Specialist Clinic | 6-dim radar, DuPont waterfall, industry percentile box plot, risk heatmap, 3-scenario forecast |
| L3 Expert Consultation | Cross-check verification, accounting policy analysis, fraud risk assessment (with timeline), related-party penetration, compliance redlines, root-cause analysis + action plan |

## Scenario-Specific Templates

### Scenario A: Single Company, Single Year
```
Priority 1: {Company}_YYYY年_财务分析报告.html
  ├─ KPI cards
  ├─ P&L analysis (waterfall + expense ratio)
  ├─ BS analysis (asset structure + liability/equity)
  ├─ Ratio radar (profit/debt/operations/growth)
  ├─ Key findings (P0/P1/P2, ≥5 items)
  ├─ Diagnosis & recommendations (by role/priority)
  └─ Data verification

Priority 2: {Company}_YYYY_L1/L2/L3_*.html (pipeline auto)
```

### Scenario B: Group, Single Year
```
Priority 1: {Group}_YYYY年_财务分析报告.html
  ├─ Group structure & ownership diagram
  ├─ Group consolidated KPIs (4 cards)
  ├─ 3-company metrics comparison charts
  ├─ Per-company analysis (P&L + ratio cards + key findings)
  ├─ Consolidated analysis (with internal offset notes)
  ├─ Group key findings (P0/P1/P2, ≥6 items)
  └─ Diagnosis & recommendations

Priority 2: {Company}_YYYY年_财务分析报告.html (one per subsidiary)
Priority 3: {Company}_YYYY_L1/L2/L3_*.html (pipeline auto)
```

### Scenario C: Single Company, Multi-Year
```
Priority 1: {Company}_YYYY-YYYY_两年综合财务分析报告.html
  ├─ Executive summary
  ├─ Yearly KPI comparison table
  ├─ P&L year-by-year comparison
  ├─ BS year-by-year comparison
  ├─ Ratio trend chart
  ├─ Revenue/expense waterfall (two years side-by-side)
  ├─ Risk assessment matrix (4 quadrants)
  └─ Strategic recommendations

Priority 2: {Company}_YYYY年_财务分析报告.html (one per year)
Priority 3: {Company}_YYYY_L1/L2/L3_*.html (one per year, pipeline auto)
```

### Scenario D: Group, Multi-Year (Most Complete)
```
Priority 1: {Group}_YYYY-YYYY_两年综合财务分析报告.html
  ├─ Executive summary (group-wide changes)
  ├─ Group KPI year-by-year comparison
  ├─ Per-company cross-year deep comparison
  ├─ Inter-company horizontal comparison
  ├─ Risk assessment matrix (company × year)
  ├─ Revenue/profit structure evolution
  └─ Group strategic recommendations

Priority 2: {Group}_YYYY年_财务分析报告.html (one per year)
Priority 3: {Company}_YYYY年_财务分析报告.html (one per company per year)
Priority 4: {Company}_YYYY_L1/L2/L3_*.html (one per company per year, pipeline auto)
```

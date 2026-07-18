---
name: financial-analysis
description: |
  Build institutional-grade financial analyses: comparable company analysis, DCF valuation, LBO model, and Excel spreadsheet workflows.
  
  **Functions:**
  - Comps Analysis: Build comparable company analyses with valuation multiples
  - DCF Model: Discounted Cash Flow valuation models
  - LBO Model: Leveraged Buyout modeling
  - 3-Statements: Income Statement, Balance Sheet, Cash Flow integration
  
  **Activate when:** User wants financial modeling, company valuation, investment analysis, M&A comps, Excel reports
  
  **Note:** This skill provides analysis methodology. Real-time financial data requires external data sources (APIs, Bloomberg, etc.)
---

# Financial Analysis Skills

This skill provides comprehensive financial analysis capabilities for investment banking, equity research, and corporate finance work.

## Available Modules

### 1. Comps Analysis (可比公司分析)
Build institutional-grade comparable company analyses with:
- Operating metrics (Revenue, Growth, Margins, EBITDA)
- Valuation multiples (EV/Revenue, EV/EBITDA, P/E)
- Statistical benchmarking (Median, Quartiles)
- Excel output with proper formatting

### 2. DCF Model (DCF 估值)
Discounted Cash Flow modeling:
- Revenue & cash flow projections
- WACC calculation
- Terminal value (Perpetuity growth vs. Exit multiple)
- Sensitivity analysis
- Enterprise value to equity value桥接

### 3. LBO Model (LBO 模型)
Leveraged Buyout analysis:
- Sources & uses of funds
- Debt schedule (Revolver, Term Loan, Subordinated)
- IRR & MOIC calculations
- Exit analysis

### 4. 3-Statements (三表模型)
Integrated financial model:
- Income Statement
- Balance Sheet
- Cash Flow Statement
- Working capital schedules

---

## Quick Start

### Comps Analysis
To analyze comparable companies:

1. **Define peer group** - Select 5-10 comparable companies
2. **Gather data** - Revenue, EBITDA, multiples from financial statements
3. **Build structure** - Set up Excel with proper headers
4. **Calculate metrics** - Margins, growth rates, valuation multiples
5. **Add statistics** - Median, quartiles for context

### DCF Valuation
To value a company using DCF:

1. **Project financials** - 5-10 year revenue/EBITDA forecast
2. **Calculate FCF** - Free Cash Flow = EBIT(1-Tax) + D&A - CapEx - Working Capital
3. **Determine WACC** - Weighted Average Cost of Capital
4. **Discount FCF** - Present value of projected FCF
5. **Terminal value** - Perpetuity growth or exit multiple method
6. **Sum and bridge** - EV - Net Debt = Equity Value

---

## Output Format

### Excel Structure

```
┌─────────────────────────────────────────────┐
│ [COMPANY] - VALUATION ANALYSIS              │
│ As of [Date] | All figures in USD Millions │
├─────────────────────────────────────────────┤
│ OPERATING METRICS                           │
│ Company | Revenue | Growth | Gross Margin   │
├─────────────────────────────────────────────┤
│ Company A   | 1,000   | 10%   | 45%        │
│ Company B   | 1,500   | 12%   | 52%        │
│ ...         |         |       |             │
│ Median      | =MEDIAN | =MEDIAN| =MEDIAN   │
├─────────────────────────────────────────────┤
│ VALUATION MULTIPLES                         │
│ Company | EV/Rev | EV/EBITDA | P/E          │
├─────────────────────────────────────────────┤
│ Company A   | 5.0x   | 12.0x  | 25.0x     │
│ Company B   | 6.5x   | 15.0x  | 30.0x      │
│ ...         |         |        |            │
│ Median      | =MEDIAN | =MEDIAN| =MEDIAN   │
└─────────────────────────────────────────────┘
```

---

## Key Formulas

### Valuation Multiples
```
EV/Revenue = Enterprise Value / Revenue
EV/EBITDA = Enterprise Value / EBITDA
P/E = Market Cap / Net Income
```

### Free Cash Flow
```
FCF = EBIT × (1 - Tax Rate) + D&A - CapEx - Δ Working Capital
```

### DCF Terminal Value
```
Perpetuity Growth: TV = FCF(n) × (1 + g) / (WACC - g)
Exit Multiple: TV = EBITDA(n) × Exit Multiple
```

### WACC Calculation
```
WACC = (E/V) × Re + (D/V) × Rd × (1 - Tc)
Where:
  E = Equity Value
  D = Debt Value  
  V = E + D
  Re = Cost of Equity
  Rd = Cost of Debt
  Tc = Corporate Tax Rate
```

---

## Best Practices

### Data Sources
- **Primary**: Bloomberg, FactSet, S&P Capital IQ
- **Secondary**: SEC filings (10-K, 10-Q), company reports
- **Verify**: Cross-check numbers across sources

### Quality Checks
- ✓ Margins: Gross > EBITDA > Net (always)
- ✓ Multiples: Reasonable ranges (EV/EBITDA: 8-25x typical)
- ✓ Growth: Higher growth → higher multiples
- ✓ Comparability: Same industry, similar size

### Documentation
- Source every number (Bloomberg ticker, SEC filing page)
- Document assumptions (growth rates, terminal growth)
- Add hyperlinks where possible
- Date-stamp analysis

---

## Common Mistakes to Avoid

❌ Mixing time periods (LTM vs Quarterly)
❌ Using different currencies without conversion
❌ Hardcoding values instead of cell references
❌ Missing statistics (median, quartiles)
❌ Including non-comparable companies
❌ Forgetting to bridge EV to Equity Value

---

## Notes

1. **This skill provides methodology** - Actual financial data requires subscriptions (Bloomberg, FactSet, etc.)

2. **Excel templates** - Can generate structured Excel files with proper formulas

3. **Analysis depth** - Adjust based on purpose (quick pitch vs. IC memo)

4. **Industry variations** - SaaS needs different metrics than industrials

---

*Based on anthropics/financial-services-plugins - converted for OpenClaw*

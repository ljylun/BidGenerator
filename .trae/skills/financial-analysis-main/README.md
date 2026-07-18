# 📊 Financial Analysis Skill

> Institutional-grade financial analysis skills for AI agents — Comps, DCF, LBO & 3-Statement modeling.

Converted from [Anthropic's Financial Services Plugins](https://github.com/anthropics/financial-services-plugins) for the [OpenClaw](https://openclaw.ai) AI agent platform.

## ✨ Features

| Module | Description |
|--------|-------------|
| **Comps Analysis** | Comparable company analysis with valuation multiples (EV/Revenue, EV/EBITDA, P/E) and statistical benchmarking |
| **DCF Model** | Discounted Cash Flow valuation with WACC, terminal value, and sensitivity analysis |
| **LBO Model** | Leveraged Buyout modeling with debt schedules, IRR & MOIC calculations |
| **3-Statements** | Integrated Income Statement, Balance Sheet, and Cash Flow Statement model |

## 📁 Project Structure

```
financial-analysis/
├── SKILL.md                          # Skill definition & methodology guide
├── _meta.json                        # Metadata, dependencies & capabilities
├── scripts/
│   └── financial_templates.py        # Excel template generator (openpyxl)
├── templates/                        # (reserved for Excel templates)
└── references/                       # (reserved for reference materials)
```

## 🚀 Quick Start

### As an OpenClaw Skill

1. Copy the skill directory to your OpenClaw skills location:
   ```bash
   cp -r financial-analysis/ ~/.openclaw/skills/financial-analysis/
   ```
2. Register the skill in your `openclaw.json`:
   ```json
   {
     "skills": {
       "entries": {
         "financial-analysis": { "enabled": true }
       }
     }
   }
   ```
3. Restart OpenClaw Gateway.

### Generate Excel Templates

```bash
pip install openpyxl
python scripts/financial_templates.py
```

This generates two formatted Excel workbooks:
- `comps_template.xlsx` — Comparable company analysis with Operating Metrics & Valuation sheets
- `dcf_template.xlsx` — DCF model with 5-year projections, terminal value & EV-to-equity bridge

## 📐 Key Formulas

```
EV/Revenue  = Enterprise Value / Revenue
EV/EBITDA   = Enterprise Value / EBITDA
P/E         = Market Cap / Net Income

FCF  = EBIT × (1 - Tax) + D&A - CapEx - Δ Working Capital
WACC = (E/V) × Re + (D/V) × Rd × (1 - Tc)

Terminal Value (Perpetuity) = FCF(n) × (1 + g) / (WACC - g)
Terminal Value (Exit Mult.) = EBITDA(n) × Exit Multiple
```

## ⚠️ Important Notes

- **Methodology only** — This skill provides analysis frameworks and templates. Real-time financial data requires external sources (Bloomberg, FactSet, SEC filings, etc.).
- **Verify all outputs** — Always cross-check AI-generated analyses with qualified financial professionals.
- **Industry-specific** — Different sectors require different metrics (e.g., SaaS vs. Industrials). Adjust accordingly.

## 🔗 Dependencies

- Python ≥ 3.8
- [openpyxl](https://openpyxl.readthedocs.io/) ≥ 3.0 (for Excel generation)

## 📄 License

Based on [anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins). Please refer to the original repository for license terms.

#!/usr/bin/env python3
"""
Apple Inc. FY2026 10-Q Financial Analysis Runner
Uses the financial-statement-analyzer skill to analyze Apple's Q1 and Q2 10-Q filings.

Data source: Apple Inc. FY2026 Q1 & Q2 10-Q (filed with SEC)
Units: Millions of USD
Periods: 
  - "Q1-2025" (3 months ended Dec 28, 2024) 
  - "Q1-2026" (3 months ended Dec 27, 2025)
  - "Q2-2026" (3 months ended Mar 28, 2026) - latest
  - Cumulative six-month periods for trend analysis
"""

import sys
import os
import json

# Add skill scripts to path
SKILL_DIR = r"h:\DEV\MyProjects\BidGenerator\.trae\skills\financial-statement-analyzer-2.10.0\scripts"
sys.path.insert(0, SKILL_DIR)

# ---------------------------------------------------------------------------
# Apple Inc. Financial Data (extracted from 10-Q PDFs, in millions USD)
# ---------------------------------------------------------------------------

# Q1 FY2026 (3 months ended Dec 27, 2025) - Income Statement
Q1_2026_IS = {
    "营业收入": 143756,       # Total net sales
    "营业成本": 74525,        # Total cost of sales
    "研发费用": 10887,        # Research and development
    "销售费用": 7492,         # SG&A combined into sales expense bucket
    "管理费用": 0,            # Included in SG&A above
    "财务费用": -150,         # Other income/(expense) reversed (negative = income)
    "营业利润": 50852,        # Operating income
    "利润总额": 51002,        # Income before tax
    "所得税费用": 8905,       # Provision for income taxes
    "净利润": 42097,          # Net income
    "扣非净利润": 42097,      # Apple doesn't report this separately
}

# Q1 FY2025 (3 months ended Dec 28, 2024) - Income Statement (prior year)
Q1_2025_IS = {
    "营业收入": 124300,
    "营业成本": 66025,
    "研发费用": 8268,
    "销售费用": 7175,
    "管理费用": 0,
    "财务费用": 248,
    "营业利润": 42832,
    "利润总额": 42584,
    "所得税费用": 6254,
    "净利润": 36330,
    "扣非净利润": 36330,
}

# Q2 FY2026 (3 months ended Mar 28, 2026) - Income Statement
Q2_2026_IS = {
    "营业收入": 111184,
    "营业成本": 56403,
    "研发费用": 11419,
    "销售费用": 7477,
    "管理费用": 0,
    "财务费用": 52,
    "营业利润": 35885,
    "利润总额": 35833,
    "所得税费用": 6255,
    "净利润": 29578,
    "扣非净利润": 29578,
}

# Cumulative 6-month data for trend analysis
H1_2026_IS = {
    "营业收入": 254940,       # 143756 + 111184
    "营业成本": 130928,       # 74525 + 56403
    "研发费用": 22306,        # 10887 + 11419
    "销售费用": 14969,        # 7492 + 7477
    "管理费用": 0,
    "财务费用": -98,          # -150 + 52 (net other income)
    "营业利润": 86737,        # 50852 + 35885
    "利润总额": 86835,        # 51002 + 35833
    "所得税费用": 15160,      # 8905 + 6255
    "净利润": 71675,          # 42097 + 29578
    "扣非净利润": 71675,
}

H1_2025_IS = {
    "营业收入": 219659,
    "营业成本": 116517,
    "研发费用": 16818,
    "销售费用": 13903,
    "管理费用": 0,
    "财务费用": 527,
    "营业利润": 72421,
    "利润总额": 71894,
    "所得税费用": 10784,
    "净利润": 61110,
    "扣非净利润": 61110,
}

# Balance Sheets (in millions USD)
# Dec 27, 2025 (Q1 FY2026 end)
BS_2026_Q1 = {
    "货币资金": 45317,
    "交易性金融资产": 21590,       # Current marketable securities
    "应收账款": 39921,
    "其他应收款": 30399,           # Vendor non-trade receivables
    "存货": 5875,
    "其他流动资产": 15002,
    "流动资产合计": 158104,
    "可供出售金融资产": 77888,     # Non-current marketable securities
    "固定资产": 50159,             # PP&E net
    "无形资产": 0,                 # Not separately reported in Q1 BS
    "其他非流动资产": 93146,        # Other non-current assets
    "非流动资产合计": 221193,
    "资产总计": 379297,
    "短期借款": 1997,              # Commercial paper
    "应付账款": 70587,
    "预收款项": 9413,              # Deferred revenue
    "其他流动负债": 68543,
    "一年内到期的非流动负债": 11827,  # Current term debt
    "流动负债合计": 162367,
    "长期借款": 76685,             # Non-current term debt
    "其他非流动负债": 52055,
    "非流动负债合计": 128740,
    "负债合计": 291107,
    "实收资本": 95221,             # Common stock + APIC
    "未分配利润": -2177,           # Accumulated deficit
    "其他综合收益": -4854,         # Accumulated OCI loss
    "所有者权益合计": 88190,
}

# Mar 28, 2026 (Q2 FY2026 end) - Latest
BS_2026_Q2 = {
    "货币资金": 45572,
    "交易性金融资产": 22935,
    "应收账款": 30339,
    "其他应收款": 23172,
    "存货": 6747,
    "其他流动资产": 15349,
    "流动资产合计": 144114,
    "可供出售金融资产": 78088,
    "固定资产": 50116,
    "无形资产": 21334,            # Reported in Q2 BS
    "其他非流动资产": 77430,
    "非流动资产合计": 226968,
    "资产总计": 371082,
    "短期借款": 1997,
    "应付账款": 57349,
    "预收款项": 9331,
    "其他流动负债": 57654,
    "一年内到期的非流动负债": 8310,
    "流动负债合计": 134641,
    "长期借款": 74404,
    "其他非流动负债": 55546,
    "非流动负债合计": 129950,
    "负债合计": 264591,
    "实收资本": 99507,
    "未分配利润": 12359,           # Retained earnings (positive!)
    "其他综合收益": -5375,
    "所有者权益合计": 106491,
}

# Sep 27, 2025 (FY2025 year-end / beginning of FY2026)
BS_2025 = {
    "货币资金": 35934,
    "交易性金融资产": 18763,
    "应收账款": 39777,
    "其他应收款": 33180,
    "存货": 5718,
    "其他流动资产": 14585,
    "流动资产合计": 147957,
    "可供出售金融资产": 77723,
    "固定资产": 49834,
    "无形资产": 11093,
    "其他非流动资产": 72634,
    "非流动资产合计": 211284,
    "资产总计": 359241,
    "短期借款": 7979,
    "应付账款": 69860,
    "预收款项": 9055,
    "其他流动负债": 66387,
    "一年内到期的非流动负债": 12350,
    "流动负债合计": 165631,
    "长期借款": 78328,
    "其他非流动负债": 41549,
    "非流动负债合计": 119877,
    "负债合计": 285508,
    "实收资本": 93568,
    "未分配利润": -14264,
    "其他综合收益": -5571,
    "所有者权益合计": 73733,
}

# Cash Flow Statement - Q1 FY2026 (3 months ended Dec 27, 2025)
CF_Q1_2026 = {
    "经营活动产生的现金流量净额": 53925,
    "投资活动产生的现金流量净额": -4886,
    "筹资活动产生的现金流量净额": -39656,
    "折旧与摊销": 3214,
    "股份支付费用": 3594,           # Share-based compensation
    "购建固定资产无形资产支付的现金": 2373,  # CAPEX
}

# Cash Flow Statement - H1 FY2026 (6 months ended Mar 28, 2026)
CF_H1_2026 = {
    "经营活动产生的现金流量净额": 82627,
    "投资活动产生的现金流量净额": -11054,
    "筹资活动产生的现金流量净额": -61935,
    "折旧与摊销": 6653,
    "股份支付费用": 7122,
    "购建固定资产无形资产支付的现金": 4344,
}

# Cash Flow Statement - H1 FY2025 (6 months ended Mar 29, 2025)
CF_H1_2025 = {
    "经营活动产生的现金流量净额": 53887,
    "投资活动产生的现金流量净额": 12709,
    "筹资活动产生的现金流量净额": -68377,
    "折旧与摊销": 5741,
    "股份支付费用": 6512,
    "购建固定资产无形资产支付的现金": 6011,
}

# Build the standardized data structure
# We'll use quarterly periods for income statement detail and H1 cumulative for trends
data = {
    "periods": ["2025-Q1", "2026-Q1", "2026-Q2"],
    "bs": {
        "2025-Q1": BS_2025,  # Using Sep 2025 as prior period reference for Q1 IS
        "2026-Q1": BS_2026_Q1,
        "2026-Q2": BS_2026_Q2,
    },
    "is": {
        "2025-Q1": Q1_2025_IS,
        "2026-Q1": Q1_2026_IS,
        "2026-Q2": Q2_2026_IS,
    },
    "cf": {
        "2025-Q1": {},  # No Q1 FY2025 CF data available
        "2026-Q1": CF_Q1_2026,
        "2026-Q2": CF_H1_2026,  # Using cumulative for Q2 period
    },
}

# Industry benchmark for Technology/Hardware (Apple-specific)
industry = {
    "label": "Technology/Consumer Electronics",
    "profit_margin_avg": 45.0,   # Apple's gross margin ~45%
    "net_margin_avg": 25.0,      # Apple's net margin ~25%
    "roe_avg": 25.0,             # Apple's ROE is very high
    "current_ratio_avg": 1.2,
    "debt_ratio_avg": 55.0,
    "turnover_avg": 0.80,
}

# ---------------------------------------------------------------------------
# Run the pipeline
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from run_pipeline import run_full_pipeline
    
    output_dir = r"h:\DEV\MyProjects\BidGenerator\Apple_Financial_Reports\FY2026\10-Q\analysis_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Also save the structured data for reference
    data_file = os.path.join(output_dir, "apple_fy2026_data.json")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to: {data_file}")
    
    # Run the full pipeline
    print("\nRunning financial analysis pipeline...")
    paths = run_full_pipeline(
        data=data,
        company_name="Apple Inc. (蘋果公司)",
        company_short="Apple",
        year="FY2026",
        output_dir=output_dir,
        industry=industry,
    )
    
    print(f"\n{'='*60}")
    print(f"Analysis complete! Generated {len(paths)} reports:")
    for p in paths:
        print(f"  -> {p}")
    print(f"{'='*60}")

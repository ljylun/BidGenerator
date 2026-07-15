#!/usr/bin/env python3
"""研发费用资本化率检测器 — 评估研发支出会计处理的激进程度。

功能: 从BS(开发支出变动)和IS(研发费用)推算资本化率,标记异常。
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 行业资本化率参考 (制造业/信息技术/环保等)
INDUSTRY_NORMS: Dict[str, Tuple[float, float, str]] = {
    "水处理/环保": (0.10, 0.20, "10-20%"),
    "制造业": (0.15, 0.25, "15-25%"),
    "信息技术": (0.20, 0.40, "20-40%"),
    "通用": (0.10, 0.25, "10-25%"),
}


def detect_rd_capitalization(
    data: Dict[str, Any],
    industry: str = "通用",
) -> Dict[str, Any]:
    """检测研发费用资本化率。

    核心逻辑:
    - 资本化率 = 当期资本化金额 / (当期资本化金额 + 当期费用化金额)
    - 资本化金额 ≈ BS中开发支出的本期增加额
    - 费用化金额 = IS中研发费用

    Args:
        data: 标准化数据 {periods, bs, is}
        industry: 行业标签

    Returns:
        资本化分析结果
    """
    periods = data.get("periods", [])
    if not periods:
        return {"error": "无数据"}

    results: Dict[str, Any] = {"periods": [], "findings": []}
    norms = INDUSTRY_NORMS.get(industry, INDUSTRY_NORMS["通用"])
    norm_low, norm_high, norm_str = norms

    for period in periods:
        bs = data.get("bs", {}).get(period, {})
        is_data = data.get("is", {}).get(period, {})

        rd_expense = is_data.get("研发费用", 0)
        dev_asset = bs.get("开发支出", 0)  # 期末开发支出余额

        # 推算本期资本化金额
        prev_dev = 0
        if len(periods) > 1:
            idx = periods.index(period)
            if idx > 0:
                prev_bs = data.get("bs", {}).get(periods[idx - 1], {})
                prev_dev = prev_bs.get("开发支出", 0)

        # 本期增加 ≈ 期末-期初(简化,假设无摊销转出)
        cap_amount = max(0, dev_asset - prev_dev) if dev_asset > prev_dev else 0

        # 如果IS中没有研发费用但BS有开发支出,说明全部资本化
        if rd_expense == 0 and dev_asset > 0:
            cap_rate = 1.0
        elif rd_expense + cap_amount > 0:
            cap_rate = cap_amount / (cap_amount + rd_expense) if (cap_amount + rd_expense) > 0 else 0
        else:
            cap_rate = 0

        # 风险评估
        risk = "normal"
        note = ""
        if cap_rate > norm_high:
            risk = "high"
            note = f"资本化率{cap_rate*100:.1f}%远超行业上限{norm_str},当期利润可能虚增{(cap_amount+rd_expense)*(cap_rate-norm_high):.0f}元"
        elif cap_rate > norm_low:
            risk = "watch"
            note = f"资本化率{cap_rate*100:.1f}%在行业{norm_str}范围内,但需关注后续摊销"
        elif cap_rate > 0:
            note = f"资本化率{cap_rate*100:.1f}%,低于行业{norm_str},会计处理保守"
        else:
            note = "无资本化,全部费用化"

        period_result = {
            "period": period,
            "rd_expense": round(rd_expense, 2),
            "dev_asset_balance": round(dev_asset, 2),
            "est_cap_amount": round(cap_amount, 2),
            "cap_rate": round(cap_rate, 4),
            "cap_rate_pct": round(cap_rate * 100, 1),
            "risk": risk,
            "note": note,
        }
        results["periods"].append(period_result)

        if risk == "high":
            results["findings"].append({
                "period": period,
                "severity": "P1",
                "message": f"研发资本化率{cap_rate*100:.1f}%偏高(行业{norm_str}),利润可能虚增",
            })

    # 汇总
    latest = results["periods"][-1] if results["periods"] else {}
    results["latest_cap_rate"] = latest.get("cap_rate_pct", 0)
    results["industry_norm"] = norm_str
    results["industry"] = industry
    results["has_rd_activity"] = any(p["rd_expense"] > 0 or p["dev_asset_balance"] > 0 for p in results["periods"])
    results["risk_level"] = "high" if any(p["risk"] == "high" for p in results["periods"]) else ("watch" if any(p["risk"] == "watch" for p in results["periods"]) else "normal")

    return results


def render_rd_html(rd_result: Dict[str, Any]) -> str:
    """渲染研发资本化分析HTML片段。"""
    if rd_result.get("error") or not rd_result.get("has_rd_activity"):
        return ""

    risk_colors = {"high": "#e74c3c", "watch": "#f39c12", "normal": "#27ae60"}
    risk_labels = {"high": "⚠ 激进", "watch": "关注", "normal": "正常"}
    color = risk_colors.get(rd_result.get("risk_level", "normal"), "#888")

    period_rows = ""
    for p in rd_result.get("periods", []):
        rc = risk_colors.get(p.get("risk", "normal"), "#888")
        period_rows += f'''<tr>
  <td>{p["period"]}</td>
  <td style="text-align:right">¥{p["rd_expense"]/10000:.1f}万</td>
  <td style="text-align:right">{p["cap_rate_pct"]}%</td>
  <td style="color:{rc}">{p["note"]}</td>
</tr>'''

    return f'''<div style="background:#FAFAF8;border:1px solid #D3D1C7;border-radius:8px;padding:12px 14px;margin:10px 0">
<h4 style="margin:0 0 8px;color:#26215C">🔬 研发资本化率评估</h4>
<p style="font-size:11px;color:#888780;margin-bottom:8px">
  行业基准({rd_result.get("industry","通用")}): <strong>{rd_result.get("industry_norm","")}</strong> | 
  当前: <strong style="color:{color}">{rd_result.get("latest_cap_rate",0)}%</strong> ({risk_labels.get(rd_result.get("risk_level","normal","正常"))})
</p>
<table style="width:100%;font-size:11px;border-collapse:collapse">
<tr style="background:#F1EFE8"><th style="text-align:left;padding:3px 6px">期间</th><th style="text-align:right;padding:3px 6px">研发费用</th><th style="text-align:right;padding:3px 6px">资本化率</th><th style="text-align:left;padding:3px 6px">评估</th></tr>
{period_rows}
</table>
<p style="font-size:10px;color:#888780;margin-top:4px">* 资本化率=资本化金额/(资本化+费用化)。行业基准为制造业/信息技术/环保等行业均值。</p>
</div>'''

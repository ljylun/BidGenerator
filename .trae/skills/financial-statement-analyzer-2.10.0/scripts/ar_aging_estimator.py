#!/usr/bin/env python3
"""应收账款账龄推算器 — 从BS/IS估算账龄分布和坏账风险。

功能: 基于期末应收、营收、周转天数推算账龄结构。
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def estimate_ar_aging(data: Dict[str, Any]) -> Dict[str, Any]:
    """估算应收账款账龄分布。

    基于期末应收余额和当期营收推算:
    - 1年内 = min(当期营收×账期系数, 期末应收)
    - 1-2年 = 超出1年但低于2年营收部分
    - 2年以上 = 剩余

    Args:
        data: 标准化数据 {periods, bs, is}

    Returns:
        账龄分析结果
    """
    periods = data.get("periods", [])
    if not periods:
        return {"error": "无数据", "aging_distribution": {}, "risk_level": "unknown"}

    latest = periods[-1]
    bs = data.get("bs", {}).get(latest, {})
    is_data = data.get("is", {}).get(latest, {})

    ar_balance = bs.get("应收账款", 0)
    revenue = is_data.get("营业收入", 0)

    if ar_balance <= 0:
        return {
            "ar_balance": ar_balance,
            "revenue": revenue,
            "aging_distribution": {},
            "ar_to_revenue_pct": 0,
            "risk_level": "none",
            "findings": ["无应收账款余额"],
        }

    ar_to_rev = ar_balance / revenue if revenue else float("inf")

    # 计算周转天数
    avg_ar = ar_balance  # 简化: 用期末代替平均
    dso = (avg_ar / revenue * 365) if revenue else float("inf")

    # 推算账龄分布(基于DSO的启发式)
    if dso <= 90:
        within_1yr = ar_balance * 0.95
        yr1_2 = ar_balance * 0.05
        over_2yr = 0
    elif dso <= 180:
        within_1yr = ar_balance * 0.70
        yr1_2 = ar_balance * 0.25
        over_2yr = ar_balance * 0.05
    elif dso <= 365:
        within_1yr = ar_balance * 0.50
        yr1_2 = ar_balance * 0.35
        over_2yr = ar_balance * 0.15
    else:
        within_1yr = ar_balance * 0.30
        yr1_2 = ar_balance * 0.40
        over_2yr = ar_balance * 0.30

    # 如果有两年数据,用两年的营收做更精确推算
    if len(periods) >= 2:
        prev = periods[-2]
        prev_rev = data.get("is", {}).get(prev, {}).get("营业收入", 0)
        if prev_rev:
            # 2年以上 = 超出(当期+前期)120%的部分
            combined = (revenue + prev_rev) * 0.6
            over_2yr = max(0, ar_balance - combined)
            yr1_2 = max(0, min(ar_balance - over_2yr, prev_rev * 0.4))
            within_1yr = ar_balance - yr1_2 - over_2yr

    # 风险评估
    findings = []
    risk = "low"

    if ar_to_rev > 0.5:
        risk = "high"
        findings.append(f"应收占营收{ar_to_rev*100:.0f}%,收入质量严重存疑")
    elif ar_to_rev > 0.3:
        risk = "medium"
        findings.append(f"应收占营收{ar_to_rev*100:.0f}%,回款压力较大")

    if dso > 180:
        risk = max(risk, "high") if risk != "low" else "high"
        findings.append(f"周转天数{dso:.0f}天,远超正常水平(60-90天)")
    elif dso > 90:
        risk = max(risk, "medium") if risk != "high" else risk
        findings.append(f"周转天数{dso:.0f}天,超出正常水平")

    if over_2yr > ar_balance * 0.15:
        findings.append(f"估计2年以上账龄{over_2yr/10000:.1f}万({over_2yr/ar_balance*100:.0f}%),坏账风险高")

    # 坏账准备建议
    provision_rate = 0.05 * within_1yr/ar_balance + 0.20 * yr1_2/ar_balance + 0.50 * over_2yr/ar_balance
    suggested_provision = ar_balance * provision_rate

    return {
        "ar_balance": ar_balance,
        "revenue": revenue,
        "ar_to_revenue_pct": round(ar_to_rev * 100, 1),
        "dso_days": round(dso, 0),
        "aging_distribution": {
            "1年以内": {"amount": round(within_1yr, 2), "pct": round(within_1yr/ar_balance*100, 1)},
            "1-2年": {"amount": round(yr1_2, 2), "pct": round(yr1_2/ar_balance*100, 1)},
            "2年以上": {"amount": round(over_2yr, 2), "pct": round(over_2yr/ar_balance*100, 1)},
        },
        "risk_level": risk,
        "suggested_provision_rate": round(provision_rate * 100, 1),
        "suggested_provision_amount": round(suggested_provision, 2),
        "findings": findings,
    }


def render_ar_aging_html(aging: Dict[str, Any]) -> str:
    """渲染账龄分析HTML片段。"""
    if aging.get("error") or not aging.get("ar_balance"):
        return ""

    risk_colors = {"low": "#27ae60", "medium": "#f39c12", "high": "#e74c3c"}
    risk_labels = {"low": "低风险", "medium": "中风险", "high": "高风险"}
    color = risk_colors.get(aging.get("risk_level", "low"), "#888")

    dist = aging.get("aging_distribution", {})
    bars = ""
    bar_colors = {"1年以内": "#27ae60", "1-2年": "#f39c12", "2年以上": "#e74c3c"}
    for label, info in dist.items():
        pct = info.get("pct", 0)
        amt = info.get("amount", 0) / 10000
        bc = bar_colors.get(label, "#888")
        bars += f'''<div style="display:flex;align-items:center;gap:8px;margin:3px 0;font-size:11px">
  <span style="width:50px">{label}</span>
  <div style="flex:1;height:16px;background:#F1EFE8;border-radius:3px;overflow:hidden">
    <div style="height:100%;width:{pct}%;background:{bc};border-radius:3px"></div>
  </div>
  <span style="width:60px;text-align:right">{amt:.1f}万</span>
  <span style="width:35px;text-align:right;color:#888780">{pct}%</span>
</div>'''

    findings_html = "".join([f'<li style="font-size:11px;margin:2px 0">• {f}</li>' for f in aging.get("findings", [])])

    return f'''<div style="background:#FAFAF8;border:1px solid #D3D1C7;border-radius:8px;padding:12px 14px;margin:10px 0">
<h4 style="margin:0 0 8px;color:#26215C">📊 应收账款账龄分析</h4>
<div style="display:flex;gap:16px;margin-bottom:8px;font-size:12px">
  <span>应收余额: <strong>{aging["ar_balance"]/10000:.1f}万</strong></span>
  <span>占营收: <strong>{aging["ar_to_revenue_pct"]}%</strong></span>
  <span>周转天数: <strong style="color:{color}">{aging["dso_days"]:.0f}天</strong></span>
  <span>风险: <strong style="color:{color}">{risk_labels.get(aging.get("risk_level",""),"未知")}</strong></span>
</div>
{bars}
<div style="margin-top:6px;font-size:11px;color:#888780">
  建议坏账准备率: <strong>{aging.get("suggested_provision_rate",0)}%</strong> ≈ <strong>{aging.get("suggested_provision_amount",0)/10000:.1f}万</strong>
</div>
<ul style="margin:6px 0 0 14px;color:#BA7517">{findings_html}</ul>
</div>'''

#!/usr/bin/env python3
"""关联交易自动对账器 — 提取和匹配集团内公司之间的关联科目。

功能: 在多公司数据中自动识别关联交易模式并标记差异。
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 常见的关联科目配对规则
_PAIR_RULES: List[Dict[str, Any]] = [
    # (公司A科目, 公司B科目, 方向, 正常差异容差%)
    {"a_key": "长期股权投资", "b_key": "实收资本", "relation": "A投资B", "tolerance": 0.05},
    {"a_key": "其他应收款", "b_key": "其他应付款", "relation": "A→B往来", "tolerance": 0.10},
    {"a_key": "应收账款", "b_key": "应付账款", "relation": "A→B销售", "tolerance": 0.10},
    {"a_key": "预付款项", "b_key": "预收账款", "relation": "A→B预付", "tolerance": 0.10},
    {"a_key": "应付账款", "b_key": "应收账款", "relation": "A←B采购", "tolerance": 0.10},
]


def match_related_parties(
    companies: Dict[str, Dict[str, Any]],
    relations: Optional[List[Tuple[str, str, str]]] = None,
) -> Dict[str, Any]:
    """自动对账集团内公司的关联科目。

    Args:
        companies: 公司数据字典 {公司名: {bs: {科目:值}, is: {科目:值}}}
        relations: 持股关系 [(母公司, 子公司, "母→子"), ...]

    Returns:
        关联交易匹配结果
    """
    matches = []
    total_matched = 0
    total_mismatch = 0

    # 如果没有指定关系，对所有公司两两配对
    company_names = list(companies.keys())
    pairs = []
    if relations:
        for parent, child, rel_type in relations:
            pairs.append((parent, child, rel_type))
    else:
        for i in range(len(company_names)):
            for j in range(i + 1, len(company_names)):
                pairs.append((company_names[i], company_names[j], "未知关系"))

    for comp_a, comp_b, rel_type in pairs:
        if comp_a not in companies or comp_b not in companies:
            continue

        bs_a = _get_latest_bs(companies[comp_a])
        bs_b = _get_latest_bs(companies[comp_b])

        for rule in _PAIR_RULES:
            val_a = bs_a.get(rule["a_key"], 0)
            val_b = bs_b.get(rule["b_key"], 0)

            if val_a == 0 and val_b == 0:
                continue

            # 关联科目金额通常相近但符号可能相反
            abs_a, abs_b = abs(val_a), abs(val_b)

            if abs_a < 100 or abs_b < 100:
                continue  # 忽略小额

            if abs_a + abs_b == 0:
                continue

            diff = abs(abs_a - abs_b)
            diff_pct = diff / max(abs_a, abs_b) if max(abs_a, abs_b) > 0 else 0
            status = "匹配 ✓" if diff_pct <= rule["tolerance"] else "偏差 ⚠"

            match_item = {
                "company_a": comp_a,
                "company_b": comp_b,
                "account_a": rule["a_key"],
                "account_b": rule["b_key"],
                "value_a": round(val_a, 2),
                "value_b": round(val_b, 2),
                "abs_diff": round(diff, 2),
                "diff_pct": round(diff_pct * 100, 1),
                "relation": rule["relation"],
                "status": status,
                "note": _get_match_note(rule["a_key"], val_a, val_b, diff_pct),
            }
            matches.append(match_item)

            if status == "匹配 ✓":
                total_matched += 1
            else:
                total_mismatch += 1

    # 按差异百分比排序
    matches.sort(key=lambda x: x["diff_pct"], reverse=True)

    return {
        "matches": matches,
        "total_matched": total_matched,
        "total_mismatch": total_mismatch,
        "has_issues": total_mismatch > 0,
        "summary": f"发现 {len(matches)} 组关联科目 ({total_matched} 匹配, {total_mismatch} 偏差)",
    }


def render_related_party_html(result: Dict[str, Any]) -> str:
    """渲染关联交易对账HTML片段。"""
    matches = result.get("matches", [])
    if not matches:
        return ""

    rows = ""
    for m in matches[:12]:  # 最多12行
        a_wan = abs(m["value_a"]) / 10000
        b_wan = abs(m["value_b"]) / 10000
        status_color = "#27ae60" if "匹配" in m["status"] else "#e74c3c"
        rows += f'''<tr>
  <td style="font-size:11px">{m["company_a"][:4]}</td>
  <td style="font-size:11px">{m["account_a"]}</td>
  <td style="font-size:11px">{m["company_b"][:4]}</td>
  <td style="font-size:11px">{m["account_b"]}</td>
  <td style="text-align:right;font-size:11px">{a_wan:.1f}万</td>
  <td style="text-align:right;font-size:11px">{b_wan:.1f}万</td>
  <td style="text-align:right;font-size:11px;color:{status_color}">{m["diff_pct"]}%</td>
  <td style="font-size:11px;color:{status_color}">{m["status"]}</td>
</tr>'''

    return f'''<div style="background:#FAFAF8;border:1px solid #D3D1C7;border-radius:8px;padding:12px 14px;margin:10px 0">
<h4 style="margin:0 0 8px;color:#26215C">🔗 关联交易自动对账</h4>
<p style="font-size:11px;color:#888780;margin-bottom:8px">{result["summary"]}</p>
<table style="width:100%;font-size:11px;border-collapse:collapse">
<tr style="background:#F1EFE8">
  <th style="text-align:left;padding:3px 6px">公司A</th><th style="text-align:left;padding:3px 6px">科目A</th>
  <th style="text-align:left;padding:3px 6px">公司B</th><th style="text-align:left;padding:3px 6px">科目B</th>
  <th style="text-align:right;padding:3px 6px">金额A</th><th style="text-align:right;padding:3px 6px">金额B</th>
  <th style="text-align:right;padding:3px 6px">差异</th><th style="text-align:left;padding:3px 6px">状态</th>
</tr>
{rows}
</table>
<p style="font-size:10px;color:#888780;margin-top:4px">* 正负号对应会计借贷方向,差异>10%标记为偏差。关联交易金额需在合并报表中抵销。</p>
</div>'''


def _get_latest_bs(company_data: Dict[str, Any]) -> Dict[str, float]:
    """获取最新期的BS数据。"""
    periods = company_data.get("periods", [])
    if not periods:
        return {}
    return company_data.get("bs", {}).get(periods[-1], {})


def _get_match_note(account: str, val_a: float, val_b: float, diff_pct: float) -> str:
    """生成关联匹配注释。"""
    if diff_pct <= 0.03:
        return "金额吻合,极可能为关联交易"
    elif diff_pct <= 0.10:
        return "金额接近,可能为关联交易(含时间性差异)"
    elif diff_pct <= 0.30:
        return "金额有差异,可能含非关联部分或其他公司往来"
    else:
        return "金额差异大,需要进一步核实关联关系"


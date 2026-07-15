#!/usr/bin/env python3
"""数据质量评分卡 — 评估分析结果的可靠程度。

功能: 对输入数据的完整性、一致性、充分性打分, 生成星级评分卡。
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


def score_data_quality(data: Dict[str, Any]) -> Dict[str, Any]:
    """评估财务数据的质量和可信度。

    Args:
        data: 标准化数据字典 {periods, bs, is, cf}

    Returns:
        评分卡字典, 含总体分/各维度分/置信度/建议
    """
    periods = data.get("periods", [])
    if not periods:
        return _empty_scorecard()

    latest = periods[-1]
    bs = data.get("bs", {}).get(latest, {})
    is_data = data.get("is", {}).get(latest, {})
    cf = data.get("cf", {}).get(latest, {})

    # ===== 维度1: 报表完整性 (45分) =====
    bs_score, bs_detail = _score_balance_sheet(bs)
    is_score, is_detail = _score_income_statement(is_data)
    cf_score, cf_detail = _score_cash_flow(cf)
    completeness = bs_score + is_score + cf_score

    # ===== 维度2: 期间充分性 (25分) =====
    period_count = len(periods)
    if period_count >= 3:
        period_score, period_detail = 25, f"{period_count}期数据,可计算趋势和M-Score"
    elif period_count >= 2:
        period_score, period_detail = 20, f"{period_count}期数据,可计算增长率但M-Score需≥2期"
    else:
        period_score, period_detail = 8, "仅1期数据,无法计算增长率和趋势,部分信号可能为假阳性"

    # ===== 维度3: BS平衡校验 (20分) =====
    balance_score, balance_detail = _check_bs_balance(bs)

    # ===== 维度4: 数据一致性 (10分) =====
    consistency_score, consistency_detail = _check_consistency(bs, is_data)

    # ===== 综合评分 =====
    total = completeness + period_score + balance_score + consistency_score
    stars = _to_stars(total)
    confidence = _to_confidence(total)
    grade = _to_grade(total)

    return {
        "total_score": total,
        "stars": stars,
        "confidence": confidence,
        "grade": grade,
        "breakdown": {
            "报表完整性": {"score": completeness, "max": 45, "detail": [bs_detail, is_detail, cf_detail]},
            "期间充分性": {"score": period_score, "max": 25, "detail": period_detail},
            "BS平衡": {"score": balance_score, "max": 20, "detail": balance_detail},
            "数据一致性": {"score": consistency_score, "max": 10, "detail": consistency_detail},
        },
        "recommendations": _get_recommendations(total, period_count, cf_score),
    }


def render_quality_card_html(scorecard: Dict[str, Any]) -> str:
    """将评分卡渲染为HTML片段。"""
    stars = scorecard["stars"]
    grade = scorecard["grade"]
    total = scorecard["total_score"]
    conf = scorecard["confidence"]
    recs = scorecard["recommendations"]

    grade_colors = {"A": "#27ae60", "B": "#2e86c1", "C": "#f39c12", "D": "#e74c3c", "F": "#c0392b"}
    color = grade_colors.get(grade, "#888")

    html = f'''<div class="quality-card" style="background:#FAFAF8;border:1px solid #D3D1C7;border-radius:8px;padding:14px 16px;margin:12px 0;font-size:13px">
<h3 style="margin:0 0 8px;color:#26215C;font-size:14px">📋 数据质量评分卡</h3>
<div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">
  <div style="font-size:28px;font-weight:700;color:{color}">{grade}级</div>
  <div style="font-size:20px;color:#888780">{stars}</div>
  <div style="flex:1;text-align:right;font-size:12px;color:#888780">综合评分: {total}/100 | 置信度: {conf}</div>
</div>
<table style="width:100%;font-size:11px;border-collapse:collapse">
<tr><th style="text-align:left;padding:3px 6px;background:#F1EFE8">维度</th><th style="text-align:right;padding:3px 6px;background:#F1EFE8">得分</th><th style="text-align:left;padding:3px 6px;background:#F1EFE8">说明</th></tr>'''

    for dim, info in scorecard["breakdown"].items():
        detail = info["detail"]
        if isinstance(detail, list):
            detail_str = "; ".join([d for d in detail if d])
        else:
            detail_str = str(detail)
        html += f'<tr><td style="padding:3px 6px">{dim}</td><td style="text-align:right;padding:3px 6px">{info["score"]}/{info["max"]}</td><td style="padding:3px 6px;font-size:11px;color:#888780">{detail_str}</td></tr>'

    html += '</table>'
    if recs:
        html += f'<div style="margin-top:8px;font-size:11px;color:#BA7517">⚠️ 建议: {"; ".join(recs[:3])}</div>'
    html += '</div>'
    return html


# ===== 内部函数 =====

def _score_balance_sheet(bs: Dict[str, float]) -> Tuple[int, str]:
    required = ["货币资金", "应收账款", "存货", "资产总计", "负债合计", "所有者权益合计"]
    found = sum(1 for k in required if k in bs and bs[k] is not None)
    if found == len(required):
        return 15, "BS完整 ✓"
    elif found >= 4:
        return 10, f"BS缺{len(required)-found}项"
    return 5, "BS严重缺失"


def _score_income_statement(is_data: Dict[str, float]) -> Tuple[int, str]:
    required = ["营业收入", "营业成本", "净利润"]
    found = sum(1 for k in required if k in is_data)
    if found == len(required):
        extras = sum(1 for k in ["管理费用", "销售费用", "研发费用", "财务费用"] if k in is_data)
        return 15, f"IS完整 ✓ (含{extras}/4项费用明细)"
    elif found >= 2:
        return 10, "IS基本完整"
    return 5, "IS严重缺失"


def _score_cash_flow(cf: Dict[str, float]) -> Tuple[int, str]:
    if not cf or all(v == 0 for v in cf.values()):
        return 3, "CF缺失 ✗ (建议补充)"
    has_oper = any("经营" in k for k in cf)
    return 15 if has_oper else 8, "CF完整 ✓" if has_oper else "CF部分(缺经营CF)"


def _check_bs_balance(bs: Dict[str, float]) -> Tuple[int, str]:
    ta = bs.get("资产总计") or bs.get("总资产") or 0
    tl = bs.get("负债合计") or bs.get("总负债") or bs.get("负债总计") or 0
    eq = bs.get("所有者权益合计") or bs.get("所有者权益") or bs.get("所有者权益总计") or 0
    if ta == 0 or (tl + eq) == 0:
        return 5, "无法校验BS平衡"
    diff = abs(ta - (tl + eq))
    pct = diff / ta if ta else 0
    if pct < 0.001:
        return 20, f"BS平衡 ✓ (偏差{pct*100:.4f}%)"
    elif pct < 0.01:
        return 15, f"BS轻微偏差 (偏差{pct*100:.2f}%)"
    else:
        return 8, f"BS不平 ⚠ (偏差{pct*100:.2f}%)"


def _check_consistency(bs: Dict, is_data: Dict) -> Tuple[int, str]:
    issues = []
    # 营收 vs 应收: 若营收>0但应收为0可能有异常
    rev = is_data.get("营业收入", 0)
    ar = bs.get("应收账款", 0)
    if rev > 1000000 and ar == 0:
        issues.append("高营收零应收")
    # 净利 vs 未分配利润变动
    ni = is_data.get("净利润", 0)
    re = bs.get("未分配利润", 0)
    if ni > 0 and re < 0:
        issues.append("盈利但未分配利润为负")

    if not issues:
        return 10, "一致性检查通过 ✓"
    return 6, "; ".join(issues)


def _to_stars(score: int) -> str:
    if score >= 90: return "★★★★★"
    elif score >= 75: return "★★★★☆"
    elif score >= 60: return "★★★☆☆"
    elif score >= 45: return "★★☆☆☆"
    else: return "★☆☆☆☆"


def _to_confidence(score: int) -> str:
    if score >= 80: return "高"
    elif score >= 60: return "中"
    else: return "低"


def _to_grade(score: int) -> str:
    if score >= 90: return "A"
    elif score >= 75: return "B"
    elif score >= 60: return "C"
    elif score >= 45: return "D"
    else: return "F"


def _get_recommendations(total: int, periods: int, cf_score: int) -> List[str]:
    recs = []
    if periods < 2:
        recs.append("补充至少2期数据以启用增长分析和M-Score")
    if cf_score < 10:
        recs.append("补充现金流量表以评估利润质量")
    if total < 60:
        recs.append("当前数据置信度较低,分析结论需谨慎使用")
    return recs


def _empty_scorecard() -> Dict[str, Any]:
    return {
        "total_score": 0,
        "stars": "☆☆☆☆☆",
        "confidence": "无数据",
        "grade": "F",
        "breakdown": {},
        "recommendations": ["无法评估: 数据为空"],
    }

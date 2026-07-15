#!/usr/bin/env python3
"""多期数据自动拼接器 — 消除单期假阳性。

功能: 检测同一公司多年数据,自动拼接为多期序列,使增长/变化类信号生效。
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def merge_multi_period(
    datasets: List[Dict[str, Any]],
    company_name: str = "",
) -> Dict[str, Any]:
    """将多个单期数据合并为多期序列。

    Args:
        datasets: 每期数据的列表, 每个是 {periods:["2024"], bs:{}, is:{}, cf:{}} 格式
        company_name: 公司名称

    Returns:
        合并后的多期数据字典, periods按年份升序排列
    """
    if len(datasets) <= 1:
        logger.info("Only %d dataset(s), no merge needed", len(datasets))
        return datasets[0] if datasets else {"periods": [], "bs": {}, "is": {}, "cf": {}}

    # 提取所有期间
    all_periods: List[str] = []
    for ds in datasets:
        all_periods.extend(ds.get("periods", []))

    # 去重排序
    all_periods = sorted(set(all_periods))

    merged_bs: Dict[str, Dict[str, float]] = {}
    merged_is: Dict[str, Dict[str, float]] = {}
    merged_cf: Dict[str, Dict[str, float]] = {}

    for ds in datasets:
        for period in ds.get("periods", []):
            merged_bs[period] = ds.get("bs", {}).get(period, {})
            merged_is[period] = ds.get("is", {}).get(period, {})
            merged_cf[period] = ds.get("cf", {}).get(period, {})

    # 数据质量评估
    completeness = _assess_completeness(all_periods, merged_bs, merged_is, merged_cf)

    logger.info(
        "Merged %d datasets into %d periods for '%s' (completeness: %.0f%%)",
        len(datasets), len(all_periods), company_name, completeness * 100,
    )

    return {
        "periods": all_periods,
        "bs": merged_bs,
        "is": merged_is,
        "cf": merged_cf,
        "merge_meta": {
            "source_count": len(datasets),
            "period_count": len(all_periods),
            "completeness": round(completeness, 2),
            "has_cf": any(v for v in merged_cf.values()),
            "has_multi_period": len(all_periods) >= 2,
        },
    }


def detect_single_period_issues(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """检测单期数据导致的分析局限性。

    Args:
        data: 标准化数据字典

    Returns:
        局限性报告
    """
    periods = data.get("periods", [])
    single_period = len(periods) <= 1
    has_cf = False
    if periods:
        cf_period = data.get("cf", {}).get(periods[-1], {})
        has_cf = any(v for k, v in cf_period.items() if k.strip() and v != 0)

    issues = []
    impact_score = 0  # 0-100, 越高越严重

    if single_period:
        issues.append({
            "issue": "单期数据",
            "detail": "仅1期数据,无法计算增长率/趋势/M-Score。增长类和变化类红Flag信号可能为假阳性。",
            "impact": "high",
            "mitigation": "补充多年数据或使用多期拼接器",
        })
        impact_score += 40

    if not has_cf:
        issues.append({
            "issue": "缺现金流量表",
            "detail": "无法评估利润的现金转化质量。F-Score中CFO相关指标全部为FAIL。现金流模式画像不可用。",
            "impact": "high",
            "mitigation": "补充现金流量表或使用间接法推算",
        })
        impact_score += 30

    if single_period and not has_cf:
        confidence = "low"
    elif single_period or not has_cf:
        confidence = "medium"
    else:
        confidence = "high"

    return {
        "issues": issues,
        "impact_score": min(impact_score, 100),
        "confidence": confidence,
        "recommendation": _get_recommendation(confidence, issues),
    }


def _assess_completeness(
    periods: List[str],
    bs: Dict[str, Dict],
    is_data: Dict[str, Dict],
    cf: Dict[str, Dict],
) -> float:
    """评估数据完整性。"""
    if not periods:
        return 0.0
    bs_ok = sum(1 for p in periods if bs.get(p)) / len(periods)
    is_ok = sum(1 for p in periods if is_data.get(p)) / len(periods)
    cf_ok = sum(1 for p in periods if cf.get(p)) / len(periods)
    return (bs_ok * 0.4 + is_ok * 0.4 + cf_ok * 0.2)


def _get_recommendation(confidence: str, issues: List[Dict]) -> str:
    """根据置信度生成建议。"""
    if confidence == "high":
        return "数据充分,分析结果可信度高。"
    elif confidence == "medium":
        missing = [i["issue"] for i in issues]
        return f"数据部分缺失({', '.join(missing)}),分析结果需谨慎解读。建议补充缺失数据以获得完整分析。"
    else:
        return "数据严重不足,分析结果仅供参考。强烈建议补充多年数据+现金流量表。"

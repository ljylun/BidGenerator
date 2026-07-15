#!/usr/bin/env python3
"""M-Score / F-Score 造假量化检测模块。

Beneish M-Score (8变量版) + Piotroski F-Score (9分制)。

作者: 优方皑尔 Uform Ai
版本: v1.0.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# M-Score 系数（Beneish 1999, 8变量模型）
_BENEISH_COEFFICIENTS: Dict[str, float] = {
    "DSRI": 0.920,
    "GMI": 0.528,
    "AQI": 0.404,
    "SGI": 0.892,
    "DEPI": 0.115,
    "SGAI": -0.172,
    "TATA": 4.679,
    "LVGI": -0.327,
}
_BENEISH_INTERCEPT: float = -4.84
_MSCORE_SUSPICION_THRESHOLD: float = -1.78
_MSCORE_HIGH_RISK_THRESHOLD: float = -2.22


def compute_mscore(data: Dict[str, Any]) -> Dict[str, Any]:
    """计算 Beneish M-Score（8变量简化版）。

    公式:
        M = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI
            + 0.892*SGI + 0.115*DEPI - 0.172*SGAI
            + 4.679*TATA - 0.327*LVGI

    判定:
        > -1.78 → 造假嫌疑
        > -2.22 → 造假高风险
        ≤ -2.22 → 正常范围

    Args:
        data: 标准化财务数据:
            {
                "periods": ["2023", "2024"],
                "bs": {period: {科目: 数值}},
                "is": {period: {科目: 数值}},
                "cf": {period: {科目: 数值}},
            }

    Returns:
        dict: 各期间的M-Score详细结果。
    """
    results: Dict[str, Any] = {}
    periods: List[str] = sorted(data.get("periods", []))

    for i, period in enumerate(periods):
        if i == 0:
            results[period] = {
                "value": None,
                "verdict": "无上年数据，无法计算",
                "variables": {},
                "error": "insufficient_data",
            }
            continue

        curr_bs: Dict[str, float] = data["bs"].get(period, {})
        prev_bs: Dict[str, float] = data["bs"].get(periods[i - 1], {})
        curr_is: Dict[str, float] = data["is"].get(period, {})
        prev_is: Dict[str, float] = data["is"].get(periods[i - 1], {})
        curr_cf: Dict[str, float] = data["cf"].get(period, {})
        prev_cf: Dict[str, float] = data["cf"].get(periods[i - 1], {})

        try:
            variables: Dict[str, float] = _compute_mscore_variables(
                curr_bs, prev_bs, curr_is, prev_is, curr_cf, prev_cf
            )
            mscore: float = _calculate_mscore(variables)

            if mscore > _MSCORE_SUSPICION_THRESHOLD:
                verdict: str = "造假嫌疑"
            elif mscore > _MSCORE_HIGH_RISK_THRESHOLD:
                verdict = "造假高风险"
            else:
                verdict = "正常范围"

            results[period] = {
                "value": round(mscore, 3),
                "verdict": verdict,
                "variables": variables,
            }
        except (ZeroDivisionError, KeyError) as exc:
            logger.warning("M-Score计算失败 for %s: %s", period, exc)
            results[period] = {
                "value": None,
                "verdict": "数据不足，无法计算",
                "variables": {},
                "error": str(exc),
            }

    return results


def _compute_mscore_variables(
    curr_bs: Dict[str, float],
    prev_bs: Dict[str, float],
    curr_is: Dict[str, float],
    prev_is: Dict[str, float],
    curr_cf: Dict[str, float],
    prev_cf: Dict[str, float],
) -> Dict[str, float]:
    """计算M-Score 8个变量。

    Args:
        curr_bs: 当期资产负债表。
        prev_bs: 上期资产负债表。
        curr_is: 当期利润表。
        prev_is: 上期利润表。
        curr_cf: 当期现金流量表。
        prev_cf: 上期现金流量表。

    Returns:
        dict: 8个变量值。
    """
    # 提取基础数据
    curr_receivables: float = curr_bs.get("应收账款", 0)
    prev_receivables: float = prev_bs.get("应收账款", 0)
    curr_revenue: float = curr_is.get("营业收入", 0)
    prev_revenue: float = prev_is.get("营业收入", 0)
    curr_cogs: float = curr_is.get("营业成本", 0)
    prev_cogs: float = prev_is.get("营业成本", 0)
    curr_total_assets: float = curr_bs.get("总资产", curr_bs.get("资产总计", 1))
    prev_total_assets: float = prev_bs.get("总资产", prev_bs.get("资产总计", 1))
    curr_current_assets: float = curr_bs.get("流动资产", 0)
    prev_current_assets: float = prev_bs.get("流动资产", 0)
    curr_fixed_assets: float = curr_bs.get("固定资产净额", curr_bs.get("固定资产", 0))
    prev_fixed_assets: float = prev_bs.get("固定资产净额", prev_bs.get("固定资产", 0))
    curr_accum_dep: float = curr_bs.get("累计折旧", 0)
    prev_accum_dep: float = prev_bs.get("累计折旧", 0)
    curr_fixed_original: float = curr_bs.get("固定资产原值", curr_fixed_assets + curr_accum_dep)
    prev_fixed_original: float = prev_bs.get("固定资产原值", prev_fixed_assets + prev_accum_dep)
    curr_sg_a: float = curr_is.get("销售费用", 0) + curr_is.get("管理费用", 0)
    prev_sg_a: float = prev_is.get("销售费用", 0) + prev_is.get("管理费用", 0)
    curr_net_income: float = curr_is.get("净利润", 0)
    curr_operating_cf: float = curr_cf.get("经营活动产生的现金流量净额",
                                           curr_cf.get("经营CFO", 0))
    curr_total_liab: float = curr_bs.get("总负债", curr_bs.get("负债总计", 0))
    prev_total_liab: float = prev_bs.get("总负债", prev_bs.get("负债总计", 0))

    # DSRI: 应收账款指数
    dsri: float = _safe_divide(
        curr_receivables / curr_revenue, prev_receivables / prev_revenue
    )

    # GMI: 毛利率指数
    curr_gm: float = (curr_revenue - curr_cogs) / curr_revenue if curr_revenue else 0
    prev_gm: float = (prev_revenue - prev_cogs) / prev_revenue if prev_revenue else 0
    gmi: float = _safe_divide(prev_gm, curr_gm)

    # AQI: 资产质量指数
    curr_non_ca_fa: float = curr_total_assets - curr_current_assets - curr_fixed_assets
    prev_non_ca_fa: float = prev_total_assets - prev_current_assets - prev_fixed_assets
    aqi: float = _safe_divide(
        curr_non_ca_fa / curr_total_assets,
        prev_non_ca_fa / prev_total_assets,
    )

    # SGI: 收入增长指数
    sgi: float = _safe_divide(curr_revenue, prev_revenue)

    # DEPI: 折旧率指数
    curr_dep_rate: float = (
        curr_accum_dep / curr_fixed_original if curr_fixed_original else 0
    )
    prev_dep_rate: float = (
        prev_accum_dep / prev_fixed_original if prev_fixed_original else 0
    )
    depi: float = _safe_divide(prev_dep_rate, curr_dep_rate)

    # SGAI: 销售及管理费用指数
    sgai: float = _safe_divide(
        curr_sg_a / curr_revenue,
        prev_sg_a / prev_revenue,
    )

    # TATA: 应计/总资产
    tata: float = (curr_net_income - curr_operating_cf) / curr_total_assets

    # LVGI: 杠杆指数
    lvgi: float = _safe_divide(
        curr_total_liab / curr_total_assets,
        prev_total_liab / prev_total_assets,
    )

    return {
        "DSRI": round(dsri, 4),
        "GMI": round(gmi, 4),
        "AQI": round(aqi, 4),
        "SGI": round(sgi, 4),
        "DEPI": round(depi, 4),
        "SGAI": round(sgai, 4),
        "TATA": round(tata, 4),
        "LVGI": round(lvgi, 4),
    }


def _calculate_mscore(variables: Dict[str, float]) -> float:
    """计算M-Score值。

    Args:
        variables: 8个M-Score变量。

    Returns:
        float: M-Score值。
    """
    return round(
        _BENEISH_INTERCEPT
        + sum(
            _BENEISH_COEFFICIENTS[var] * variables[var]
            for var in _BENEISH_COEFFICIENTS
        ),
        3,
    )


def _safe_divide(numerator: float, denominator: float) -> float:
    """安全除法，分母为0时返回1.0（代表无变化）。

    Args:
        numerator: 分子。
        denominator: 分母。

    Returns:
        float: 比值。
    """
    if denominator == 0:
        return 1.0
    return numerator / denominator


def compute_fscore(data: Dict[str, Any]) -> Dict[str, Any]:
    """计算 Piotroski F-Score（0-9分）。

    维度:
        盈利能力 (4分): ROA>0, CFO>0, ΔROA>0, CFO>净利
        杠杆 (3分): Δ长期负债率<0, Δ流动率>0, 无股权稀释
        效率 (2分): Δ毛利率>0, Δ周转率>0

    判定: F-Score ≤ 3 → 高风险财务困境企业。

    Args:
        data: 标准化财务数据。

    Returns:
        dict: 各期间的F-Score详细结果。
    """
    results: Dict[str, Any] = {}
    periods: List[str] = sorted(data.get("periods", []))

    for i, period in enumerate(periods):
        bs: Dict[str, float] = data["bs"].get(period, {})
        iso: Dict[str, float] = data["is"].get(period, {})
        cf: Dict[str, float] = data["cf"].get(period, {})

        profit_score: int = 0
        leverage_score: int = 0
        efficiency_score: int = 0
        details: List[Dict[str, Any]] = []

        # --- 盈利能力 (4分) ---
        total_assets: float = bs.get("总资产", bs.get("资产总计", 1))
        net_income: float = iso.get("净利润", 0)
        operating_cf: float = cf.get("经营活动产生的现金流量净额",
                                      cf.get("经营CFO", 0))

        # 1) ROA > 0
        roa: float = net_income / total_assets if total_assets else 0
        if roa > 0:
            profit_score += 1
            details.append({"criterion": "ROA>0", "value": round(roa, 4), "passed": True})
        else:
            details.append({"criterion": "ROA>0", "value": round(roa, 4), "passed": False})

        # 2) CFO > 0
        if operating_cf > 0:
            profit_score += 1
            details.append({"criterion": "CFO>0", "value": round(operating_cf, 0), "passed": True})
        else:
            details.append({"criterion": "CFO>0", "value": round(operating_cf, 0), "passed": False})

        # 3) ΔROA > 0
        delta_roa: bool = False
        if i > 0:
            prev_bs2: Dict[str, float] = data["bs"].get(periods[i - 1], {})
            prev_ta: float = prev_bs2.get("总资产", prev_bs2.get("资产总计", 1))
            prev_is2: Dict[str, float] = data["is"].get(periods[i - 1], {})
            prev_ni: float = prev_is2.get("净利润", 0)
            prev_roa: float = prev_ni / prev_ta if prev_ta else 0
            if roa > prev_roa:
                profit_score += 1
                delta_roa = True
        details.append({"criterion": "ΔROA>0", "value": "N/A" if i == 0 else round(roa - prev_roa, 4), "passed": delta_roa})

        # 4) CFO > 净利
        if operating_cf > net_income:
            profit_score += 1
            details.append({"criterion": "CFO>净利", "value": f"{operating_cf:.0f} vs {net_income:.0f}", "passed": True})
        else:
            details.append({"criterion": "CFO>净利", "value": f"{operating_cf:.0f} vs {net_income:.0f}", "passed": False})

        # --- 杠杆 (3分) ---
        total_liab: float = bs.get("总负债", bs.get("负债总计", 0))
        current_assets: float = bs.get("流动资产", 0)
        current_liab: float = bs.get("流动负债", 0)
        long_debt: float = bs.get("长期借款", 0) + bs.get("应付债券", 0)
        equity: float = bs.get("所有者权益", bs.get("所有者权益总计", 0))

        # 5) Δ长期负债率 < 0
        delta_leverage: bool = False
        curr_ltd_ratio: float = long_debt / total_assets if total_assets else 0
        if i > 0:
            prev_bs3: Dict[str, float] = data["bs"].get(periods[i - 1], {})
            prev_ta2: float = prev_bs3.get("总资产", prev_bs3.get("资产总计", 1))
            prev_ld: float = prev_bs3.get("长期借款", 0) + prev_bs3.get("应付债券", 0)
            prev_ltd_ratio: float = prev_ld / prev_ta2 if prev_ta2 else 0
            if curr_ltd_ratio < prev_ltd_ratio:
                leverage_score += 1
                delta_leverage = True
        details.append({"criterion": "Δ长期负债率<0", "value": round(curr_ltd_ratio, 4), "passed": delta_leverage})

        # 6) Δ流动率 > 0
        curr_ratio: float = current_assets / current_liab if current_liab else 0
        delta_current: bool = False
        if i > 0:
            prev_bs4: Dict[str, float] = data["bs"].get(periods[i - 1], {})
            prev_ca: float = prev_bs4.get("流动资产", 0)
            prev_cl: float = prev_bs4.get("流动负债", 0)
            prev_cr: float = prev_ca / prev_cl if prev_cl else 0
            if curr_ratio > prev_cr:
                leverage_score += 1
                delta_current = True
        details.append({"criterion": "Δ流动率>0", "value": round(curr_ratio, 4), "passed": delta_current})

        # 7) 无股权稀释（简化：实收资本不增加）
        no_dilution: bool = True
        if i > 0:
            prev_bs5: Dict[str, float] = data["bs"].get(periods[i - 1], {})
            prev_capital: float = prev_bs5.get("实收资本", prev_bs5.get("股本", 0))
            curr_capital: float = bs.get("实收资本", bs.get("股本", 0))
            if curr_capital <= prev_capital:
                leverage_score += 1
                no_dilution = True
            else:
                no_dilution = False
        else:
            leverage_score += 1
        details.append({"criterion": "无股权稀释", "value": "", "passed": no_dilution})

        # --- 效率 (2分) ---
        # 8) Δ毛利率 > 0
        revenue: float = iso.get("营业收入", 0)
        cogs: float = iso.get("营业成本", 0)
        curr_gm: float = (revenue - cogs) / revenue if revenue else 0
        delta_gm: bool = False
        if i > 0:
            prev_is6: Dict[str, float] = data["is"].get(periods[i - 1], {})
            prev_rev: float = prev_is6.get("营业收入", 0)
            prev_cogs2: float = prev_is6.get("营业成本", 0)
            prev_gm: float = (prev_rev - prev_cogs2) / prev_rev if prev_rev else 0
            if curr_gm > prev_gm:
                efficiency_score += 1
                delta_gm = True
        details.append({"criterion": "Δ毛利率>0", "value": round(curr_gm, 4), "passed": delta_gm})

        # 9) Δ资产周转率 > 0
        curr_turnover: float = revenue / total_assets if total_assets else 0
        delta_turnover: bool = False
        if i > 0:
            prev_bs7: Dict[str, float] = data["bs"].get(periods[i - 1], {})
            prev_ta3: float = prev_bs7.get("总资产", prev_bs7.get("资产总计", 1))
            prev_is7: Dict[str, float] = data["is"].get(periods[i - 1], {})
            prev_rev2: float = prev_is7.get("营业收入", 0)
            prev_turnover: float = prev_rev2 / prev_ta3 if prev_ta3 else 0
            if curr_turnover > prev_turnover:
                efficiency_score += 1
                delta_turnover = True
        details.append({"criterion": "Δ周转率>0", "value": round(curr_turnover, 4), "passed": delta_turnover})

        total_score: int = profit_score + leverage_score + efficiency_score

        if total_score <= 3:
            fscore_verdict: str = "高风险财务困境"
        elif total_score <= 5:
            fscore_verdict = "中等风险"
        else:
            fscore_verdict = "财务健康"

        results[period] = {
            "total": total_score,
            "profitability": profit_score,
            "leverage": leverage_score,
            "efficiency": efficiency_score,
            "verdict": fscore_verdict,
            "details": details,
        }

    return results

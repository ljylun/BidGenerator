#!/usr/bin/env python3
"""财务比率计算引擎 — 五维度40+指标实时计算。

所有指标均通过Python函数实时计算，遵循"公式优先"原则，绝不硬编码数值。

作者: 优方皑尔 Uform Ai
版本: v1.0.0
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def compute_all_ratios(data: Dict[str, Any]) -> Dict[str, Any]:
    """计算全部五维度40+财务比率。

    Args:
        data: 标准化财务数据结构:
            {
                "periods": ["2023", "2024", "2025"],
                "bs": {period: {科目: 数值}},
                "is": {period: {科目: 数值}},
                "cf": {period: {科目: 数值}},
            }

    Returns:
        dict: 包含所有比率结果的字典。
    """
    results: Dict[str, Any] = {
        "偿债能力": _compute_solvency_ratios(data),
        "营运能力": _compute_operating_ratios(data),
        "盈利能力": _compute_profitability_ratios(data),
        "现金流质量": _compute_cashflow_ratios(data),
        "成长能力": _compute_growth_ratios(data),
    }
    return results


# =============================================================================
# 偿债能力 (8指标)
# =============================================================================


def _compute_solvency_ratios(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """计算偿债能力指标。"""
    ratios: List[Dict[str, Any]] = []
    for period in data.get("periods", []):
        bs: Dict[str, float] = data["bs"].get(period, {})
        iso: Dict[str, float] = data["is"].get(period, {})
        cf: Dict[str, float] = data["cf"].get(period, {})

        total_assets: float = bs.get("总资产", bs.get("资产总计", 0))
        current_assets: float = bs.get("流动资产", bs.get("流动资产合计", 0))
        current_liab: float = bs.get("流动负债", bs.get("流动负债合计", 0))
        total_liab: float = bs.get("总负债", bs.get("负债总计", bs.get("负债合计", 0)))
        cash: float = bs.get("货币资金", 0)
        inventory: float = bs.get("存货", 0)
        equity: float = bs.get("所有者权益", bs.get("所有者权益总计", bs.get("所有者权益合计", 0)))
        ebit: float = iso.get("营业利润", 0)
        interest_expense: float = abs(iso.get("财务费用", iso.get("利息费用", 0)))

        # 流动比率
        current_ratio: float = (
            current_assets / current_liab if current_liab != 0 else float("inf")
        )

        # 速动比率
        quick_ratio: float = (
            (current_assets - inventory) / current_liab
            if current_liab != 0
            else float("inf")
        )

        # 现金比率
        cash_ratio: float = cash / current_liab if current_liab != 0 else float("inf")

        # 资产负债率
        debt_to_asset: float = total_liab / total_assets if total_assets != 0 else 0

        # 权益乘数
        equity_multiplier: float = total_assets / equity if equity != 0 else float("inf")

        # EBITDA利息覆盖
        depreciation: float = _estimate_depreciation(bs, iso)
        ebitda: float = ebit + depreciation
        ebitda_interest_coverage: float = (
            ebitda / interest_expense if interest_expense != 0 else float("inf")
        )

        # 有息负债率
        interest_bearing_debt: float = _estimate_interest_bearing_debt(bs)
        interest_debt_ratio: float = (
            interest_bearing_debt / total_assets if total_assets != 0 else 0
        )

        # 短债占比
        short_debt_ratio: float = (
            current_liab / total_liab if total_liab != 0 else 0
        )

        ratios.append({
            "period": period,
            "流动比率": round(current_ratio, 3),
            "速动比率": round(quick_ratio, 3),
            "现金比率": round(cash_ratio, 3),
            "资产负债率": round(debt_to_asset, 3),
            "权益乘数": round(equity_multiplier, 3),
            "EBITDA利息覆盖倍数": round(ebitda_interest_coverage, 2),
            "有息负债率": round(interest_debt_ratio, 3),
            "短债占比": round(short_debt_ratio, 3),
        })
    return ratios


# =============================================================================
# 营运能力 (7指标)
# =============================================================================


def _compute_operating_ratios(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """计算营运能力指标。"""
    ratios: List[Dict[str, Any]] = []
    periods: List[str] = data.get("periods", [])

    for i, period in enumerate(periods):
        bs: Dict[str, float] = data["bs"].get(period, {})
        iso: Dict[str, float] = data["is"].get(period, {})

        revenue: float = iso.get("营业收入", 0)
        cost: float = iso.get("营业成本", 0)
        receivables: float = bs.get("应收账款", 0)
        inventory: float = bs.get("存货", 0)
        payables: float = bs.get("应付账款", 0)
        total_assets: float = bs.get("总资产", bs.get("资产总计", 0))
        current_assets: float = bs.get("流动资产", bs.get("流动资产合计", 0))
        fixed_assets: float = bs.get("固定资产净额", bs.get("固定资产", 0))

        # 应收周转天数 (DSO)
        dso: float = (
            receivables / revenue * 365 if revenue != 0 else float("inf")
        )

        # 存货周转天数 (DIO)
        dio: float = (
            inventory / cost * 365 if cost != 0 else float("inf")
        )

        # 应付周转天数 (DPO)
        dpo: float = (
            payables / cost * 365 if cost != 0 else float("inf")
        )

        # 现金转化周期 (CCC)
        ccc: float = dso + dio - dpo

        # 总资产周转率
        asset_turnover: float = revenue / total_assets if total_assets != 0 else 0

        # 流动资产周转率
        current_asset_turnover: float = (
            revenue / current_assets if current_assets != 0 else 0
        )

        # 固定资产周转率
        fixed_asset_turnover: float = (
            revenue / fixed_assets if fixed_assets != 0 else 0
        )

        ratios.append({
            "period": period,
            "应收周转天数(DSO)": round(dso, 1),
            "存货周转天数(DIO)": round(dio, 1),
            "应付周转天数(DPO)": round(dpo, 1),
            "现金转化周期(CCC)": round(ccc, 1),
            "总资产周转率": round(asset_turnover, 3),
            "流动资产周转率": round(current_asset_turnover, 3),
            "固定资产周转率": round(fixed_asset_turnover, 3),
        })
    return ratios


# =============================================================================
# 盈利能力 (7指标)
# =============================================================================


def _compute_profitability_ratios(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """计算盈利能力指标。"""
    ratios: List[Dict[str, Any]] = []
    for period in data.get("periods", []):
        bs: Dict[str, float] = data["bs"].get(period, {})
        iso: Dict[str, float] = data["is"].get(period, {})

        revenue: float = iso.get("营业收入", 0)
        cost: float = iso.get("营业成本", 0)
        net_profit: float = iso.get("净利润", 0)
        gross_profit: float = revenue - cost
        total_assets: float = bs.get("总资产", bs.get("资产总计", 0))
        equity: float = bs.get("所有者权益", bs.get("所有者权益总计", bs.get("所有者权益合计", 0)))
        ebit: float = iso.get("营业利润", 0)
        recurring_net: float = iso.get("扣非净利润", net_profit)

        # 毛利率
        gross_margin: float = gross_profit / revenue if revenue != 0 else 0

        # 净利率
        net_margin: float = net_profit / revenue if revenue != 0 else 0

        # 扣非净利率
        recurring_margin: float = recurring_net / revenue if revenue != 0 else 0

        # EBIT利润率
        ebit_margin: float = ebit / revenue if revenue != 0 else 0

        # ROA
        avg_assets: float = _get_average(data, "总资产", period)
        roa: float = net_profit / avg_assets if avg_assets != 0 else 0

        # ROE
        avg_equity: float = _get_average(data, "所有者权益", period)
        roe: float = net_profit / avg_equity if avg_equity != 0 else 0

        # 扣非/净利比
        recurring_ratio: float = recurring_net / net_profit if net_profit != 0 else 1

        ratios.append({
            "period": period,
            "毛利率": round(gross_margin, 4),
            "净利率": round(net_margin, 4),
            "扣非净利率": round(recurring_margin, 4),
            "EBIT利润率": round(ebit_margin, 4),
            "ROA": round(roa, 4),
            "ROE": round(roe, 4),
            "扣非净利/净利": round(recurring_ratio, 4),
        })
    return ratios


# =============================================================================
# 现金流质量 (6指标)
# =============================================================================


def _compute_cashflow_ratios(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """计算现金流质量指标。"""
    ratios: List[Dict[str, Any]] = []
    for period in data.get("periods", []):
        iso: Dict[str, float] = data["is"].get(period, {})
        cf: Dict[str, float] = data["cf"].get(period, {})

        revenue: float = iso.get("营业收入", 0)
        net_profit: float = iso.get("净利润", 0)
        operating_cf: float = cf.get("经营活动产生的现金流量净额",
                                      cf.get("经营CFO", 0))
        investing_cf: float = cf.get("投资活动产生的现金流量净额",
                                      cf.get("投资CFI", 0))
        capex: float = abs(cf.get("购建固定资产无形资产支付的现金",
                                  cf.get("CAPEX", 0)))
        cash_receipts: float = cf.get("销售商品提供劳务收到的现金", 0)

        # 销售收现比
        sales_cash_ratio: float = cash_receipts / revenue if revenue != 0 else 0

        # 经营CF/净利
        cfo_to_net: float = (
            operating_cf / net_profit if net_profit != 0 else
            (float("inf") if operating_cf > 0 else float("-inf"))
        )

        # 自由现金流
        fcf: float = operating_cf - capex

        # FCF/净利
        fcf_to_net: float = fcf / net_profit if net_profit != 0 else 0

        # FCF/营收
        fcf_margin: float = fcf / revenue if revenue != 0 else 0

        # CAPEX/折旧摊销
        depreciation: float = _estimate_depreciation(
            data.get("bs", {}).get(period, {}), iso
        )
        capex_to_dep: float = capex / depreciation if depreciation != 0 else float("inf")

        ratios.append({
            "period": period,
            "销售收现比": round(sales_cash_ratio, 4),
            "经营CF/净利": round(cfo_to_net, 3),
            "自由现金流(FCF)": round(fcf, 1),
            "FCF/净利": round(fcf_to_net, 3),
            "FCF利润率": round(fcf_margin, 4),
            "CAPEX/折旧摊销": round(capex_to_dep, 2),
        })
    return ratios


# =============================================================================
# 成长能力 (5指标)
# =============================================================================


def _compute_growth_ratios(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """计算成长能力指标。"""
    ratios: List[Dict[str, Any]] = []
    periods: List[str] = data.get("periods", [])

    for i, period in enumerate(periods):
        iso: Dict[str, float] = data["is"].get(period, {})
        bs: Dict[str, float] = data["bs"].get(period, {})

        revenue: float = iso.get("营业收入", 0)
        net_profit: float = iso.get("净利润", 0)
        total_assets: float = bs.get("总资产", bs.get("资产总计", 0))
        equity: float = bs.get("所有者权益", bs.get("所有者权益总计", bs.get("所有者权益合计", 0)))

        # 同比计算
        revenue_growth: float = 0
        net_profit_growth: float = 0
        asset_growth: float = 0
        equity_growth: float = 0

        if i > 0:
            prev_iso: Dict[str, float] = data["is"].get(periods[i - 1], {})
            prev_bs: Dict[str, float] = data["bs"].get(periods[i - 1], {})
            prev_rev: float = prev_iso.get("营业收入", 0)
            prev_np: float = prev_iso.get("净利润", 0)
            prev_ta: float = prev_bs.get("总资产", prev_bs.get("资产总计", 0))
            prev_eq: float = prev_bs.get("所有者权益", prev_bs.get("所有者权益总计", 0))

            revenue_growth = (revenue - prev_rev) / prev_rev if prev_rev != 0 else 0
            net_profit_growth = (net_profit - prev_np) / prev_np if prev_np != 0 else 0
            asset_growth = (total_assets - prev_ta) / prev_ta if prev_ta != 0 else 0
            equity_growth = (equity - prev_eq) / prev_eq if prev_eq != 0 else 0

        # 扣非净利增长率
        recurring_net: float = iso.get("扣非净利润", net_profit)
        recurring_growth: float = revenue_growth  # 默认用营收增长代替

        if i > 0:
            prev_iso2: Dict[str, float] = data["is"].get(periods[i - 1], {})
            prev_rn: float = prev_iso2.get("扣非净利润", prev_iso2.get("净利润", 0))
            recurring_growth = (
                (recurring_net - prev_rn) / prev_rn if prev_rn != 0 else 0
            )

        ratios.append({
            "period": period,
            "营收增长率": round(revenue_growth, 4),
            "净利润增长率": round(net_profit_growth, 4),
            "总资产增长率": round(asset_growth, 4),
            "净资产增长率": round(equity_growth, 4),
            "扣非净利增长率": round(recurring_growth, 4),
        })
    return ratios


# =============================================================================
# 辅助函数
# =============================================================================


def _estimate_interest_bearing_debt(bs: Dict[str, float]) -> float:
    """估算有息负债总额。

    Args:
        bs: 资产负债表数据。

    Returns:
        float: 有息负债估算值。
    """
    return (
        bs.get("短期借款", 0)
        + bs.get("长期借款", 0)
        + bs.get("应付债券", 0)
        + bs.get("一年内到期的非流动负债", 0)
        + bs.get("租赁负债", 0)
        + bs.get("长期应付款", 0)
    )


def _estimate_depreciation(
    bs: Dict[str, float],
    iso: Dict[str, float],
) -> float:
    """估算当期折旧费用。

    Args:
        bs: 资产负债表数据。
        iso: 利润表数据。

    Returns:
        float: 折旧估算值。
    """
    # 优先使用累计折旧变动
    accum_dep: float = bs.get("累计折旧", 0)
    fixed_assets: float = bs.get("固定资产净额", bs.get("固定资产", 0))
    # 如无法计算，使用固定资产的约5%作为估算
    if accum_dep <= 0:
        # 尝试从费用中推断
        admin: float = iso.get("管理费用", 0)
        cost: float = iso.get("营业成本", 0)
        return (admin + cost) * 0.05  # 粗略估算
    return accum_dep * 0.15  # 如果只有累计折旧，估算当期


def _get_average(
    data: Dict[str, Any],
    account: str,
    period: str,
    bs_key: str = "bs",
) -> float:
    """计算某科目当期与上期的平均值。

    Args:
        data: 财务数据字典。
        account: 科目名称。
        period: 当前期间。
        bs_key: 'bs' 或 'is'。

    Returns:
        float: 平均值。
    """
    periods: List[str] = data.get("periods", [])
    table: Dict[str, Dict[str, float]] = data.get(bs_key, {})

    alt_keys: List[str] = [account, "总资产", "资产总计", "所有者权益", "所有者权益总计"]

    curr_val: float = 0.0
    tbl: Dict[str, float] = table.get(period, {})
    for key in alt_keys:
        if key in account or account in key:
            curr_val = tbl.get(key, tbl.get(account, 0))
            break
    if curr_val == 0:
        curr_val = tbl.get(account, 0)

    try:
        idx: int = periods.index(period)
    except ValueError:
        return curr_val

    if idx == 0:
        return curr_val

    prev_period: str = periods[idx - 1]
    prev_tbl: Dict[str, float] = table.get(prev_period, {})
    prev_val: float = prev_tbl.get(account, 0)
    for key in alt_keys:
        if prev_val == 0:
            prev_val = prev_tbl.get(key, 0)

    return (curr_val + prev_val) / 2.0


def compute_dupont(data: Dict[str, Any]) -> Dict[str, Any]:
    """杜邦三因素分解分析。

    公式: ROE = 净利润率 × 总资产周转率 × 权益乘数

    Args:
        data: 标准化财务数据。

    Returns:
        dict: 各期间的杜邦分解结果。
    """
    results: Dict[str, Any] = {}
    periods: List[str] = data.get("periods", [])

    for i, period in enumerate(periods):
        ratios: List[Dict[str, Any]] = data.get("ratios", {}).get("盈利能力", [])
        operating: List[Dict[str, Any]] = data.get("ratios", {}).get("营运能力", [])
        solvency: List[Dict[str, Any]] = data.get("ratios", {}).get("偿债能力", [])

        npm: float = ratios[i]["净利率"] if i < len(ratios) else 0
        tat: float = operating[i]["总资产周转率"] if i < len(operating) else 0
        em: float = solvency[i]["权益乘数"] if i < len(solvency) else 0
        roe: float = npm * tat * em

        changes: Dict[str, float] = {}
        if i > 0:
            prev_npm: float = results[periods[i - 1]]["净利润率"]
            prev_tat: float = results[periods[i - 1]]["总资产周转率"]
            prev_em: float = results[periods[i - 1]]["权益乘数"]
            changes["Δ利润率贡献"] = round((npm - prev_npm) * prev_tat * prev_em, 4)
            changes["Δ周转率贡献"] = round(npm * (tat - prev_tat) * prev_em, 4)
            changes["Δ杠杆贡献"] = round(npm * tat * (em - prev_em), 4)

        results[period] = {
            "ROE": round(roe, 4),
            "净利润率": round(npm, 4),
            "总资产周转率": round(tat, 4),
            "权益乘数": round(em, 4),
            "连环替代": changes,
        }
    return results


def classify_cashflow_pattern(data: Dict[str, Any]) -> Dict[str, Any]:
    """现金流8模式画像分类。

    Args:
        data: 标准化财务数据。

    Returns:
        dict: 各期间的现金流模式分类结果。
    """
    patterns: Dict[int, Dict[str, Any]] = {
        1: {"name": "现金牛+融资", "signal": "🟡", "desc": "经营现金流健康且在融资扩张，需关注投资效率"},
        2: {"name": "黄金状态", "signal": "✅", "desc": "经营现金流充足，偿还债务后仍有盈余，财务极健康"},
        3: {"name": "成长期", "signal": "⚠️", "desc": "经营现金流为正但持续投资扩张，需关注投资回报期"},
        4: {"name": "成熟稳健", "signal": "✅", "desc": "经营现金流覆盖投资+偿债，运营成熟自给自足"},
        5: {"name": "变卖资产度日", "signal": "🚨", "desc": "经营亏损，靠变卖资产和融资维持，极度危险"},
        6: {"name": "拆东墙补西墙", "signal": "🚨🚨", "desc": "经营+投资均失血，靠处置资产勉强维持"},
        7: {"name": "烧钱模式", "signal": "🚨", "desc": "经营现金流为负，依赖外部融资维持运营"},
        8: {"name": "现金枯竭", "signal": "🚨🚨🚨", "desc": "三大现金流全面为负，企业面临生存危机"},
    }

    results: Dict[str, Any] = {}
    for period in data.get("periods", []):
        cf: Dict[str, float] = data["cf"].get(period, {})
        oper: float = cf.get("经营活动产生的现金流量净额", cf.get("经营CFO", 0))
        invest: float = cf.get("投资活动产生的现金流量净额", cf.get("投资CFI", 0))
        finance: float = cf.get("筹资活动产生的现金流量净额", cf.get("筹资CFF", 0))

        # 检测：如果CF数据完全为空（单一期且无任何CF科目），标注为"无数据"
        cf_keys = [k for k in cf if k not in ("", " ")]
        if not cf_keys or (oper == 0 and invest == 0 and finance == 0 and len(cf_keys) == 0):
            results[period] = {
                "经营CF": "N/A",
                "投资CF": "N/A",
                "筹资CF": "N/A",
                "模式": 0,
                "名称": "无现金流量表数据",
                "信号": "⚠️",
                "描述": "未提供现金流量表，无法进行现金流模式画像。建议补充现金流量表数据以获得完整分析。",
            }
            continue

        oper_sign: str = "+" if oper > 0 else "-"
        invest_sign: str = "+" if invest > 0 else "-"
        finance_sign: str = "+" if finance > 0 else "-"

        pattern_id: int = _map_cf_pattern(oper_sign, invest_sign, finance_sign)
        pattern_info: Dict[str, Any] = patterns.get(pattern_id, patterns[8])

        results[period] = {
            "经营CF": f"{oper_sign} ({oper:,.0f})",
            "投资CF": f"{invest_sign} ({invest:,.0f})",
            "筹资CF": f"{finance_sign} ({finance:,.0f})",
            "模式": pattern_id,
            "名称": pattern_info["name"],
            "信号": pattern_info["signal"],
            "描述": pattern_info["desc"],
        }
    return results


def _map_cf_pattern(oper: str, invest: str, finance: str) -> int:
    """根据三现金流符号映射模式编号。

    Args:
        oper: 经营CF符号。
        invest: 投资CF符号。
        finance: 筹资CF符号。

    Returns:
        int: 现金流模式编号(1-8)。
    """
    mapping: Dict[Tuple[str, str, str], int] = {
        ("+", "+", "+"): 1,
        ("+", "+", "-"): 2,
        ("+", "-", "+"): 3,
        ("+", "-", "-"): 4,
        ("-", "+", "+"): 5,
        ("-", "+", "-"): 6,
        ("-", "-", "+"): 7,
        ("-", "-", "-"): 8,
    }
    return mapping.get((oper, invest, finance), 8)


def compute_altman_zscore(data: Dict[str, Any]) -> Dict[str, float]:
    """计算Altman Z-Score破产预测模型。

    公式: Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    判定: >2.99安全 | 1.81-2.99灰色 | <1.81危险

    Args:
        data: 标准化财务数据。

    Returns:
        dict: 各期间的Z-Score。
    """
    results: Dict[str, float] = {}
    for period in data.get("periods", []):
        bs: Dict[str, float] = data["bs"].get(period, {})
        iso: Dict[str, float] = data["is"].get(period, {})

        total_assets: float = bs.get("总资产", bs.get("资产总计", 1))
        current_assets: float = bs.get("流动资产", bs.get("流动资产合计", 0))
        current_liab: float = bs.get("流动负债", bs.get("流动负债合计", 0))
        retained: float = bs.get("未分配利润", 0)
        ebit: float = iso.get("营业利润", 0)
        equity: float = bs.get("所有者权益", bs.get("所有者权益总计", bs.get("所有者权益合计", 0)))
        total_liab: float = bs.get("总负债", bs.get("负债总计", bs.get("负债合计", 0)))
        revenue: float = iso.get("营业收入", 0)

        working_capital: float = current_assets - current_liab

        x1: float = working_capital / total_assets
        x2: float = retained / total_assets
        x3: float = ebit / total_assets
        x4: float = equity / total_liab if total_liab != 0 else 0
        x5: float = revenue / total_assets

        z: float = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
        results[period] = round(z, 2)

    return results

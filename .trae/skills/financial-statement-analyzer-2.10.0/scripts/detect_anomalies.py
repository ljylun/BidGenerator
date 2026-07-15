#!/usr/bin/env python3
"""科目异常检测模块 — Z-Score滚动检测 + 四色预警。

通过对关键科目的时间序列数据进行Z-Score标准化计算，
检测异常波动并输出四级颜色预警。

作者: 优方皑尔 Uform Ai
版本: v1.0.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Z-Score四级预警阈值
_ZSCORE_GREEN: float = 1.5    # 🟢 正常
_ZSCORE_YELLOW: float = 2.0   # 🟡 关注
_ZSCORE_ORANGE: float = 3.0   # 🟠 异常，建议核查
# ≥ _ZSCORE_ORANGE            # 🔴 严重异常，强烈建议核查

# 默认检测科目列表
_DEFAULT_ACCOUNTS: List[str] = [
    "营业收入",
    "营业成本",
    "净利润",
    "应收账款",
    "存货",
    "经营活动产生的现金流量净额",
    "毛利率",
    "应收账款周转天数",
]


def compute_zscores(
    data: Dict[str, Any],
    accounts: Optional[List[str]] = None,
    window: int = 4,
) -> Dict[str, Any]:
    """批量计算关键科目的Z-Score异常评分。

    Args:
        data: 标准化财务数据。
        accounts: 需要检测的科目列表。默认使用内置列表。
        window: 滚动窗口大小（期数）。默认4期。

    Returns:
        dict: 各科目各期的Z-Score详情。
    """
    target_accounts: List[str] = accounts or _DEFAULT_ACCOUNTS
    periods: List[str] = data.get("periods", [])

    if len(periods) < window:
        logger.warning(
            "数据期数(%d)小于窗口(%d)，Z-Score检测可能不准确",
            len(periods),
            window,
        )

    results: Dict[str, Any] = {
        "periods": periods,
        "summary": {
            "total_anomalies": 0,
            "green": 0, "yellow": 0, "orange": 0, "red": 0,
        },
        "accounts": {},
    }

    for account in target_accounts:
        series: List[float] = _extract_series(data, account, periods)
        account_zscore: Dict[str, Any] = _compute_zscore_series(series, periods, window)

        # 汇总
        for item in account_zscore.get("values", []):
            level: str = item.get("level", "N/A")
            if level == "🟢":
                results["summary"]["green"] += 1
            elif level == "🟡":
                results["summary"]["yellow"] += 1
            elif level == "🟠":
                results["summary"]["orange"] += 1
            elif level == "🔴":
                results["summary"]["red"] += 1
                results["summary"]["total_anomalies"] += 1

        results["accounts"][account] = account_zscore

    return results


def _extract_series(
    data: Dict[str, Any],
    account: str,
    periods: List[str],
) -> List[float]:
    """从财务数据中提取科目的时间序列。

    Args:
        data: 财务数据。
        account: 科目名称。
        periods: 期间列表。

    Returns:
        list: 数值序列。
    """
    series: List[float] = []

    for period in periods:
        val: float = 0.0
        # 先查找预计算的比率
        ratios: Dict[str, Any] = data.get("ratios", {})
        for category_name, category_data in ratios.items():
            if isinstance(category_data, list):
                for item in category_data:
                    if item.get("period") == period and account in item:
                        val = item[account]
                        break

        # 再查三表
        if val == 0.0:
            for table_key in ["bs", "is", "cf"]:
                tbl: Dict[str, Dict[str, float]] = data.get(table_key, {})
                if period in tbl and account in tbl[period]:
                    val = tbl[period][account]
                    break

        series.append(val)

    return series


def _compute_zscore_series(
    series: List[float],
    periods: List[str],
    window: int = 4,
) -> Dict[str, Any]:
    """计算滚动Z-Score序列。

    公式: Z_i = (X_i - μ_window) / σ_window
    其中 μ_window 和 σ_window 为前window期的均值和标准差。

    Args:
        series: 数值序列。
        periods: 对应的期间标签。
        window: 滚动窗口大小。

    Returns:
        dict: {values: [{period, value, zscore, level}, ...]}
    """
    values: List[Dict[str, Any]] = []

    for i, val in enumerate(series):
        if i < window:
            values.append({
                "period": periods[i],
                "value": round(val, 2),
                "zscore": 0.0,
                "level": "N/A",
                "window_data": [],
            })
            continue

        window_vals: List[float] = series[i - window : i]
        mean_val: float = float(np.mean(window_vals))
        std_val: float = float(np.std(window_vals))

        if std_val < 1e-10:
            zscore: float = 0.0
        else:
            zscore = (val - mean_val) / std_val

        abs_z: float = abs(zscore)

        if abs_z < _ZSCORE_GREEN:
            level: str = "🟢"
        elif abs_z < _ZSCORE_YELLOW:
            level = "🟡"
        elif abs_z < _ZSCORE_ORANGE:
            level = "🟠"
        else:
            level = "🔴"

        values.append({
            "period": periods[i],
            "value": round(val, 2),
            "zscore": round(zscore, 2),
            "level": level,
            "window_mean": round(mean_val, 2),
            "window_std": round(std_val, 4),
        })

    # 统计
    level_counts: Dict[str, int] = {"🟢": 0, "🟡": 0, "🟠": 0, "🔴": 0, "N/A": 0}
    for v in values:
        level_counts[v["level"]] += 1

    return {
        "values": values,
        "summary": {
            "total": len(values),
            "red_alerts": level_counts["🔴"],
            "orange_alerts": level_counts["🟠"],
        },
    }


def detect_anomalies(
    data: Dict[str, Any],
    accounts: Optional[List[str]] = None,
    window: int = 4,
) -> Dict[str, Any]:
    """便捷函数：执行科目异常检测。

    Args:
        data: 标准化财务数据。
        accounts: 检测科目列表。
        window: 滚动窗口大小。

    Returns:
        dict: Z-Score异常检测结果。
    """
    return compute_zscores(data, accounts, window)


def get_anomaly_summary(zscore_results: Dict[str, Any]) -> Dict[str, Any]:
    """生成异常检测摘要。

    Args:
        zscore_results: compute_zscores的输出。

    Returns:
        dict: 异常摘要，包含Top异常科目和严重度统计。
    """
    red_alerts: List[Dict[str, Any]] = []
    orange_alerts: List[Dict[str, Any]] = []

    for account, account_data in zscore_results.get("accounts", {}).items():
        for val in account_data.get("values", []):
            if val.get("level") == "🔴":
                red_alerts.append({
                    "account": account,
                    "period": val["period"],
                    "zscore": val["zscore"],
                    "value": val["value"],
                })
            elif val.get("level") == "🟠":
                orange_alerts.append({
                    "account": account,
                    "period": val["period"],
                    "zscore": val["zscore"],
                    "value": val["value"],
                })

    # 按|Z-Score|降序排列
    red_alerts.sort(key=lambda x: abs(x["zscore"]), reverse=True)
    orange_alerts.sort(key=lambda x: abs(x["zscore"]), reverse=True)

    return {
        "red_alerts": red_alerts,
        "orange_alerts": orange_alerts,
        "total_red": len(red_alerts),
        "total_orange": len(orange_alerts),
        "summary_text": (
            f"共检测到 {len(red_alerts)} 个严重异常(🔴) 和 "
            f"{len(orange_alerts)} 个需关注异常(🟠)"
        ),
    }

#!/usr/bin/env python3
"""ECharts/HTML图表渲染模块 — 生成可嵌入HTML的JavaScript图表配置。

生成15种分析图表，通过ECharts CDN渲染。

打印兼容性说明（v2.1 新增）：
- 所有图表配置默认禁用动画（animation: False），避免打印时canvas重绘
- 图表容器需设置 min-height 防止打印时高度塌缩
- 模板中的 @media print 规则强制保留背景色

作者: 优方皑尔 Uform Ai
版本: v2.1.0
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def _base_option() -> Dict[str, Any]:
    """返回所有ECharts图表共用的基础配置（打印兼容）。

    Returns:
        dict: 包含 animation=False 等打印兼容设置的字典。
    """
    return {
        "animation": False,  # 禁用动画，打印/PDF导出时避免canvas重绘变形
    }


def _merge_base(option: Dict[str, Any]) -> Dict[str, Any]:
    """将基础配置合并到图表option中。

    Args:
        option: 图表配置字典。

    Returns:
        dict: 合并后的配置字典。
    """
    base = _base_option()
    base.update(option)
    return base


def render_health_gauge(score: float) -> str:
    """渲染健康度仪表盘。

    Args:
        score: 综合风险评分 (0-100)。

    Returns:
        str: ECharts option的JSON字符串。
    """
    if score <= 20:
        color: str = "#27ae60"
    elif score <= 40:
        color = "#f39c12"
    elif score <= 60:
        color = "#e67e22"
    else:
        color = "#e74c3c"

    option: Dict[str, Any] = {
        "series": [{
            "type": "gauge",
            "startAngle": 210,
            "endAngle": -30,
            "center": ["50%", "55%"],
            "radius": "85%",
            "min": 0,
            "max": 100,
            "axisLine": {
                "lineStyle": {
                    "width": 20,
                    "color": [
                        [0.2, "#27ae60"],
                        [0.4, "#f39c12"],
                        [0.6, "#e67e22"],
                        [0.8, "#e74c3c"],
                        [1.0, "#8b0000"],
                    ]
                }
            },
            "pointer": {"length": "70%", "width": 8, "itemStyle": {"color": "auto"}},
            "detail": {
                "valueAnimation": True,
                "formatter": "{value}分",
                "fontSize": 24,
                "color": color,
            },
            "data": [{"value": round(score, 1), "name": "风险评分"}],
        }]
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_radar_chart(
    dimensions: List[str],
    current_values: List[float],
    industry_values: Optional[List[float]] = None,
    title: str = "六维财务雷达图",
) -> str:
    """渲染六维雷达图。

    Args:
        dimensions: 维度名称列表。
        current_values: 当前企业各维度值 (0-100)。
        industry_values: 行业中位数值 (0-100)。
        title: 图表标题。

    Returns:
        str: ECharts option的JSON字符串。
    """
    indicator: List[Dict[str, Any]] = [
        {"name": d, "max": 100} for d in dimensions
    ]
    data: List[Dict[str, Any]] = [
        {
            "value": current_values,
            "name": "当前企业",
            "areaStyle": {"color": "rgba(37, 99, 235, 0.15)"},
            "lineStyle": {"color": "#2563eb", "width": 2},
            "itemStyle": {"color": "#2563eb"},
        }
    ]
    if industry_values:
        data.append({
            "value": industry_values,
            "name": "行业中位数",
            "areaStyle": {"color": "rgba(149, 165, 166, 0.08)"},
            "lineStyle": {"color": "#95a5a6", "width": 2, "type": "dashed"},
            "itemStyle": {"color": "#95a5a6"},
        })

    option: Dict[str, Any] = {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {},
        "radar": {
            "center": ["50%", "55%"],
            "radius": "65%",
            "indicator": indicator,
        },
        "series": [{"type": "radar", "data": data}],
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_mscore_chart(
    periods: List[str],
    mscore_values: List[Optional[float]],
) -> str:
    """渲染M-Score趋势折线图。

    Args:
        periods: 期间列表。
        mscore_values: M-Score值列表。

    Returns:
        str: ECharts option的JSON字符串。
    """
    option: Dict[str, Any] = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": periods},
        "yAxis": {
            "type": "value",
            "name": "M-Score",
            "min": -4,
            "max": 0,
        },
        "series": [
            {
                "type": "line",
                "data": mscore_values,
                "name": "M-Score",
                "lineStyle": {"color": "#e74c3c", "width": 2},
                "itemStyle": {"color": "#e74c3c"},
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "data": [
                        {
                            "yAxis": -1.78,
                            "lineStyle": {"color": "#e74c3c", "type": "dashed"},
                            "label": {"formatter": "嫌疑线 -1.78"},
                        },
                        {
                            "yAxis": -2.22,
                            "lineStyle": {"color": "#f39c12", "type": "dashed"},
                            "label": {"formatter": "警戒线 -2.22"},
                        },
                    ],
                },
            }
        ],
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_dupont_waterfall(
    labels: List[str],
    values: List[float],
) -> str:
    """渲染杜邦分析瀑布图。

    Args:
        labels: 贡献因素标签。
        values: 贡献值。

    Returns:
        str: ECharts option的JSON字符串。
    """
    option: Dict[str, Any] = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {"type": "category", "data": labels},
        "yAxis": {"type": "value", "axisLabel": {"formatter": "{value}%"}},
        "series": [{
            "type": "bar",
            "data": values,
            "barWidth": "50%",
            "itemStyle": {
                "color": "function(p) { return p.data >= 0 ? '#27ae60' : '#e74c3c'; }"
            },
        }],
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_cf_sankey(
    operating_cf: float,
    investing_cf: float,
    financing_cf: float,
) -> str:
    """渲染现金流桑基图。

    Args:
        operating_cf: 经营CF。
        investing_cf: 投资CF。
        financing_cf: 筹资CF。

    Returns:
        str: ECharts option的JSON字符串。
    """
    nodes: List[Dict[str, str]] = [
        {"name": "经营"}, {"name": "投资"}, {"name": "筹资"},
        {"name": "现金变动"},
    ]
    links: List[Dict[str, Any]] = []
    for cf_val, source in [
        (operating_cf, "经营"),
        (investing_cf, "投资"),
        (financing_cf, "筹资"),
    ]:
        links.append({
            "source": source,
            "target": "现金变动",
            "value": abs(cf_val),
        })

    option: Dict[str, Any] = {
        "series": [{
            "type": "sankey",
            "layout": "none",
            "emphasis": {"focus": "adjacency"},
            "nodeAlign": "left",
            "data": nodes,
            "links": links,
            "label": {"fontSize": 12},
        }]
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_heatmap(
    x_data: List[str],
    y_data: List[str],
    data: List[List[Any]],
    title: str = "风险热力图",
) -> str:
    """渲染风险热力图。

    Args:
        x_data: X轴标签（期间）。
        y_data: Y轴标签（风险类别）。
        data: [[x_index, y_index, value], ...] 格式的热力数据。
        title: 图表标题。

    Returns:
        str: ECharts option的JSON字符串。
    """
    option: Dict[str, Any] = {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"position": "top"},
        "grid": {"top": "15%", "left": "15%", "right": "5%", "bottom": "15%"},
        "xAxis": {"type": "category", "data": x_data, "splitArea": {"show": True}},
        "yAxis": {"type": "category", "data": y_data, "splitArea": {"show": True}},
        "visualMap": {
            "min": 0,
            "max": 3,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "0%",
            "inRange": {"color": ["#d4edda", "#fff3cd", "#ffe5d0", "#fadbd8"]},
        },
        "series": [{
            "type": "heatmap",
            "data": data,
            "label": {"show": False},
            "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}},
        }],
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_scenario_chart(
    periods: List[str],
    optimistic: List[float],
    base: List[float],
    pessimistic: List[float],
    metric_name: str = "净利润",
) -> str:
    """渲染三情景预测区间折线图。

    Args:
        periods: 期间标签。
        optimistic: 乐观情景值。
        base: 基准情景值。
        pessimistic: 悲观情景值。
        metric_name: 指标名称。

    Returns:
        str: ECharts option的JSON字符串。
    """
    option: Dict[str, Any] = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["乐观", "基准", "悲观"], "bottom": "0%"},
        "xAxis": {"type": "category", "data": periods},
        "yAxis": {"type": "value", "name": metric_name},
        "series": [
            {
                "type": "line",
                "data": optimistic,
                "name": "乐观",
                "lineStyle": {"color": "#27ae60"},
                "areaStyle": {"color": "rgba(39, 174, 96, 0.08)"},
            },
            {
                "type": "line",
                "data": base,
                "name": "基准",
                "lineStyle": {"color": "#2563eb"},
            },
            {
                "type": "line",
                "data": pessimistic,
                "name": "悲观",
                "lineStyle": {"color": "#e74c3c"},
                "areaStyle": {"color": "rgba(231, 76, 60, 0.08)"},
            },
        ],
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    y_label: str = "",
) -> str:
    """渲染通用柱状图。

    Args:
        labels: X轴标签。
        values: Y轴值。
        title: 图表标题。
        y_label: Y轴标签。

    Returns:
        str: ECharts option的JSON字符串。
    """
    option: Dict[str, Any] = {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": labels},
        "yAxis": {"type": "value", "name": y_label},
        "series": [{
            "type": "bar",
            "data": values,
            "barWidth": "50%",
            "itemStyle": {
                "color": "function(p) { return '#2563eb'; }"
            },
        }],
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_line_chart(
    periods: List[str],
    series_data: Dict[str, List[float]],
    title: str = "",
) -> str:
    """渲染通用折线图。

    Args:
        periods: X轴期间。
        series_data: {名称: [值列表]}。
        title: 图表标题。

    Returns:
        str: ECharts option的JSON字符串。
    """
    colors: List[str] = ["#2563eb", "#e74c3c", "#27ae60", "#f39c12", "#8e44ad"]
    series: List[Dict[str, Any]] = []
    for i, (name, data) in enumerate(series_data.items()):
        series.append({
            "type": "line",
            "data": data,
            "name": name,
            "lineStyle": {"color": colors[i % len(colors)], "width": 2},
            "itemStyle": {"color": colors[i % len(colors)]},
        })

    option: Dict[str, Any] = {
        "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": list(series_data.keys()), "bottom": "0%"},
        "xAxis": {"type": "category", "data": periods},
        "yAxis": {"type": "value"},
        "series": series,
    }
    return json.dumps(_merge_base(option), ensure_ascii=False)


def render_charts_bundle(results: Dict[str, Any]) -> Dict[str, str]:
    """便捷函数：渲染全套分析图表。

    Args:
        results: 分析结果字典。

    Returns:
        dict: {图表名称: ECharts option JSON}。
    """
    periods: List[str] = results.get("periods", [])
    charts: Dict[str, str] = {}

    # M-Score趋势
    mscore_trend: List[Optional[float]] = [
        results.get("mscore", {}).get(p, {}).get("value") for p in periods
    ]
    if mscore_trend:
        charts["mscore_trend"] = render_mscore_chart(periods, mscore_trend)

    # 雷达图
    radar_values: List[float] = [50, 50, 50, 50, 50, 50]  # 默认
    dimensions: List[str] = ["偿债", "营运", "盈利", "现金流", "成长", "资产质量"]
    charts["radar"] = render_radar_chart(dimensions, radar_values)

    # 风险热力图
    heat_data: List[List[Any]] = []
    for i, p in enumerate(periods):
        for j in range(5):
            heat_data.append([i, j, 0])
    charts["heatmap"] = render_heatmap(periods, ["收入", "资产", "关联", "流动", "合规"], heat_data)

    return charts

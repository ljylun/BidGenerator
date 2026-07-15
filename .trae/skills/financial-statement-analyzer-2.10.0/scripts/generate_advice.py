#!/usr/bin/env python3
"""实用建议生成引擎 — 基于诊断结果匹配生成运营与财务管理建议。

根据触发的红灯信号匹配对应建议模板，生成分岗位、分优先级
的操作建议。

作者: 优方皑尔 Uform Ai
版本: v1.0.0
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_ADVICE_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "references",
    "advice-templates.yaml",
)


class AdviceEngine:
    """实用建议生成引擎。

    根据触发的红灯信号，从advice-templates.yaml中匹配对应的
    运营改善/财务管理/战略调整建议，生成分岗位行动清单。
    """

    def __init__(self, advice_path: Optional[str] = None):
        """初始化建议引擎。

        Args:
            advice_path: 建议模板YAML文件路径。
        """
        self._advice_path: str = advice_path or _DEFAULT_ADVICE_PATH
        self._templates: Dict[str, Any] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """加载建议模板。"""
        try:
            with open(self._advice_path, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = yaml.safe_load(f)
            self._templates = config.get("advice_templates", {})
            logger.info("Loaded %d advice templates", len(self._templates))
        except Exception as exc:
            logger.error("Failed to load advice templates: %s", exc)
            self._templates = {}

    def generate(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """根据分析结果生成建议。

        Args:
            analysis_results: 分析结果字典，需包含:
                - redflags: 红灯扫描结果
                - ratios: 比率计算结果
                - mscore: M-Score结果

        Returns:
            dict: 建议结果。
        """
        triggered_signals: List[str] = self._extract_triggered_signals(
            analysis_results
        )
        advice_list: List[Dict[str, Any]] = []
        matched_templates: set = set()

        for template_name, template in self._templates.items():
            trigger_signals: List[str] = template.get("trigger_signals", [])
            if any(sig in triggered_signals for sig in trigger_signals):
                if template_name not in matched_templates:
                    matched_templates.add(template_name)
                    advice_list.append({
                        "template": template_name,
                        "scenario": template.get("scenario", ""),
                        "severity": template.get("severity", "P1"),
                        "operations": template.get("advice", {}).get("operations", []),
                        "finance": template.get("advice", {}).get("finance", []),
                        "strategy": template.get("advice", {}).get("strategy", []),
                    })

        # 如果没有任何信号触发，生成通用建议
        if not advice_list:
            advice_list = self._generate_default_advice(analysis_results)

        # 按严重度排序
        advice_list.sort(key=lambda a: 0 if a["severity"] == "P0" else 1)

        # 生成分岗位行动清单
        action_checklist: List[Dict[str, Any]] = self._generate_action_checklist(
            advice_list
        )

        return {
            "advice_list": advice_list,
            "total_advice_groups": len(advice_list),
            "action_checklist": action_checklist,
            "summary": self._generate_summary(advice_list),
        }

    @staticmethod
    def _extract_triggered_signals(analysis_results: Dict[str, Any]) -> List[str]:
        """从分析结果中提取触发的红灯信号ID列表。"""
        redflags: Dict[str, Any] = analysis_results.get("redflags", {})
        triggered: List[Dict[str, Any]] = redflags.get("triggered_signals", [])
        return [s["id"] for s in triggered]

    @staticmethod
    def _generate_default_advice(
        analysis_results: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """生成默认通用建议（无红灯触发时）。"""
        return [{
            "template": "default_health",
            "scenario": "财务报表整体健康，无明显红灯信号",
            "severity": "P2",
            "operations": [
                {
                    "action": "持续监控关键财务指标月度变化",
                    "owner": "财务部",
                    "deadline": "持续",
                    "priority": "P2",
                },
                {
                    "action": "定期进行行业对标分析",
                    "owner": "财务部+战略部",
                    "deadline": "季度",
                    "priority": "P2",
                },
            ],
            "finance": [
                {
                    "action": "保持健康的现金流管理",
                    "owner": "财务部",
                    "deadline": "持续",
                    "priority": "P2",
                },
                {
                    "action": "建立财务预警指标体系",
                    "owner": "财务部",
                    "deadline": "2个月内",
                    "priority": "P2",
                },
            ],
            "strategy": [
                {
                    "action": "评估业务增长机会和投资方向",
                    "owner": "管理层",
                    "deadline": "季度",
                    "priority": "P2",
                },
            ],
        }]

    @staticmethod
    def _generate_action_checklist(
        advice_list: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """生成分岗位行动清单。"""
        checklist: List[Dict[str, Any]] = []

        for advice in advice_list:
            for category in ["operations", "finance", "strategy"]:
                for item in advice.get(category, []):
                    checklist.append({
                        "task": item.get("action", ""),
                        "owner": item.get("owner", ""),
                        "deadline": item.get("deadline", ""),
                        "priority": item.get("priority", "P2"),
                        "scenario": advice.get("scenario", ""),
                    })

        # 按优先级排序: P0 > P1 > P2
        priority_order: Dict[str, int] = {"P0": 0, "P1": 1, "P2": 2}
        checklist.sort(key=lambda x: priority_order.get(x["priority"], 99))

        return checklist

    @staticmethod
    def _generate_summary(advice_list: List[Dict[str, Any]]) -> str:
        """生成建议摘要文本。"""
        if not advice_list:
            return "未生成任何建议。"

        p0_count: int = sum(1 for a in advice_list if a["severity"] == "P0")
        p1_count: int = sum(1 for a in advice_list if a["severity"] == "P1")

        parts: List[str] = [f"共生成 {len(advice_list)} 组实用建议"]
        if p0_count:
            parts.append(f"其中 {p0_count} 项为紧急(P0)")
        if p1_count:
            parts.append(f"{p1_count} 项为重要(P1)")

        return "，".join(parts) + "。"


def generate_advice(
    analysis_results: Dict[str, Any],
    advice_path: Optional[str] = None,
) -> Dict[str, Any]:
    """便捷函数：生成实用建议。

    Args:
        analysis_results: 分析结果字典。
        advice_path: 建议模板路径。

    Returns:
        dict: 建议结果。
    """
    engine: AdviceEngine = AdviceEngine(advice_path)
    return engine.generate(analysis_results)

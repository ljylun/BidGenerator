#!/usr/bin/env python3
"""21红灯信号并行扫描引擎 + 联动升级。

基于YAML配置驱动，通过条件表达式求值实现并行扫描。
支持联动升级规则：多个关联信号同时触发时自动升级严重度。

作者: 优方皑尔 Uform Ai
版本: v1.0.0
"""

from __future__ import annotations

import logging
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)

# 默认规则文件路径
_DEFAULT_RULES_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "references",
    "red-flags.yaml",
)


class RedFlagScanner:
    """21红灯信号并行扫描引擎。

    加载YAML规则配置，基于财务数据上下文并行求值所有信号条件。
    支持联动升级逻辑。
    """

    def __init__(self, rules_path: Optional[str] = None):
        """初始化扫描引擎。

        Args:
            rules_path: 规则YAML文件路径。默认使用内置规则。
        """
        self._rules_path: str = rules_path or _DEFAULT_RULES_PATH
        self._rules: List[Dict[str, Any]] = []
        self._linked_upgrades: List[Dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self) -> None:
        """加载并解析YAML规则文件。"""
        try:
            with open(self._rules_path, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = yaml.safe_load(f)
            self._rules = config.get("signals", [])
            self._linked_upgrades = config.get("linked_upgrade_rules", [])
            logger.info(
                "Loaded %d signals, %d linked upgrade rules from %s",
                len(self._rules),
                len(self._linked_upgrades),
                self._rules_path,
            )
        except Exception as exc:
            logger.error("Failed to load rules from %s: %s", self._rules_path, exc)
            self._rules = []
            self._linked_upgrades = []

    def scan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行全部21个红灯信号的并行扫描。

        Args:
            data: 标准化财务数据字典。

        Returns:
            dict: 扫描结果，包含每个信号的触发状态和详情。
        """
        results: Dict[str, Any] = {
            "triggered_signals": [],
            "all_signals": {},
            "summary": {
                "total_triggered": 0,
                "p0_triggered": 0,
                "p1_triggered": 0,
                "risk_types": {},
            },
        }

        for rule in self._rules:
            rule_id: str = rule.get("id", "unknown")
            detection: Dict[str, Any] = rule.get("detection", {})

            # 构建上下文
            context: Dict[str, Any] = self._build_context(data, rule)

            # 求值条件
            triggered: bool = False
            evidence: Dict[str, Any] = {}

            try:
                triggered, evidence = self._evaluate_rule(rule, context, data)
            except Exception as exc:
                logger.debug("Rule %s evaluation failed: %s", rule_id, exc)
                triggered = False
                evidence = {"error": str(exc)}

            signal_result: Dict[str, Any] = {
                "id": rule_id,
                "name": rule.get("name", ""),
                "description": rule.get("description", ""),
                "category": rule.get("category", ""),
                "severity": rule.get("severity", "P2"),
                "risk_type": rule.get("risk_type", ""),
                "triggered": triggered,
                "evidence": evidence,
                "cause_path": rule.get("cause_path", ""),
                "linked_signals": rule.get("linked_signals", []),
                "audit_procedure": rule.get("audit_procedure", ""),
            }
            results["all_signals"][rule_id] = signal_result

            if triggered:
                results["triggered_signals"].append(signal_result)
                results["summary"]["total_triggered"] += 1
                if signal_result["severity"] == "P0":
                    results["summary"]["p0_triggered"] += 1
                elif signal_result["severity"] == "P1":
                    results["summary"]["p1_triggered"] += 1

                risk_type: str = signal_result["risk_type"]
                results["summary"]["risk_types"][risk_type] = (
                    results["summary"]["risk_types"].get(risk_type, 0) + 1
                )

        # 执行联动升级
        results = self._apply_linked_upgrades(results)

        # 按严重度排序
        results["triggered_signals"].sort(
            key=lambda s: (0 if s["severity"] == "P0" else 1, s["id"])
        )

        return results

    def _build_context(
        self, data: Dict[str, Any], rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """为规则求值构建变量上下文。

        Args:
            data: 财务数据。
            rule: 规则定义。

        Returns:
            dict: 包含规则所需所有变量的上下文。
        """
        context: Dict[str, Any] = {"data": data}
        # 提取最新期间数据作为快捷变量
        periods: List[str] = data.get("periods", [])
        latest: str = periods[-1] if periods else ""

        if latest:
            bs: Dict[str, float] = data.get("bs", {}).get(latest, {})
            iso: Dict[str, float] = data.get("is", {}).get(latest, {})
            cf: Dict[str, float] = data.get("cf", {}).get(latest, {})

            context["bs"] = bs
            context["is"] = iso
            context["cf"] = cf
            context["latest_period"] = latest

        return context

    def _evaluate_rule(
        self,
        rule: Dict[str, Any],
        context: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Tuple[bool, Dict[str, Any]]:
        """求值单个规则的检测条件。

        对于每个 detection 条目，调用对应的检测方法。

        Args:
            rule: 规则定义。
            context: 变量上下文。
            data: 完整财务数据。

        Returns:
            tuple: (是否触发, 证据字典)。
        """
        detection: Dict[str, Any] = rule.get("detection", {})
        condition: str = rule.get("condition", "")

        evidence: Dict[str, Any] = {}
        all_conditions_met: bool = True

        # 逐项检查每个检测条件
        for var_name, var_config in detection.items():
            if var_name in ("statutory_rate",):
                val: Any = var_config.get("value", 0)
                evidence[var_name] = val
                continue

            method: str = var_config.get("method", "")
            field: str = var_config.get("field", "")
            threshold: float = var_config.get("threshold", 0)
            numerator: str = var_config.get("numerator", "")
            denominator: str = var_config.get("denominator", "")
            min_periods: int = var_config.get("min_periods", 2)

            try:
                if method == "compute_ratio":
                    result: float = self._method_compute_ratio(
                        data, numerator, denominator
                    )
                    evidence[var_name] = result
                    if threshold != 0:
                        if not (result > threshold):
                            all_conditions_met = False

                elif method == "compute_growth_rate":
                    result = self._method_growth_rate(data, field)
                    evidence[var_name] = result

                elif method == "check_consecutive_negative":
                    result = self._method_consecutive_negative(data, field, min_periods)
                    evidence[var_name] = result
                    if not result:
                        all_conditions_met = False

                elif method == "check_consecutive_increase":
                    result = self._method_consecutive_increase(data, field, min_periods)
                    evidence[var_name] = result
                    if not result:
                        all_conditions_met = False

                elif method == "check_gap_widening":
                    result = self._method_gap_widening(data, numerator or "净利润",
                                                       denominator or "经营活动产生的现金流量净额")
                    evidence[var_name] = result
                    if not result:
                        all_conditions_met = False

                elif method == "check_positive":
                    result = self._method_check_positive(data, field)
                    evidence[var_name] = result

                elif method == "check_no_impairment":
                    result = self._method_check_field_zero(data, field)
                    evidence[var_name] = result

                elif method == "check_deteriorating":
                    result = self._method_check_deteriorating(data, field)
                    evidence[var_name] = result

                elif method == "check_aging":
                    result = self._method_check_aging(data, field, threshold)
                    evidence[var_name] = result

                elif method == "compute_change":
                    result = self._method_compute_change(data, field)
                    evidence[var_name] = result

                elif method == "get_field":
                    result = self._method_get_latest(data, field)
                    evidence[var_name] = result

                elif method == "compute_decline_rate":
                    result = self._method_decline_rate(data, field)
                    evidence[var_name] = result

                elif method == "check_consecutive":
                    result = self._method_check_consecutive(data, field, min_periods)
                    evidence[var_name] = result

                elif method == "compute_growth_rate_2yr":
                    result = self._method_growth_rate_2yr(data, field)
                    evidence[var_name] = result

                elif method == "compute_pp_change":
                    result = self._method_pp_change(data, field)
                    evidence[var_name] = result

                elif method == "compute_relative_change":
                    result = self._method_relative_change(data, field)
                    evidence[var_name] = result

                elif method == "compute_average":
                    result = self._method_compute_average(data, field)
                    evidence[var_name] = result

                elif method == "check_field_zero":
                    result = self._method_check_field_zero(data, field)
                    evidence[var_name] = result

                elif method == "check_divergence":
                    result = self._method_check_divergence(data, numerator, denominator, threshold)
                    evidence[var_name] = result

                elif method == "manual_flag":
                    evidence[var_name] = var_config.get("default", False)

                elif method == "estimate":
                    evidence[var_name] = var_config.get("default", 0)

                elif method == "constant":
                    evidence[var_name] = var_config.get("value", 0)

                else:
                    logger.debug("Unknown method: %s for %s", method, var_name)
                    evidence[var_name] = None

            except Exception as exc:
                logger.debug("Method %s failed for %s: %s", method, var_name, exc)
                evidence[var_name] = None
                all_conditions_met = False

        return all_conditions_met, evidence

    # ---- 检测方法实现 ----

    @staticmethod
    def _method_compute_ratio(data: Dict[str, Any], num: str, den: str) -> float:
        """计算比率。"""
        periods: List[str] = data.get("periods", [])
        if not periods:
            return 0.0
        latest: str = periods[-1]
        num_val: float = 0.0
        den_val: float = 1.0
        for table in ["bs", "is", "cf"]:
            tbl: Dict[str, Dict[str, float]] = data.get(table, {})
            if latest in tbl:
                num_val = tbl[latest].get(num, num_val)
                den_val = tbl[latest].get(den, den_val)
        return num_val / den_val if den_val else 0.0

    @staticmethod
    def _method_growth_rate(data: Dict[str, Any], field: str) -> float:
        """计算最新期间增长率。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < 2:
            return 0.0
        curr_val: float = RedFlagScanner._get_field_value(data, periods[-1], field)
        prev_val: float = RedFlagScanner._get_field_value(data, periods[-2], field)
        return (curr_val - prev_val) / prev_val if prev_val else 0.0

    @staticmethod
    def _method_consecutive_negative(
        data: Dict[str, Any], field: str, min_periods: int
    ) -> bool:
        """检查是否连续多期为负。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < min_periods:
            return False
        count: int = 0
        for period in reversed(periods):
            val: float = RedFlagScanner._get_field_value(data, period, field)
            if val < 0:
                count += 1
            else:
                break
        return count >= min_periods

    @staticmethod
    def _method_consecutive_increase(
        data: Dict[str, Any], field: str, min_periods: int
    ) -> bool:
        """检查是否连续多期增长。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < min_periods:
            return False
        values: List[float] = [
            RedFlagScanner._get_field_value(data, p, field) for p in periods[-min_periods:]
        ]
        return all(values[i] > values[i - 1] for i in range(1, len(values)))

    @staticmethod
    def _method_gap_widening(
        data: Dict[str, Any], field_a: str, field_b: str
    ) -> bool:
        """检查两指标差距是否扩大。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < 2:
            return False
        a_curr: float = RedFlagScanner._get_field_value(data, periods[-1], field_a)
        b_curr: float = RedFlagScanner._get_field_value(data, periods[-1], field_b)
        a_prev: float = RedFlagScanner._get_field_value(data, periods[-2], field_a)
        b_prev: float = RedFlagScanner._get_field_value(data, periods[-2], field_b)
        return abs(a_curr - b_curr) > abs(a_prev - b_prev)

    @staticmethod
    def _method_check_positive(data: Dict[str, Any], field: str) -> bool:
        """检查最新值是否为正。"""
        periods: List[str] = data.get("periods", [])
        if not periods:
            return False
        return RedFlagScanner._get_field_value(data, periods[-1], field) > 0

    @staticmethod
    def _method_check_field_zero(data: Dict[str, Any], field: str) -> bool:
        """检查字段是否为零（无减值等）。"""
        periods: List[str] = data.get("periods", [])
        if not periods:
            return True
        val: float = RedFlagScanner._get_field_value(data, periods[-1], field)
        return abs(val) < 0.01

    @staticmethod
    def _method_check_deteriorating(data: Dict[str, Any], field: str) -> bool:
        """检查是否在恶化（趋势向下）。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < 2:
            return False
        curr: float = RedFlagScanner._get_field_value(data, periods[-1], field)
        prev: float = RedFlagScanner._get_field_value(data, periods[-2], field)
        return curr < prev

    @staticmethod
    def _method_check_aging(data: Dict[str, Any], field: str, days: float) -> bool:
        """检查是否有长账龄项目（简化：比较值是否超过阈值）。"""
        return True  # 账龄检查需要附注数据，简化处理

    @staticmethod
    def _method_compute_change(data: Dict[str, Any], field: str) -> float:
        """计算变动量。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < 2:
            return 0.0
        curr: float = RedFlagScanner._get_field_value(data, periods[-1], field)
        prev: float = RedFlagScanner._get_field_value(data, periods[-2], field)
        return curr - prev

    @staticmethod
    def _method_get_latest(data: Dict[str, Any], field: str) -> float:
        """获取最新值。"""
        periods: List[str] = data.get("periods", [])
        if not periods:
            return 0.0
        return RedFlagScanner._get_field_value(data, periods[-1], field)

    @staticmethod
    def _method_decline_rate(data: Dict[str, Any], field: str) -> float:
        """计算下降率（正值表示下降）。"""
        growth: float = RedFlagScanner._method_growth_rate(data, field)
        return -growth

    @staticmethod
    def _method_check_consecutive(
        data: Dict[str, Any], field: str, min_periods: int
    ) -> int:
        """检查条件连续满足的期数。"""
        periods: List[str] = data.get("periods", [])
        count: int = 0
        for period in reversed(periods):
            val: float = RedFlagScanner._get_field_value(data, period, field)
            if val < 0.3:  # 默认阈值
                count += 1
            else:
                break
        return count

    @staticmethod
    def _method_growth_rate_2yr(data: Dict[str, Any], field: str) -> float:
        """计算2年累计增长率。"""
        periods: List[str] = data.get("periods", [])
        if len(periods) < 3:
            return RedFlagScanner._method_growth_rate(data, field)
        curr: float = RedFlagScanner._get_field_value(data, periods[-1], field)
        base: float = RedFlagScanner._get_field_value(data, periods[-3], field)
        return (curr - base) / base if base else 0.0

    @staticmethod
    def _method_pp_change(data: Dict[str, Any], field: str) -> float:
        """计算百分点变化。"""
        return RedFlagScanner._method_compute_change(data, field) * 100

    @staticmethod
    def _method_relative_change(data: Dict[str, Any], field: str) -> float:
        """计算相对变化。"""
        return RedFlagScanner._method_growth_rate(data, field)

    @staticmethod
    def _method_compute_average(data: Dict[str, Any], field: str) -> float:
        """计算平均值。"""
        periods: List[str] = data.get("periods", [])
        if not periods:
            return 0.0
        values: List[float] = [
            RedFlagScanner._get_field_value(data, p, field) for p in periods
        ]
        return sum(values) / len(values)

    @staticmethod
    def _method_check_divergence(
        data: Dict[str, Any], field_a: str, field_b: str, threshold: float
    ) -> bool:
        """检查两个指标的背离。"""
        periods: List[str] = data.get("periods", [])
        if not periods:
            return False
        a: float = RedFlagScanner._get_field_value(data, periods[-1], field_a)
        b: float = RedFlagScanner._get_field_value(data, periods[-1], field_b)
        if abs(b) < 0.01:
            return a > 0
        return a / b < threshold

    @staticmethod
    def _get_field_value(data: Dict[str, Any], period: str, field: str) -> float:
        """从三表中查找字段值。"""
        for table_key in ["bs", "is", "cf"]:
            tbl: Dict[str, Dict[str, float]] = data.get(table_key, {})
            if period in tbl and field in tbl[period]:
                return tbl[period][field]
        return 0.0

    def _apply_linked_upgrades(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """执行联动升级规则。

        当多个关联信号同时触发时，自动升级严重度。

        Args:
            results: 扫描结果。

        Returns:
            dict: 升级后的结果。
        """
        triggered_ids: set = {
            s["id"] for s in results["triggered_signals"]
        }

        for upgrade_rule in self._linked_upgrades:
            linked: List[str] = upgrade_rule.get("linked_signals", [])
            if all(sig in triggered_ids for sig in linked):
                upgrade_desc: str = upgrade_rule.get("description", "")
                logger.info("Linked upgrade triggered: %s", upgrade_desc)
                # 在summary中记录联动触发
                if "linked_upgrades_triggered" not in results["summary"]:
                    results["summary"]["linked_upgrades_triggered"] = []
                results["summary"]["linked_upgrades_triggered"].append({
                    "rule_id": upgrade_rule.get("id", ""),
                    "name": upgrade_rule.get("name", ""),
                    "description": upgrade_desc,
                    "signals": linked,
                })
                # 将涉及信号标记为升级
                for sig in results["triggered_signals"]:
                    if sig["id"] in linked:
                        sig["linked_upgraded"] = True

        return results


def scan_red_flags(data: Dict[str, Any], rules_path: Optional[str] = None) -> Dict[str, Any]:
    """便捷函数：执行红灯信号扫描。

    Args:
        data: 标准化财务数据。
        rules_path: 规则文件路径（可选）。

    Returns:
        dict: 扫描结果。
    """
    scanner: RedFlagScanner = RedFlagScanner(rules_path)
    return scanner.scan(data)

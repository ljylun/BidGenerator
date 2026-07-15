#!/usr/bin/env python3
"""财务数据校验引擎 — 防止单位混淆、列颠倒、数据遗漏等常见错误。

核心设计原则：
1. 单一数据源（Single Source of Truth）：原始数据以【元】为单位统一存储
2. 自动单位转换：显示层通过 to_wan() / to_yi() 统一转换，禁止手工换算
3. 交叉验证：表格数据与图表数据必须源自同一数据对象
4. 完整性检查：利润表/资产负债表关键字段不得缺失

作者: 优方皑尔 Uform Ai (revised)
版本: v2.0.0 — 新增数据校验层
"""

from __future__ import annotations

import copy
import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# 单位管理常量（全局唯一）
# ============================================================
class Unit:
    """财务数据单位枚举。

    所有内部计算和存储统一使用 YUAN（元）。
    显示时通过转换函数输出。
    """
    YUAN = 1           # 元 (原始精度)
    WAN_YUAN = 10000   # 万元 (1万=10,000元)
    YI_YUAN = 100000000  # 亿元 (1亿=100,000,000元)

    @staticmethod
    def convert(value: float, from_unit: int, to_unit: int) -> float:
        """单位转换。"""
        if from_unit == to_unit:
            return value
        ratio: float = to_unit / from_unit
        return value * ratio

    @staticmethod
    def format_yuan(value: float) -> str:
        """格式化为带逗号的元字符串。"""
        if abs(value) >= 100000000:
            return f"{value:,.2f}"
        elif abs(value) >= 10000:
            return f"{value:,.2f}"
        else:
            return f"{value:.2f}"

    @staticmethod
    def format_wan(value_yuan: float, decimals: int = 2) -> str:
        """将元转换为万元并格式化。"""
        wan: float = value_yuan / Unit.WAN_YUAN
        return f"{wan:,.{decimals}f}"


def to_wan(yuan_value: float, decimals: int = 1) -> float:
    """元→万元 转换（保留指定小数位数）。

    这是图表数据的标准转换函数，所有Chart.js/ECharts的data数组
    都应通过此函数生成，禁止手动÷10000。

    Args:
        yuan_value: 以【元】为单位的数值。
        decimals: 保留小数位数，默认1位。

    Returns:
        float: 以【万元】为单位的数值。
    """
    return round(yuan_value / Unit.WAN_YUAN, decimals)


def to_wan_array(yuan_list: List[float], decimals: int = 1) -> List[float]:
    """批量 元→万元 转换。

    Args:
        yuan_list: 以【元】为单位的数值列表。
        decimals: 保留小数位数。

    Returns:
        list: 以【万元】为单位的数值列表。
    """
    return [to_wan(v, decimals) for v in yuan_list]


def validate_chart_unit(
    chart_data: List[float],
    source_data_yuan: List[float],
    axis_label: str,
    tolerance: float = 0.5,
) -> Dict[str, Any]:
    """校验图表数据与源数据的单位一致性。

    检测逻辑：
    1. 如果chart_data ≈ source_data / 10000 → 正确(万元)
    2. 如果chart_data ≈ source_data / 1000  → 错误(千元)
    3. 如果chart_data ≈ source_data          → 错误(未转换单位)
    4. 其他情况 → 无法判断

    Args:
        chart_data: 图表中实际填入的数据。
        source_data_yuan: 源数据（以元为单位）。
        axis_label: Y轴标注文本（如"金额（万元）"）。
        tolerance: 允许的相对误差比例。

    Returns:
        dict: 校验结果。
    """
    issues: List[str] = []
    is_valid: bool = True

    for i, (chart_val, src_val) in enumerate(zip(chart_data, source_data_yuan)):
        if src_val == 0:
            continue

        expected_wan: float = to_wan(src_val)
        rel_err: float = abs(chart_val - expected_wan) / max(abs(expected_wan), 0.01)

        # 检测是否为千元级错误（×10偏差）
        qian_expected: float = src_val / 1000
        if abs(chart_val - qian_expected) < tolerance and rel_err > 0.05:
            is_valid = False
            issues.append(
                f"[索引{i}] 图表值={chart_val} ≈ 源数据/1000={qian_expected:.1f}"
                f"（千元级），但Y轴标注为'{axis_label}'。"
                f"正确值应为 {expected_wan:.1f}（万元级）。"
                f"可能原因：手工除以了1000而非10000。"
            )
            continue

        # 检测是否未转换单位
        if abs(chart_val - src_val) < tolerance * 10 and abs(src_val) > 10000:
            is_valid = False
            issues.append(
                f"[索引{i}] 图表值={chart_val} 等于源数据原始值({src_val})，"
                f"但Y轴标注为'{axis_label}'。"
                f"忘记调用 to_wan() 进行单位转换！"
            )
            continue

        # 正常误差范围外
        if rel_err > tolerance and abs(chart_val - expected_wan) > 1:
            issues.append(
                f"[索引{i}] 图表值={chart_val} vs 预期={expected_wan:.1f}, "
                f"误差={rel_err*100:.1f}%"
            )

    return {
        "is_valid": is_valid,
        "issues": issues,
        "issue_count": len(issues),
        "axis_label": axis_label,
    }


# ============================================================
# 列顺序校验（防止年初/期末颠倒）
# ============================================================

# 资产负债表典型特征：货币资金、应收账款等流动资产在报告期通常变化不大，
# 但如果年初>>期末 或 期末>>年初 且变动率>50%，需要警惕列颠倒
BS_COLUMNS_SWAPPABLE: List[str] = [
    "货币资金", "应收账款", "预付账款", "其他应收款", "存货",
    "应付账款", "预收款项", "应交税费", "其他应付款",
    "未分配利润",
]

# 利润表不应有"年初余额"/"期末余额"的概念，只有"本期累计"/"本月"
IS_PERIOD_COLUMNS: List[str] = ["本年累计金额", "本月金额", "上年同期"]


def detect_column_swap_risk(
    item_name: str,
    col_a_value: float,
    col_b_value: float,
    col_a_label: str = "年初余额",
    col_b_label: str = "期末余额",
) -> Dict[str, Any]:
    """检测是否存在年初/期末列被颠倒的风险。

    基于业务合理性启发式规则：
    - 对于大多数正常企业，流动资产科目不会出现极端的单向暴增/暴跌
    - 如果 col_a 的值远大于 col_b（如>5倍）且该科目历史上较稳定，可能是列颠倒了

    注意：此检测仅为辅助提示，不能替代人工核对原始报表。

    Args:
        item_name: 科目名称。
        col_a_value: 第一列的值。
        col_b_value: 第二列的值。
        col_a_label: 第一列标签。
        col_b_label: 第二列标签。

    Returns:
        dict: 风险检测结果。
    """
    result: Dict[str, Any] = {
        "item": item_name,
        "col_a": {"label": col_a_label, "value": col_a_value},
        "col_b": {"label": col_b_label, "value": col_b_value},
        "risk_level": "LOW",
        "reason": "",
        "suggestion": "",
    }

    if col_a_value == 0 and col_b_value == 0:
        result["reason"] = "两侧均为0，无法判断"
        return result

    # 计算变动方向
    change_pct: float = 0
    if col_b_value != 0:
        change_pct = (col_b_value - col_a_value) / abs(col_a_value) * 100 if col_a_value != 0 else 999
    elif col_a_value != 0:
        change_pct = -100  # 从有值变成0

    result["change_pct"] = round(change_pct, 1)

    # 风险判断规则
    abs_change: float = abs(change_pct)

    if abs_change > 500:
        # 变动超过500%（6倍），高概率列颠倒
        result["risk_level"] = "HIGH"
        result["reason"] = (
            f"变动幅度达{abs_change:.0f}%，远超正常经营波动范围。"
            f"{col_a_label}={Unit.format_yuan(col_a_value)}, "
            f"{col_b_label}={Unit.format_yuan(col_b_value)}"
        )
        result["suggestion"] = (
            f"请核对PDF原始报表确认 '{item_name}' 的{col_a_label}/{col_b_label}列 "
            f"是否录入正确。建议对照表头行次号逐项核对。"
        )

    elif abs_change > 200:
        result["risk_level"] = "MEDIUM"
        result["reason"] = f"变动幅度达{abs_change:.0f}%，需关注"
        result["suggestion"] = (
            f"'{item_name}' 变动较大，请确认数据录入无误且变动有合理商业原因。"
        )

    else:
        result["risk_level"] = "LOW"
        result["reason"] = f"变动{change_pct:+.1f}%，在正常范围内"

    return result


# ============================================================
# 完整性校验（防止漏录行项目）
# ============================================================

# 利润表必须包含的核心行项目（中文名）
REQUIRED_IS_ITEMS: List[str] = [
    "营业收入", "营业成本", "销售费用", "管理费用", "财务费用",
    "营业利润", "利润总额", "净利润",
]

# 可选但建议包含的项目
RECOMMENDED_IS_ITEMS: List[str] = [
    "投资收益", "营业税金及附加", "研发费用", "资产减值损失",
    "所得税费用", "营业外收入", "营业外支出",
]

# 资产负债表必须包含的核心项目
REQUIRED_BS_ITEMS: List[str] = [
    "货币资金", "应收账款", "存货", "固定资产", "资产总计",
    "应付账款", "实收资本", "未分配利润", "所有者权益合计",
]


def check_income_statement_completeness(
    is_items: List[str],
) -> Dict[str, Any]:
    """检查利润表项目的完整性。

    Args:
        is_items: 已录入的利润表项目名列表。

    Returns:
        dict: 包含缺失项目和建议的结果。
    """
    missing_required: List[str] = [item for item in REQUIRED_IS_ITEMS if item not in is_items]
    missing_recommended: List[str] = [item for item in RECOMMENDED_IS_ITEMS if item not in is_items]

    return {
        "is_complete": len(missing_required) == 0,
        "total_items": len(is_items),
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "completeness_rate": round(
            (len(REQUIRED_IS_ITEMS) - len(missing_required)) / len(REQUIRED_IS_ITEMS) * 100, 1
        ),
        "suggestion": (
            f"缺少必要项目: {', '.join(missing_required)}。"
            if missing_required else (
                f"建议补充可选项目: {', '.join(missing_recommended[:3])}"
                if missing_recommended else "利润表项目完整"
            )
        ),
    }


def check_balance_sheet_completeness(
    bs_items: List[str],
) -> Dict[str, Any]:
    """检查资产负债表项目的完整性。

    Args:
        bs_items: 已录入的资产负债表项目名列表。

    Returns:
        dict: 完整性检查结果。
    """
    missing: List[str] = [item for item in REQUIRED_BS_ITEMS if item not in bs_items]
    return {
        "is_complete": len(missing) == 0,
        "missing": missing,
        "completeness_rate": round(
            (len(REQUIRED_BS_ITEMS) - len(missing)) / len(REQUIRED_BS_ITEMS) * 100, 1
        ),
    }


# ============================================================
# 勾稽关系快速校验
# ============================================================

def quick_crosscheck(
    bs_data: Dict[str, float],
    is_data: Dict[str, float],
    period_label: str = "本期",
) -> List[Dict[str, Any]]:
    """执行一组快速的勾稽关系校验。

    包括：
    1. BS平衡：总资产 ≈ 总负债 + 所有者权益
    2. 未分配利润滚动：本期净利润应反映在未分配利润变动中
    3. 量级一致性：BS与IS的主要数字应在合理量级范围内

    Args:
        bs_data: 资产负债表数据 {科目: 金额(元)}。
        is_data: 利润表数据 {科目: 金额(元)}。
        period_label: 期间标签。

    Returns:
        list: 校验结果列表。
    """
    checks: List[Dict[str, Any]] = []

    # 1. BS平衡
    total_assets: float = bs_data.get("资产总计", bs_data.get("总资产", 0))
    total_liab: float = bs_data.get("负债总计", bs_data.get("流动负债合计", 0)
                         + bs_data.get("非流动负债合计", 0))
    total_equity: float = bs_data.get("所有者权益合计", bs_data.get("所有者权益总计", 0))

    bs_diff: float = abs(total_assets - total_liab - total_equity)
    bs_ok: bool = bs_diff < 1 or (total_assets > 0 and bs_diff / total_assets < 0.001)
    checks.append({
        "check_id": "QC-BS-01",
        "name": "资产负债表平衡",
        "status": "PASS" if bs_ok else "FAIL",
        "detail": f"资产={Unit.format_yuan(total_assets)}, "
                   f"负债+权益={Unit.format_yuan(total_liab + total_equity)}, "
                   f"差额={Unit.format_yuan(bs_diff)}",
        "period": period_label,
    })

    # 2. 量级一致性
    rev: float = abs(is_data.get("营业收入", 0))
    cash: float = abs(bs_data.get("货币资金", 0))
    assets: float = abs(total_assets)

    if rev > 0 and assets > 0:
        ratio: float = assets / rev
        if ratio < 0.1 or ratio > 100:
            checks.append({
                "check_id": "QC-MAG-01",
                "name": "资产负债与收入量级比",
                "status": "WARN",
                "detail": f"资产/营收={ratio:.1f}x（异常范围0.1-100x）。"
                           f"请确认两者使用相同货币单位。",
                "period": period_label,
            })
        else:
            checks.append({
                "check_id": "QC-MAG-01",
                "name": "量级一致性",
                "status": "PASS",
                "detail": f"资产/营收={ratio:.1f}x，量级合理",
                "period": period_label,
            })

    # 3. 净利率合理性
    net_profit: float = is_data.get("净利润", 0)
    if rev > 0:
        npm: float = net_profit / rev * 100
        if npm < -500 or npm > 80:
            checks.append({
                "check_id": "QC-NPM-01",
                "name": "净利率合理性",
                "status": "WARN",
                "detail": f"净利率={npm:.1f}%（异常范围-500%~80%），请核实数据准确性",
                "period": period_label,
            })

    return checks


# ============================================================
# 统一入口：全面数据校验
# ============================================================

class DataValidator:
    """财务数据全面校验器。

    用法示例::

        validator = DataValidator()
        result = validator.validate_all(
            bs_table_data, is_table_data,
            chart_bs_data_source, chart_is_data_source,
            axis_unit_label="万"
        )
        if not result['passed']:
            for issue in result['issues']:
                print(f"[{issue['severity']}] {issue['message']}")
    """

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def validate_all(
        self,
        bs_items: Dict[str, Dict[str, float]],
        is_items: Dict[str, float],
        chart_config: Optional[Dict[str, Any]] = None,
        axis_unit: str = "万元",
    ) -> Dict[str, Any]:
        """执行全部校验。

        Args:
            bs_items: {科目名: {"年初": val, "期末": val}}。
            is_items: {科目名: 金额}。
            chart_config: 图表配置（含数据和轴标签）。
            axis_unit: 图表Y轴标注的单位。

        Returns:
            dict: 全面校验结果。
        """
        self.issues = []
        self.warnings = []

        # 1. 完整性检查
        bs_names: List[str] = list(bs_items.keys())
        is_names: List[str] = list(is_items.keys())

        bs_complete: Dict[str, Any] = check_balance_sheet_completeness(bs_names)
        if not bs_complete["is_complete"]:
            self.issues.append({
                "category": "COMPLETENESS",
                "severity": "ERROR",
                "message": f"资产负债表缺必要项目: {bs_complete['missing']}",
            })

        is_complete: Dict[str, Any] = check_income_statement_completeness(is_names)
        if not is_complete["is_complete"]:
            self.issues.append({
                "category": "COMPLETENESS",
                "severity": "WARN",
                "message": is_complete["suggestion"],
            })

        # 2. 列顺序风险检测
        for item_name, cols in bs_items.items():
            vals: List[float] = list(cols.values())
            labels: List[str] = list(cols.keys())
            if len(vals) == 2:
                risk: Dict[str, Any] = detect_column_swap_risk(
                    item_name, vals[0], vals[1],
                    labels[0] if len(labels) > 0 else "列A",
                    labels[1] if len(labels) > 1 else "列B",
                )
                if risk["risk_level"] == "HIGH":
                    self.issues.append({
                        "category": "COLUMN_ORDER",
                        "severity": "ERROR",
                        "message": f"[{item_name}] {risk['suggestion']} ({risk['reason']})",
                    })
                elif risk["risk_level"] == "MEDIUM":
                    self.warnings.append({
                        "category": "COLUMN_ORDER",
                        "severity": "WARN",
                        "message": f"[{item_name}] {risk['reason']}",
                    })

        # 3. 图表单位校验（如果有图表配置）
        if chart_config:
            for chart_name, cfg in chart_config.items():
                chart_vals: List[float] = cfg.get("data", [])
                source_vals: List[float] = cfg.get("source_yuan", [])
                ax_label: str = cfg.get("axis_label", axis_unit)
                if chart_vals and source_vals:
                    unit_check: Dict[str, Any] = validate_chart_unit(
                        chart_vals, source_vals, ax_label
                    )
                    if not unit_check["is_valid"]:
                        for issue_text in unit_check["issues"]:
                            self.issues.append({
                                "category": "CHART_UNIT",
                                "severity": "CRITICAL",
                                "message": f"[图表:{chart_name}] {issue_text}",
                            })

        # 4. 快速勾稽
        latest_bs: Dict[str, float] = {}
        for item_name, cols in bs_items.items():
            # 取最后一个非零列作为"当前期间"
            for label in ["期末余额", "期末", "年末余额", "年末", "本月金额"]:
                if label in cols:
                    latest_bs[item_name] = cols[label]
                    break
            else:
                # 默认取最后一个值
                values = list(cols.values())
                if values:
                    latest_bs[item_name] = values[-1]

        qc_results: List[Dict[str, Any]] = quick_crosscheck(latest_bs, is_items)
        for qc in qc_results:
            if qc["status"] == "FAIL":
                self.issues.append({
                    "category": "CROSSCHECK",
                    "severity": "ERROR",
                    "message": f"[{qc['check_id']}] {qc['detail']}",
                })
            elif qc["status"] == "WARN":
                self.warnings.append({
                    "category": "CROSSCHECK",
                    "severity": "WARN",
                    "message": f"[{qc['check_id']}] {qc['detail']}",
                })

        return {
            "passed": len(self.issues) == 0,
            "error_count": len(self.issues),
            "warning_count": len(self.warnings),
            "errors": self.issues,
            "warnings": self.warnings,
            "summary": self._build_summary(),
        }

    def _build_summary(self) -> str:
        """构建校验摘要文本。"""
        parts: List[str] = []
        if not self.issues and not self.warnings:
            return "全部校验通过 ✅"

        if self.issues:
            parts.append(f"发现 {len(self.issues)} 个错误")
        if self.warnings:
            parts.append(f"{len(self.warnings)} 个警告")
        return "；".join(parts)


def run_validation_report(
    bs_items: Dict[str, Dict[str, float]],
    is_items: Dict[str, float],
) -> str:
    """便捷函数：运行校验并返回可读的报告文本。

    Args:
        bs_items: 资产负债表数据。
        is_items: 利润表数据。

    Returns:
        str: 格式化的校验报告。
    """
    validator: DataValidator = DataValidator()
    result: Dict[str, Any] = validator.validate_all(bs_items, is_items)

    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("财务数据校验报告")
    lines.append("=" * 60)
    lines.append(f"状态: {'✅ 通过' if result['passed'] else '❌ 发现问题'}")
    lines.append(f"错误: {result['error_count']} | 警告: {result['warning_count']}")
    lines.append("")

    if result["errors"]:
        lines.append("--- 错误 (Errors) ---")
        for err in result["errors"]:
            lines.append(f"  [{err['severity']}] {err['category']}: {err['message']}")
        lines.append("")

    if result["warnings"]:
        lines.append("--- 警告 (Warnings) ---")
        for warn in result["warnings"]:
            lines.append(f"  [{warn['severity']}] {warn['category']}: {warn['message']}")
        lines.append("")

    lines.append("-" * 60)
    lines.append(result["summary"])
    return "\n".join(lines)

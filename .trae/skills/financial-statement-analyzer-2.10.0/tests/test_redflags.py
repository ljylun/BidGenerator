"""21红灯信号扫描引擎测试。

作者: 优方皑尔 Uform Ai
"""

import json
import os
import sys
from typing import Any, Dict

import pytest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
)

from scan_redflags import RedFlagScanner, scan_red_flags

FIXTURES_DIR: str = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_PATH: str = os.path.join(FIXTURES_DIR, "sample_manufacturer.json")


def _load_sample_data() -> Dict[str, Any]:
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


class TestRedFlagScanner:
    """红灯信号扫描测试。"""

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        return _load_sample_data()

    @pytest.fixture
    def scanner(self) -> RedFlagScanner:
        return RedFlagScanner()

    def test_scanner_loads_rules(self, scanner: RedFlagScanner) -> None:
        """测试扫描器成功加载规则。"""
        assert len(scanner._rules) > 0, "No rules loaded"
        assert len(scanner._rules) == 21, f"Expected 21 rules, got {len(scanner._rules)}"

    def test_scan_returns_all_signals(self, scanner: RedFlagScanner, sample_data: Dict[str, Any]) -> None:
        """测试扫描返回全部21个信号的状态。"""
        results: Dict[str, Any] = scanner.scan(sample_data)
        assert len(results["all_signals"]) == 21, (
            f"Expected 21 signals, got {len(results['all_signals'])}"
        )

    def test_scan_has_summary(self, scanner: RedFlagScanner, sample_data: Dict[str, Any]) -> None:
        """测试扫描结果包含汇总信息。"""
        results: Dict[str, Any] = scanner.scan(sample_data)
        assert "summary" in results
        assert "total_triggered" in results["summary"]
        assert "p0_triggered" in results["summary"]
        assert "p1_triggered" in results["summary"]

    def test_scan_triggered_signals_have_required_fields(
        self, scanner: RedFlagScanner, sample_data: Dict[str, Any]
    ) -> None:
        """测试触发信号包含必要字段。"""
        results: Dict[str, Any] = scanner.scan(sample_data)
        for signal in results["triggered_signals"]:
            assert "id" in signal
            assert "name" in signal
            assert "severity" in signal
            assert "risk_type" in signal
            assert "triggered" in signal
            assert signal["triggered"] is True

    def test_triggered_signals_sorted_by_severity(
        self, scanner: RedFlagScanner, sample_data: Dict[str, Any]
    ) -> None:
        """测试触发信号按严重度排序（P0优先）。"""
        results: Dict[str, Any] = scanner.scan(sample_data)
        triggered: list = results["triggered_signals"]
        severities: list = [s["severity"] for s in triggered]
        # P0应在P1之前
        p0_indices: list = [i for i, s in enumerate(severities) if s == "P0"]
        p1_indices: list = [i for i, s in enumerate(severities) if s == "P1"]
        if p0_indices and p1_indices:
            assert max(p0_indices) < min(p1_indices), "P0 signals should come before P1"


class TestRedFlagEdgeCases:
    """红灯扫描边界测试。"""

    def test_empty_data(self) -> None:
        """测试空数据不崩溃。"""
        scanner: RedFlagScanner = RedFlagScanner()
        results: Dict[str, Any] = scanner.scan({"periods": [], "bs": {}, "is": {}, "cf": {}})
        assert "triggered_signals" in results

    def test_single_period_data(self) -> None:
        """测试单期数据。"""
        scanner: RedFlagScanner = RedFlagScanner()
        data: Dict[str, Any] = {
            "periods": ["2021"],
            "bs": {"2021": {"总资产": 1000, "流动资产": 600, "流动负债": 300, "应收账款": 200,
                           "货币资金": 100, "存货": 150, "固定资产净额": 350, "开发支出": 10,
                           "商誉": 50, "其他应收款": 20, "总负债": 500, "资产总计": 1000,
                           "负债总计": 500, "所有者权益": 500, "所有者权益总计": 500}},
            "is": {"2021": {"营业收入": 800, "营业成本": 560, "净利润": 80, "研发费用": 30,
                           "销售费用": 40, "管理费用": 50, "营业利润": 90, "利润总额": 88,
                           "所得税费用": 22}},
            "cf": {"2021": {"经营活动产生的现金流量净额": 60, "经营CFO": 60}},
        }
        results: Dict[str, Any] = scanner.scan(data)
        # 不应抛出异常
        assert "all_signals" in results

"""M-Score / F-Score 造假检测测试。

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

from compute_mscore import compute_fscore, compute_mscore

FIXTURES_DIR: str = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_PATH: str = os.path.join(FIXTURES_DIR, "sample_manufacturer.json")


def _load_sample_data() -> Dict[str, Any]:
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


class TestMScore:
    """M-Score计算测试。"""

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        return _load_sample_data()

    def test_mscore_returns_all_periods(self, sample_data: Dict[str, Any]) -> None:
        """测试M-Score返回所有期间。"""
        results: Dict[str, Any] = compute_mscore(sample_data)
        for period in sample_data["periods"]:
            assert period in results, f"Missing period: {period}"

    def test_first_period_no_mscore(self, sample_data: Dict[str, Any]) -> None:
        """测试第一期无M-Score（缺上年数据）。"""
        results: Dict[str, Any] = compute_mscore(sample_data)
        first: dict = results[sample_data["periods"][0]]
        assert first["value"] is None
        assert "无法计算" in str(first["verdict"])

    def test_mscore_outputs_variables(self, sample_data: Dict[str, Any]) -> None:
        """测试M-Score输出8个变量。"""
        results: Dict[str, Any] = compute_mscore(sample_data)
        # 取第二期
        period: str = sample_data["periods"][1]
        variables: Dict[str, float] = results[period]["variables"]
        expected_vars: list = ["DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "TATA", "LVGI"]
        for var in expected_vars:
            assert var in variables, f"Missing variable: {var}"
        assert len(variables) == 8

    def test_mscore_formula_correct(self, sample_data: Dict[str, Any]) -> None:
        """测试M-Score公式计算正确。"""
        results: Dict[str, Any] = compute_mscore(sample_data)
        period: str = sample_data["periods"][1]
        variables: Dict[str, float] = results[period]["variables"]

        # 手动验证公式
        coefficients: Dict[str, float] = {
            "DSRI": 0.920, "GMI": 0.528, "AQI": 0.404, "SGI": 0.892,
            "DEPI": 0.115, "SGAI": -0.172, "TATA": 4.679, "LVGI": -0.327,
        }
        intercept: float = -4.84
        expected: float = round(
            intercept + sum(coefficients[var] * variables[var] for var in coefficients), 3
        )
        assert results[period]["value"] == expected

    def test_mscore_verdict(self, sample_data: Dict[str, Any]) -> None:
        """测试M-Score判定逻辑。"""
        results: Dict[str, Any] = compute_mscore(sample_data)
        period: str = sample_data["periods"][1]
        value: float = results[period]["value"]  # type: ignore[assignment]
        if value > -1.78:
            assert results[period]["verdict"] == "造假嫌疑"
        elif value > -2.22:
            assert results[period]["verdict"] == "造假高风险"
        else:
            assert results[period]["verdict"] == "正常范围"


class TestFScore:
    """F-Score计算测试。"""

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        return _load_sample_data()

    def test_fscore_total_range(self, sample_data: Dict[str, Any]) -> None:
        """测试F-Score总分在0-9范围内。"""
        results: Dict[str, Any] = compute_fscore(sample_data)
        for period, data in results.items():
            assert 0 <= data["total"] <= 9, f"F-Score {data['total']} out of range"

    def test_fscore_components_sum(self, sample_data: Dict[str, Any]) -> None:
        """测试F-Score分项之和等于总分。"""
        results: Dict[str, Any] = compute_fscore(sample_data)
        for period, data in results.items():
            component_sum: int = (
                data["profitability"] + data["leverage"] + data["efficiency"]
            )
            assert component_sum == data["total"]

    def test_fscore_verdict(self, sample_data: Dict[str, Any]) -> None:
        """测试F-Score判定。"""
        results: Dict[str, Any] = compute_fscore(sample_data)
        for period, data in results.items():
            if data["total"] <= 3:
                assert data["verdict"] == "高风险财务困境"
            elif data["total"] <= 5:
                assert data["verdict"] == "中等风险"
            else:
                assert data["verdict"] == "财务健康"

    def test_fscore_details(self, sample_data: Dict[str, Any]) -> None:
        """测试F-Score包含9个判定详情。"""
        results: Dict[str, Any] = compute_fscore(sample_data)
        period: str = sample_data["periods"][-1]
        details: list = results[period]["details"]
        assert len(details) == 9, f"Expected 9 details, got {len(details)}"

"""财务比率计算引擎测试。

作者: 优方皑尔 Uform Ai
"""

import json
import os
import sys
from typing import Any, Dict

import pytest

# 添加 scripts 目录到路径
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
)

from compute_ratios import (
    classify_cashflow_pattern,
    compute_all_ratios,
    compute_altman_zscore,
    compute_dupont,
)

# 加载测试数据
FIXTURES_DIR: str = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_PATH: str = os.path.join(FIXTURES_DIR, "sample_manufacturer.json")


def _load_sample_data() -> Dict[str, Any]:
    """加载测试fixture数据。"""
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


class TestComputeRatios:
    """比率计算测试类。"""

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        """加载样本数据fixture。"""
        return _load_sample_data()

    def test_compute_all_ratios_returns_five_categories(self, sample_data: Dict[str, Any]) -> None:
        """测试返回五个维度的比率。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        expected_categories: list = ["偿债能力", "营运能力", "盈利能力", "现金流质量", "成长能力"]
        for cat in expected_categories:
            assert cat in ratios, f"Missing category: {cat}"
            assert isinstance(ratios[cat], list)
            assert len(ratios[cat]) > 0

    def test_solvency_ratios_positive(self, sample_data: Dict[str, Any]) -> None:
        """测试偿债能力指标非负。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        solvency: list = ratios["偿债能力"]
        for period_data in solvency:
            for key in ["流动比率", "速动比率", "资产负债率"]:
                assert period_data[key] >= 0, f"{key} should be >= 0"

    def test_profitability_ratios_reasonable(self, sample_data: Dict[str, Any]) -> None:
        """测试盈利能力指标在合理范围。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        profitability: list = ratios["盈利能力"]
        for period_data in profitability:
            assert 0 <= period_data["毛利率"] <= 1, "毛利率应在0-1之间"
            assert 0 <= period_data["净利率"] <= 1, "净利率应在0-1之间"
            assert period_data["ROE"] < 2.0, "ROE不应超过200%"

    def test_cashflow_ratios(self, sample_data: Dict[str, Any]) -> None:
        """测试现金流质量指标计算正确。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        cf: list = ratios["现金流质量"]
        # 2021年：经营CF=3000万 净利≈7987.5万
        period_2021: dict = cf[2]  # 第三期
        assert period_2021["period"] == "2021"
        assert period_2021["经营CF/净利"] < 1.0, "经营CF应小于净利"

    def test_growth_ratios(self, sample_data: Dict[str, Any]) -> None:
        """测试成长能力指标。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        growth: list = ratios["成长能力"]
        # 第一期增长率应为0（无上年数据）
        assert growth[0]["营收增长率"] == 0, "第一期增长率应为0"
        # 2020年营收增长应为 (920-800)/800 = 0.15
        assert abs(growth[1]["营收增长率"] - 0.15) < 0.01

    def test_dupont_decomposition(self, sample_data: Dict[str, Any]) -> None:
        """测试杜邦分解。"""
        # 先计算比率
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        sample_data["ratios"] = ratios
        dupont: Dict[str, Any] = compute_dupont(sample_data)
        assert "2021" in dupont
        assert "ROE" in dupont["2021"]
        # ROE ≈ 净利率 × 周转率 × 权益乘数
        d2021: dict = dupont["2021"]
        roe_computed: float = d2021["净利润率"] * d2021["总资产周转率"] * d2021["权益乘数"]
        assert abs(roe_computed - d2021["ROE"]) < 0.001

    def test_cashflow_pattern_classification(self, sample_data: Dict[str, Any]) -> None:
        """测试现金流8模式分类。"""
        patterns: Dict[str, Any] = classify_cashflow_pattern(sample_data)
        # 2021年：经营CF+、投资CF-、筹资CF- → 模式4（成熟稳健）
        assert "2021" in patterns
        pattern_2021: dict = patterns["2021"]
        assert pattern_2021["模式"] == 4, f"Expected pattern 4, got {pattern_2021['模式']}"

    def test_altman_zscore(self, sample_data: Dict[str, Any]) -> None:
        """测试Altman Z-Score。"""
        zscores: Dict[str, float] = compute_altman_zscore(sample_data)
        assert "2021" in zscores
        # 制造业健康企业Z-Score应>1.81
        assert zscores["2021"] > 1.0, f"Z-Score should be > 1.0, got {zscores['2021']}"

    def test_operating_ratios(self, sample_data: Dict[str, Any]) -> None:
        """测试营运能力指标。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample_data)
        operating: list = ratios["营运能力"]
        # DSO应为正数
        for period_data in operating:
            assert period_data["应收周转天数(DSO)"] > 0
            assert period_data["存货周转天数(DIO)"] > 0
        # CCC = DSO + DIO - DPO
        for period_data in operating:
            ccc: float = (
                period_data["应收周转天数(DSO)"]
                + period_data["存货周转天数(DIO)"]
                - period_data["应付周转天数(DPO)"]
            )
            assert abs(ccc - period_data["现金转化周期(CCC)"]) < 0.1


class TestEdgeCases:
    """边界值测试。"""

    def test_zero_denominator(self) -> None:
        """测试分母为0的情况。"""
        data: Dict[str, Any] = {
            "periods": ["2021"],
            "bs": {"2021": {"总资产": 0, "资产总计": 0, "流动资产": 0, "流动负债": 1000000,
                           "所有者权益": 0, "所有者权益总计": 0}},
            "is": {"2021": {"营业收入": 0, "营业成本": 0, "净利润": 0}},
            "cf": {"2021": {"经营活动产生的现金流量净额": 0}},
        }
        ratios: Dict[str, Any] = compute_all_ratios(data)
        # 不应抛出异常
        assert "偿债能力" in ratios

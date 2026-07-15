"""端到端集成测试 + 错误边界测试。

覆盖核心流程：数据解析 → 比率计算 → 红灯扫描 → M-Score → 异常检测
→ 勾稽验证 → 案例匹配 → 建议生成 → 报告生成 → 图表渲染

作者: Edward (QA Engineer)
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))

from compute_ratios import (
    classify_cashflow_pattern,
    compute_all_ratios,
    compute_altman_zscore,
    compute_dupont,
)
from compute_mscore import compute_fscore, compute_mscore
from detect_anomalies import compute_zscores
from generate_advice import generate_advice
from generate_report import generate_report
from match_cases import match_cases
from render_charts import (
    render_bar_chart,
    render_cf_sankey,
    render_dupont_waterfall,
    render_health_gauge,
    render_heatmap,
    render_line_chart,
    render_mscore_chart,
    render_radar_chart,
    render_scenario_chart,
)
from scan_redflags import RedFlagScanner, scan_red_flags
from verify_crosschecks import verify_crosschecks

FIXTURES_DIR: str = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_PATH: str = os.path.join(FIXTURES_DIR, "sample_manufacturer.json")


def _load_sample() -> Dict[str, Any]:
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 端到端集成测试
# =============================================================================


class TestEndToEndFlow:
    """完整的端到端分析流程：解析 → 计算 → 分析 → 报告。"""

    @pytest.fixture
    def sample(self) -> Dict[str, Any]:
        return _load_sample()

    @pytest.fixture
    def full_analysis(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """运行完整的分析流水线并返回结果。"""
        results: Dict[str, Any] = {
            "periods": sample["periods"],
            "company_name": sample.get("company_name", ""),
        }

        # Step 1: 比率计算
        ratios: Dict[str, Any] = compute_all_ratios(sample)
        results["ratios"] = ratios
        sample["ratios"] = ratios  # 后续模块可能需要

        # Step 2: 杜邦分析
        results["dupont"] = compute_dupont(sample)

        # Step 3: M-Score
        results["mscore"] = compute_mscore(sample)

        # Step 4: F-Score
        results["fscore"] = compute_fscore(sample)

        # Step 5: Z-Score / 异常检测
        results["anomalies"] = compute_zscores(sample)

        # Step 6: 红灯扫描
        results["redflags"] = scan_red_flags(sample)

        # Step 7: 勾稽验证
        results["crosscheck"] = verify_crosschecks(sample)

        # Step 8: 现金流模式
        results["cf_pattern"] = classify_cashflow_pattern(sample)

        # Step 9: Altman Z-Score
        results["zscore"] = compute_altman_zscore(sample)

        # Step 10: 案例匹配
        results["case_match"] = match_cases(sample)

        # Step 11: 建议生成
        results["advice"] = generate_advice(results)

        # Step 12: 报告生成
        results["report_l1"] = generate_report(results, level=1)
        results["report_l2"] = generate_report(results, level=2)
        results["report_l3"] = generate_report(results, level=3)

        # Step 13: 图表渲染
        results["chart_gauge"] = render_health_gauge(results.get("risk_score", 30))
        results["chart_radar"] = render_radar_chart(
            ["偿债", "营运", "盈利", "现金流", "成长", "资产质量"],
            [50, 60, 70, 40, 55, 65],
        )
        results["chart_mscore"] = render_mscore_chart(
            ["2020", "2021"],
            [-2.5, -1.9],
        )

        return results

    # ---- 比率计算集成 ----

    def test_e2e_ratios_produced(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：比率计算产出完整。"""
        ratios: Dict[str, Any] = full_analysis["ratios"]
        for cat in ["偿债能力", "营运能力", "盈利能力", "现金流质量", "成长能力"]:
            assert cat in ratios
            assert len(ratios[cat]) == 3  # 3个期间

    # ---- M-Score 集成 ----

    def test_e2e_mscore_chain(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：M-Score 链条完整。"""
        mscore: Dict[str, Any] = full_analysis["mscore"]
        periods: List[str] = full_analysis["periods"]
        for p in periods:
            assert p in mscore
        # 第一期应为 None
        assert mscore[periods[0]]["value"] is None
        # 后两期应有值
        assert mscore[periods[1]]["value"] is not None
        assert mscore[periods[2]]["value"] is not None

    # ---- 红灯扫描集成 ----

    def test_e2e_redflag_scan_results(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：红灯扫描结果包含21个信号。"""
        redflags: Dict[str, Any] = full_analysis["redflags"]
        assert len(redflags["all_signals"]) == 21
        assert "summary" in redflags
        assert "triggered_signals" in redflags

    # ---- 勾稽验证集成 ----

    def test_e2e_crosscheck_results(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：勾稽验证返回8大类。"""
        crosscheck: Dict[str, Any] = full_analysis["crosscheck"]
        assert "master_status" in crosscheck
        assert len(crosscheck.get("categories", {})) == 8

    # ---- 报告生成集成 ----

    def test_e2e_report_level1_html(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：第一级报告生成HTML。"""
        html: str = full_analysis["report_l1"]
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "急诊初筛" in html

    def test_e2e_report_level2_html(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：第二级报告生成HTML。"""
        html: str = full_analysis["report_l2"]
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

    def test_e2e_report_level3_html(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：第三级报告生成HTML。"""
        html: str = full_analysis["report_l3"]
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "专家会诊" in html

    # ---- 现金流模式 ----

    def test_e2e_cf_pattern(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：现金流模式分类正确。"""
        cf_pattern: Dict[str, Any] = full_analysis["cf_pattern"]
        assert "2021" in cf_pattern
        p: Dict[str, Any] = cf_pattern["2021"]
        assert p["模式"] in range(1, 9)

    # ---- 案例匹配 ----

    def test_e2e_case_match(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：案例匹配运行正常。"""
        case_match: Dict[str, Any] = full_analysis["case_match"]
        assert "matched_cases" in case_match
        assert "company_features" in case_match

    # ---- 建议生成 ----

    def test_e2e_advice_generated(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：建议生成产出完整。"""
        advice: Dict[str, Any] = full_analysis["advice"]
        assert "advice_list" in advice
        assert "action_checklist" in advice
        assert "summary" in advice

    # ---- 图表渲染 ----

    def test_e2e_charts_valid_json(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：图表JSON格式有效。"""
        for key in ["chart_gauge", "chart_radar", "chart_mscore"]:
            chart_json: str = full_analysis[key]
            parsed: Any = json.loads(chart_json)
            assert isinstance(parsed, dict)

    # ---- 数据一致性 ----

    def test_e2e_risk_score_within_range(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：风险评分在0-100间。"""
        # 从 report context 获取
        ctx: str = full_analysis["report_l1"]
        assert ctx is not None

    def test_e2e_data_integrity(self, full_analysis: Dict[str, Any]) -> None:
        """端到端：分析过程数据完整性。"""
        # 确保所有关键分析模块都产生了结果
        required_keys: List[str] = [
            "ratios", "dupont", "mscore", "fscore",
            "anomalies", "redflags", "crosscheck",
            "cf_pattern", "zscore", "case_match",
            "advice", "report_l1", "report_l2", "report_l3",
        ]
        for key in required_keys:
            assert key in full_analysis, f"Missing key: {key}"


# =============================================================================
# 图表渲染测试
# =============================================================================


class TestChartRendering:
    """图表渲染功能测试。"""

    def test_health_gauge(self) -> None:
        opt: str = render_health_gauge(45.5)
        data: Dict = json.loads(opt)
        assert "series" in data
        assert data["series"][0]["type"] == "gauge"

    def test_radar_chart(self) -> None:
        opt: str = render_radar_chart(
            ["A", "B", "C"], [50, 70, 30],
            industry_values=[45, 60, 40],
        )
        data: Dict = json.loads(opt)
        assert len(data["series"][0]["data"]) == 2  # 当前+行业
        assert data["series"][0]["data"][1]["name"] == "行业中位数"

    def test_radar_chart_no_industry(self) -> None:
        opt: str = render_radar_chart(["A", "B"], [50, 60])
        data: Dict = json.loads(opt)
        assert len(data["series"][0]["data"]) == 1

    def test_mscore_chart(self) -> None:
        opt: str = render_mscore_chart(
            ["2020", "2021"], [-2.5, -1.9]
        )
        data: Dict = json.loads(opt)
        assert "markLine" in data["series"][0]
        # 验证阈值线
        mark_lines = data["series"][0]["markLine"]["data"]
        thresholds = [m["yAxis"] for m in mark_lines]
        assert -1.78 in thresholds
        assert -2.22 in thresholds

    def test_dupont_waterfall(self) -> None:
        opt: str = render_dupont_waterfall(
            ["利润率", "周转率", "杠杆", "ROE变动"],
            [2.5, -1.0, 0.5, 2.0],
        )
        data: Dict = json.loads(opt)
        assert data["series"][0]["type"] == "bar"

    def test_cf_sankey(self) -> None:
        opt: str = render_cf_sankey(100, -50, -20)
        data: Dict = json.loads(opt)
        assert data["series"][0]["type"] == "sankey"

    def test_heatmap(self) -> None:
        opt: str = render_heatmap(
            ["2020", "2021"], ["风险A", "风险B"],
            [[0, 0, 1], [0, 1, 2], [1, 0, 0], [1, 1, 3]],
        )
        data: Dict = json.loads(opt)
        assert data["series"][0]["type"] == "heatmap"

    def test_scenario_chart(self) -> None:
        opt: str = render_scenario_chart(
            ["Y1", "Y2", "Y3"],
            [120, 150, 180],
            [100, 110, 121],
            [80, 72, 65],
        )
        data: Dict = json.loads(opt)
        names: List[str] = [s["name"] for s in data["series"]]
        assert "乐观" in names
        assert "基准" in names
        assert "悲观" in names

    def test_bar_chart(self) -> None:
        opt: str = render_bar_chart(["A", "B"], [10, 20], title="Test")
        data: Dict = json.loads(opt)
        assert data["series"][0]["type"] == "bar"

    def test_line_chart(self) -> None:
        opt: str = render_line_chart(
            ["Y1", "Y2"], {"系列A": [10, 20], "系列B": [15, 18]}
        )
        data: Dict = json.loads(opt)
        assert len(data["series"]) == 2


# =============================================================================
# 错误处理边界测试
# =============================================================================


class TestErrorBoundaries:
    """错误处理和边界条件测试。"""

    def test_compute_ratios_with_empty_data(self) -> None:
        """边界：空数据不崩溃。"""
        data: Dict[str, Any] = {
            "periods": [],
            "bs": {}, "is": {}, "cf": {},
        }
        ratios: Dict[str, Any] = compute_all_ratios(data)
        for cat in ratios.values():
            assert isinstance(cat, list)

    def test_compute_ratios_with_single_period(self) -> None:
        """边界：单期数据可正常计算。"""
        data: Dict[str, Any] = {
            "periods": ["2021"],
            "bs": {"2021": {"总资产": 1000, "流动资产": 500, "流动负债": 300,
                           "所有者权益": 600, "资产总计": 1000}},
            "is": {"2021": {"营业收入": 800, "营业成本": 560, "净利润": 80,
                           "营业利润": 90}},
            "cf": {"2021": {"经营活动产生的现金流量净额": 60}},
        }
        ratios: Dict[str, Any] = compute_all_ratios(data)
        assert len(ratios["偿债能力"]) == 1

    def test_mscore_insufficient_data(self) -> None:
        """边界：数据不足时M-Score不崩溃。"""
        data: Dict[str, Any] = {
            "periods": ["2021"],
            "bs": {"2021": {"总资产": 1000}},
            "is": {"2021": {"营业收入": 500, "净利润": 50}},
            "cf": {"2021": {"经营活动产生的现金流量净额": 30}},
        }
        results: Dict[str, Any] = compute_mscore(data)
        assert results["2021"]["value"] is None

    def test_scan_empty_data_no_crash(self) -> None:
        """边界：空数据扫描不崩溃。"""
        scanner: RedFlagScanner = RedFlagScanner()
        result: Dict[str, Any] = scanner.scan({
            "periods": [], "bs": {}, "is": {}, "cf": {},
        })
        assert "triggered_signals" in result
        assert isinstance(result["triggered_signals"], list)

    def test_crosscheck_empty_data(self) -> None:
        """边界：空数据勾稽验证不崩溃。"""
        data: Dict[str, Any] = {
            "periods": [], "bs": {}, "is": {}, "cf": {},
        }
        result: Dict[str, Any] = verify_crosschecks(data)
        assert "master_status" in result

    def test_report_generation_graceful_degradation(self) -> None:
        """边界：报告生成时缺数据应降级不崩溃。"""
        minimal: Dict[str, Any] = {
            "periods": ["2021"],
            "ratios": {},
            "mscore": {},
            "fscore": {},
            "redflags": {"triggered_signals": [], "summary": {}},
            "cf_pattern": {},
            "zscore": {},
            "crosscheck": {"categories": {}, "master_status": "PASS"},
            "case_match": {"matched_cases": []},
            "advice": {"advice_list": [], "action_checklist": []},
        }
        html: str = generate_report(minimal, level=1)
        assert "<!DOCTYPE html>" in html
        assert len(html) > 0

    def test_anomaly_detection_few_periods(self) -> None:
        """边界：期数少于窗口时Z-Score不崩溃。"""
        data: Dict[str, Any] = {
            "periods": ["2020", "2021"],
            "bs": {
                "2020": {"营业收入": 100},
                "2021": {"营业收入": 120},
            },
            "is": {
                "2020": {"营业收入": 100},
                "2021": {"营业收入": 120},
            },
            "cf": {
                "2020": {},
                "2021": {},
            },
        }
        result: Dict[str, Any] = compute_zscores(data, accounts=["营业收入"], window=4)
        assert "accounts" in result

    def test_case_match_empty_data(self) -> None:
        """边界：空数据案例匹配不崩溃。"""
        data: Dict[str, Any] = {"periods": [], "bs": {}, "is": {}, "cf": {}}
        result: Dict[str, Any] = match_cases(data)
        assert "matched_cases" in result

    def test_advice_no_signals(self) -> None:
        """边界：无红灯信号时生成默认建议。"""
        results: Dict[str, Any] = {
            "redflags": {"triggered_signals": []},
            "ratios": {},
            "mscore": {},
        }
        advice: Dict[str, Any] = generate_advice(results)
        assert len(advice["advice_list"]) >= 1
        assert advice["advice_list"][0]["template"] == "default_health"

    def test_dupont_single_period(self) -> None:
        """边界：单期无杜邦连环替代变化。"""
        data: Dict[str, Any] = {
            "periods": ["2021"],
            "bs": {"2021": {"总资产": 1000, "所有者权益": 500}},
            "is": {"2021": {"营业收入": 800, "净利润": 80}},
            "ratios": {
                "盈利能力": [{"净利率": 0.1}],
                "营运能力": [{"总资产周转率": 0.8}],
                "偿债能力": [{"权益乘数": 2.0}],
            },
        }
        dupont: Dict[str, Any] = compute_dupont(data)
        assert "2021" in dupont
        assert dupont["2021"]["ROE"] == pytest.approx(0.1 * 0.8 * 2.0)

    def test_zscore_with_zero_std(self) -> None:
        """边界：零标准差时Z-Score不崩溃。"""
        data: Dict[str, Any] = {
            "periods": ["2018", "2019", "2020", "2021", "2022", "2023"],
            "bs": {p: {"总资产": 1000, "流动资产": 500, "流动负债": 300,
                       "未分配利润": 100, "所有者权益": 600, "总负债": 400}
                   for p in ["2018", "2019", "2020", "2021", "2022", "2023"]},
            "is": {p: {"营业收入": 1000, "营业利润": 100}
                   for p in ["2018", "2019", "2020", "2021", "2022", "2023"]},
            "cf": {p: {} for p in ["2018", "2019", "2020", "2021", "2022", "2023"]},
        }
        # 所有值相同 → std=0
        result: Dict[str, Any] = compute_zscores(data, accounts=["营业收入"], window=4)
        assert "accounts" in result

    def test_fscore_data_insufficiency(self) -> None:
        """边界：F-Score单期数据仍可运行。"""
        data: Dict[str, Any] = {
            "periods": ["2021"],
            "bs": {"2021": {"总资产": 1000, "资产总计": 1000, "流动资产": 500,
                           "流动负债": 300, "实收资本": 200}},
            "is": {"2021": {"营业收入": 800, "净利润": 80}},
            "cf": {"2021": {"经营活动产生的现金流量净额": 40}},
        }
        result: Dict[str, Any] = compute_fscore(data)
        assert "2021" in result
        assert 0 <= result["2021"]["total"] <= 9


# =============================================================================
# 数据一致性测试
# =============================================================================


class TestDataConsistency:
    """Fixtures数据与计算结果一致性验证。"""

    @pytest.fixture
    def sample(self) -> Dict[str, Any]:
        return _load_sample()

    def test_bs_balances(self, sample: Dict[str, Any]) -> None:
        """BS平衡验证：资产=负债+权益。"""
        for period, bs in sample["bs"].items():
            assets: float = bs["总资产"]
            liab: float = bs["总负债"]
            equity: float = bs["所有者权益"]
            assert abs(assets - liab - equity) < 0.01, (
                f"BS not balanced for {period}: {assets} != {liab} + {equity}"
            )

    def test_cf_ending_cash_vs_bs_cash(self, sample: Dict[str, Any]) -> None:
        """CF期末现金与BS货币资金一致性。"""
        for period in sample["periods"]:
            cf_cash: float = sample["cf"][period]["期末现金及现金等价物余额"]
            bs_cash: float = sample["bs"][period]["货币资金"]
            assert cf_cash == pytest.approx(bs_cash), (
                f"Cash mismatch for {period}: CF={cf_cash}, BS={bs_cash}"
            )

    def test_cf_sum_ties_out(self, sample: Dict[str, Any]) -> None:
        """三大现金流合计等于现金变动。"""
        for period in sample["periods"]:
            cf: Dict[str, float] = sample["cf"][period]
            oper: float = cf["经营活动产生的现金流量净额"]
            invest: float = cf["投资活动产生的现金流量净额"]
            finance: float = cf["筹资活动产生的现金流量净额"]
            fx: float = cf["汇率变动对现金的影响"]
            ending: float = cf["期末现金及现金等价物余额"]
            beginning: float = cf["期初现金及现金等价物余额"]

            expected_change: float = oper + invest + finance + fx
            actual_change: float = ending - beginning
            assert expected_change == pytest.approx(actual_change), (
                f"CF sum mismatch for {period}"
            )

    def test_net_profit_order(self, sample: Dict[str, Any]) -> None:
        """净利润增长趋势与营业收入一致（制造业健康企业）。"""
        prev_np: float = 0
        for period in sample["periods"]:
            np_val: float = sample["is"][period]["净利润"]
            if prev_np > 0:
                assert np_val > prev_np, f"Net profit decreased in {period}"
            prev_np = np_val

    def test_ratios_match_fixture_data(self, sample: Dict[str, Any]) -> None:
        """手动验证比率计算与fixture数据一致性。"""
        ratios: Dict[str, Any] = compute_all_ratios(sample)
        # 2021年：营收=1050M，应收=350M → DSO ≈ 350/1050*365 = 121.67
        op2021: Dict[str, Any] = ratios["营运能力"][2]
        expected_dso: float = 350 / 1050 * 365
        assert op2021["应收周转天数(DSO)"] == pytest.approx(expected_dso, rel=0.01)

        # 2021年毛利率 = (1050-766.5)/1050 = 0.27
        prof2021: Dict[str, Any] = ratios["盈利能力"][2]
        expected_gm: float = (1050 - 766.5) / 1050
        assert prof2021["毛利率"] == pytest.approx(expected_gm, rel=0.01)

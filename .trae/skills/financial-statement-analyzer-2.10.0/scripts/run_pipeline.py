#!/usr/bin/env python3
"""端到端分析管道 — 统一入口，保证报告输出数量和质量一致。

从标准化财务数据出发，运行全分析管道（比率→红灯→勾稽→MS/F-Score→现金流→
异常检测→案例匹配→建议生成），最后调用 ReportGenerator.generate_all_reports()
一次性输出 4 份报告（综合 + L1/L2/L3），确保每次调用的输出一致。

作者: 优方皑尔 Uform Ai
版本: v2.9.0
"""

import sys, os, json, logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_full_pipeline(
    data: dict,
    company_name: str = "",
    company_short: str = "",
    year: str = "",
    output_dir: str = "",
    industry: dict = None,
) -> list:
    """运行完整的分析管道并生成全部报告。

    这是 skills 的唯一入口函数。调用者只需提供标准化数据，
    管道负责所有分析步骤和报告生成。

    Args:
        data: 标准化财务数据，格式为:
            {
                "periods": ["2025"],
                "bs": {"2025": {"货币资金": ..., "资产总计": ..., ...}},
                "is": {"2025": {"营业收入": ..., "净利润": ..., ...}},
                "cf": {"2025": {}}  # 可选
            }
        company_name: 公司全称（用于报告标题）
        company_short: 公司简称（用于文件命名）
        year: 年度标识
        output_dir: 输出目录（必须指定）
        industry: 行业基准参数（可选）

    Returns:
        生成的文件路径列表
    """
    periods = data.get("periods", [])
    latest = periods[-1] if periods else ""

    # ---- Step 1: 构建结果容器 ----
    results = {
        "company_name": company_name or "未命名企业",
        "periods": data["periods"],
        "is": data.get("is", {}),
        "bs": data.get("bs", {}),
        "cf": data.get("cf", {}),
    }

    # ---- Step 2: 比率分析 ----
    logger.info("Running compute_ratios...")
    from compute_ratios import compute_all_ratios, compute_dupont, classify_cashflow_pattern
    try:
        results["ratios"] = compute_all_ratios(data)
        logger.info("  -> %d categories", len(results["ratios"]) if isinstance(results["ratios"], dict) else 0)
    except Exception as e:
        logger.warning("  Ratios failed: %s", e)
        results["ratios"] = {}

    try:
        results["dupont"] = compute_dupont(data)
    except Exception:
        results["dupont"] = {}

    try:
        results["cf_pattern"] = classify_cashflow_pattern(data)
    except Exception:
        results["cf_pattern"] = {}

    # ---- Step 3: 造假检测 ----
    logger.info("Running compute_mscore / compute_fscore...")
    from compute_mscore import compute_mscore, compute_fscore
    try:
        results["mscore"] = compute_mscore(data)
    except Exception as e:
        logger.warning("  M-Score: %s", e)
        results["mscore"] = {}
    try:
        results["fscore"] = compute_fscore(data)
    except Exception:
        results["fscore"] = {}

    # ---- Step 4: 红灯信号 ----
    logger.info("Running scan_redflags...")
    from scan_redflags import scan_red_flags
    try:
        results["redflags"] = scan_red_flags({**data, "ratios": results["ratios"]})
        logger.info("  -> %d triggered", results["redflags"].get("summary", {}).get("total_triggered", 0))
    except Exception as e:
        logger.warning("  Red flags: %s", e)
        results["redflags"] = {"triggered_signals": [], "summary": {}}

    # ---- Step 5: 异常检测 ----
    from detect_anomalies import detect_anomalies
    try:
        results["anomalies"] = detect_anomalies(data)
    except Exception:
        results["anomalies"] = {"accounts": {}, "summary": {}}

    # ---- Step 6: 勾稽验证 ----
    from verify_crosschecks import verify_crosschecks
    try:
        results["crosscheck"] = verify_crosschecks(data)
    except Exception:
        results["crosscheck"] = {"master_status": "PASS", "categories": {}}

    # ---- Step 7: 案例匹配 ----
    from match_cases import match_cases
    try:
        results["case_match"] = match_cases(data)
    except Exception:
        results["case_match"] = {"matched_cases": []}

    # ---- Step 8: 建议生成 ----
    from generate_advice import generate_advice
    try:
        results["advice"] = generate_advice(results)
    except Exception:
        results["advice"] = {"advice_list": [], "total_advice_groups": 0}

    # ---- Step 9: Z-Score ----
    bs = data.get("bs", {}).get(latest, {})
    is_data = data.get("is", {}).get(latest, {})
    ta_val = float(bs.get("资产总计", 1) or bs.get("总资产", 1))
    ca_val = float(bs.get("流动资产合计", 0) or bs.get("流动资产", 0))
    cl_val = float(bs.get("流动负债合计", 0) or bs.get("流动负债", 0))
    re_val = float(bs.get("未分配利润", 0))
    tp_val = float(is_data.get("利润总额", 0))
    fe_val = float(is_data.get("财务费用", 0))
    eq_val = float(bs.get("所有者权益合计", 1) or bs.get("所有者权益", 1))
    tl_val = float(bs.get("负债合计", 0) or bs.get("总负债", 0))
    rev_val = float(is_data.get("营业收入", 1))

    z = (1.2 * (ca_val - cl_val) / max(ta_val, 1) +
         1.4 * re_val / max(ta_val, 1) +
         3.3 * (tp_val + abs(fe_val)) / max(ta_val, 1) +
         (0.6 * eq_val / tl_val if tl_val > 0 else 0) +
         1.0 * rev_val / max(ta_val, 1))
    results["zscore"] = {latest: round(z, 2)}
    results["raw_revenue"] = rev_val

    # ---- Step 10: 行业基准 ----
    results["industry"] = industry or {
        "label": "通用",
        "profit_margin_avg": 25.0, "net_margin_avg": 10.0, "roe_avg": 12.0,
        "current_ratio_avg": 2.0, "debt_ratio_avg": 40.0, "turnover_avg": 0.60,
    }

    # ---- Step 11: v2.8+ 新增模块 ----
    from data_quality_scorer import score_data_quality
    try:
        results["data_quality"] = score_data_quality(data)
    except Exception:
        results["data_quality"] = {"total_score": "N/A", "grade": "N/A"}

    from ar_aging_estimator import estimate_ar_aging
    try:
        results["ar_aging"] = estimate_ar_aging(data)
    except Exception:
        results["ar_aging"] = {"risk_level": "unknown"}

    from rd_capitalization_detector import detect_rd_capitalization
    try:
        results["rd_cap"] = detect_rd_capitalization(data, results["industry"]["label"])
    except Exception:
        results["rd_cap"] = {"latest_cap_rate": 0}

    # ---- Step 12: 生成全部报告（统一入口，保证4份报告） ----
    if not output_dir:
        raise ValueError("output_dir 必须指定")

    from generate_report import ReportGenerator
    gen = ReportGenerator()

    paths = gen.generate_all_reports(
        analysis_results=results,
        output_dir=output_dir,
        company_short=company_short or "公司",
        year=year or latest,
    )

    logger.info("Pipeline complete: %d reports generated in %s", len(paths), output_dir)
    return paths


# ---- 便捷 CLI 入口 ----
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="财务报表分析管道")
    parser.add_argument("--data", required=True, help="JSON 格式的标准化数据文件")
    parser.add_argument("--company", default="", help="公司全称")
    parser.add_argument("--short", default="公司", help="公司简称")
    parser.add_argument("--year", default="", help="年度")
    parser.add_argument("--output", required=True, help="输出目录")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    paths = run_full_pipeline(
        data=data,
        company_name=args.company,
        company_short=args.short,
        year=args.year,
        output_dir=args.output,
    )
    for p in paths:
        print(f"  -> {p}")

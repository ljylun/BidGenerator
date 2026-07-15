#!/usr/bin/env python3
"""案例模式匹配模块 — 余弦相似度匹配已知财务造假案例。

基于案例特征向量库（case-library.json），计算当前企业与已知案例的
余弦相似度，返回Top-N匹配案例。

作者: 优方皑尔 Uform Ai
版本: v1.0.0
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_DEFAULT_CASES_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "references",
    "case-library.json",
)


class CaseMatcher:
    """案例模式匹配引擎。

    使用余弦相似度 + P0特征重叠加权匹配已知财务造假案例。
    """

    def __init__(self, cases_path: Optional[str] = None):
        """初始化匹配器。

        Args:
            cases_path: 案例库JSON文件路径。
        """
        self._cases_path: str = cases_path or _DEFAULT_CASES_PATH
        self._cases: List[Dict[str, Any]] = []
        self._feature_weights: Dict[str, float] = {}
        self._p0_boost: float = 0.3
        self._thresholds: Dict[str, float] = {
            "high": 0.70, "medium": 0.50, "low": 0.30,
        }
        self._load_cases()

    def _load_cases(self) -> None:
        """加载案例库。"""
        try:
            with open(self._cases_path, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
            self._cases = config.get("cases", [])
            self._feature_weights = config.get("feature_weights", {})
            self._p0_boost = config.get("p0_feature_boost", 0.3)
            self._thresholds = config.get("matching_threshold", self._thresholds)
            logger.info(
                "Loaded %d cases with %d features",
                len(self._cases),
                len(self._feature_weights),
            )
        except Exception as exc:
            logger.error("Failed to load case library: %s", exc)
            self._cases = []
            self._feature_weights = {}

    def match(
        self,
        data: Dict[str, Any],
        top_n: int = 3,
    ) -> Dict[str, Any]:
        """执行案例匹配。

        Args:
            data: 标准化财务数据 + 计算得出的特征向量。
            top_n: 返回前N个匹配案例。

        Returns:
            dict: 匹配结果。
        """
        # 计算当前企业的特征向量
        company_features: Dict[str, float] = self._extract_features(data)

        if not company_features or not self._cases:
            return {
                "matched_cases": [],
                "total_cases": len(self._cases),
                "company_features": company_features,
                "note": "无法提取特征或无案例库",
            }

        # 计算与每个案例的相似度
        similarities: List[Dict[str, Any]] = []
        for case in self._cases:
            case_features: Dict[str, float] = case.get("features", {})
            p0_features: List[str] = case.get("p0_features", [])
            similarity: float = self._cosine_similarity(
                company_features, case_features, p0_features
            )
            similarities.append({
                "case_id": case.get("id", ""),
                "case_name": case.get("name", ""),
                "case_summary": case.get("summary", ""),
                "fraud_type": case.get("fraud_type", ""),
                "similarity": round(similarity * 100, 1),
                "shared_features": self._get_shared_features(
                    company_features, case_features
                ),
            })

        # 按相似度降序排列
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        # 分类
        matched: List[Dict[str, Any]] = []
        for s in similarities[:top_n]:
            if s["similarity"] >= self._thresholds["low"] * 100:
                matched.append(s)

        # 如果没有高相似度匹配
        if not matched:
            matched = [{
                "case_id": "NONE",
                "case_name": "无匹配",
                "case_summary": "未匹配到高度相似的已知案例",
                "fraud_type": "",
                "similarity": 0,
                "shared_features": [],
            }]

        return {
            "matched_cases": matched,
            "all_similarities": similarities,
            "total_cases": len(self._cases),
            "company_features": company_features,
        }

    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """从财务数据提取特征向量。

        Args:
            data: 标准化财务数据。

        Returns:
            dict: 特征字典。
        """
        features: Dict[str, float] = {}
        periods: List[str] = data.get("periods", [])
        if not periods:
            return features

        latest: str = periods[-1]
        bs: Dict[str, float] = data["bs"].get(latest, {})
        iso: Dict[str, float] = data["is"].get(latest, {})
        cf: Dict[str, float] = data["cf"].get(latest, {})

        total_assets: float = bs.get("总资产", bs.get("资产总计", 1))
        total_liab: float = bs.get("总负债", bs.get("负债总计", 0))
        equity: float = bs.get("所有者权益", bs.get("所有者权益总计", 1))
        revenue: float = iso.get("营业收入", 1)
        net_income: float = iso.get("净利润", 0)
        operating_cf: float = cf.get("经营活动产生的现金流量净额", 0)
        cash_val: float = bs.get("货币资金", 0)
        receivables: float = bs.get("应收账款", 0)
        inventory: float = bs.get("存货", 0)

        # 利息收入估算
        interest_income: float = abs(iso.get("财务费用", 0)) * 0.3

        features["cash_to_total_assets"] = cash_val / total_assets
        features["interest_income_to_cash"] = (
            interest_income / cash_val if cash_val else 0
        )
        features["interest_bearing_debt_to_total_assets"] = (
            (bs.get("短期借款", 0) + bs.get("长期借款", 0) + bs.get("应付债券", 0))
            / total_assets
        )

        # 毛利率vs行业
        gross: float = (revenue - iso.get("营业成本", 0)) / revenue if revenue else 0
        features["gross_margin_vs_industry"] = gross / 0.25  # 以默认行业均值为基准

        features["cfo_to_net_income"] = (
            operating_cf / net_income if net_income else 0
        )

        # 应收增速/收入增速（简化用绝对值比）
        features["receivable_growth_to_revenue_growth"] = (
            receivables / revenue * 2 if revenue else 0
        )
        features["inventory_growth_to_cost_growth"] = (
            inventory / iso.get("营业成本", 1) * 2 if iso.get("营业成本") else 0
        )

        # M-Score
        mscore_results: Dict[str, Any] = data.get("mscore", {})
        mscore_val: float = -3.0  # 默认正常
        for p, m in mscore_results.items():
            if m.get("value") is not None:
                mscore_val = m["value"]
        features["mscore"] = mscore_val

        # 商誉
        features["goodwill_to_equity"] = bs.get("商誉", 0) / equity if equity else 0

        # 研发资本化率
        rd_expense: float = iso.get("研发费用", 0)
        dev_expenditure: float = bs.get("开发支出", 0)
        features["rd_capitalization_rate"] = (
            dev_expenditure / (rd_expense + dev_expenditure)
            if (rd_expense + dev_expenditure)
            else 0
        )

        return features

    def _cosine_similarity(
        self,
        company: Dict[str, float],
        case: Dict[str, float],
        p0_features: List[str],
    ) -> float:
        """计算加权余弦相似度。

        Args:
            company: 企业特征向量。
            case: 案例特征向量。
            p0_features: 案例的P0特征（计算额外权重）。

        Returns:
            float: 相似度 (0.0 - 1.0+)。
        """
        # 获取所有特征键
        all_keys: List[str] = list(set(list(company.keys()) + list(case.keys())))

        vec_a: List[float] = []
        vec_b: List[float] = []
        weights: List[float] = []

        for key in all_keys:
            a_val: float = company.get(key, 0)
            b_val: float = case.get(key, 0)
            vec_a.append(a_val)
            vec_b.append(b_val)
            w: float = self._feature_weights.get(key, 0.1)
            if key in p0_features:
                w *= (1 + self._p0_boost)
            weights.append(w)

        vec_a_np: np.ndarray = np.array(vec_a) * np.array(weights)
        vec_b_np: np.ndarray = np.array(vec_b) * np.array(weights)

        norm_a: float = float(np.linalg.norm(vec_a_np))
        norm_b: float = float(np.linalg.norm(vec_b_np))

        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.0

        return float(np.dot(vec_a_np, vec_b_np) / (norm_a * norm_b))

    @staticmethod
    def _get_shared_features(
        company: Dict[str, float],
        case: Dict[str, float],
    ) -> List[str]:
        """识别共同特征。

        Args:
            company: 企业特征。
            case: 案例特征。

        Returns:
            list: 共同特征名称列表。
        """
        shared: List[str] = []
        feature_labels: Dict[str, str] = {
            "cash_to_total_assets": "货币资金/总资产偏高",
            "interest_income_to_cash": "利息收入/货币偏低",
            "cfo_to_net_income": "经营CF/净利偏低",
            "receivable_growth_to_revenue_growth": "应收增速>收入增速",
            "inventory_growth_to_cost_growth": "存货增速>成本增速",
            "mscore": "M-Score偏高",
            "rd_capitalization_rate": "研发资本化率偏高",
            "goodwill_to_equity": "商誉占比偏高",
            "gross_margin_vs_industry": "毛利率偏离行业",
        }

        for key in case:
            if key in company and abs(company[key] - case[key]) < 0.5:
                label: str = feature_labels.get(key, key)
                shared.append(label)

        return shared[:5]


def match_cases(
    data: Dict[str, Any],
    cases_path: Optional[str] = None,
    top_n: int = 3,
) -> Dict[str, Any]:
    """便捷函数：案例模式匹配。

    Args:
        data: 标准化财务数据。
        cases_path: 案例库路径。
        top_n: 返回前N个匹配。

    Returns:
        dict: 匹配结果。
    """
    matcher: CaseMatcher = CaseMatcher(cases_path)
    return matcher.match(data, top_n)

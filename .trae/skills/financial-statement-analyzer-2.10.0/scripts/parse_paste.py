#!/usr/bin/env python3
"""粘贴数据解析模块 — 支持用户粘贴文本/制表符分隔/CSV格式的财务数据。

自动识别数据结构，提取三表（BS/IS/CF）数值。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import io
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class PasteParseError(Exception):
    """粘贴数据解析异常。"""


# 三表关键词识别模式
_BALANCE_SHEET_KEYWORDS: List[str] = [
    "资产负债表", "资产总计", "负债总计", "所有者权益",
    "流动资产", "非流动资产", "流动负债", "非流动负债",
]

_INCOME_STATEMENT_KEYWORDS: List[str] = [
    "利润表", "营业收入", "营业成本", "净利润", "利润总额",
    "营业利润", "销售费用", "管理费用",
]

_CASH_FLOW_KEYWORDS: List[str] = [
    "现金流量表", "经营活动产生", "投资活动产生", "筹资活动产生",
    "现金及现金等价物", "期初现金", "期末现金",
]


def parse_pasted_text(text: str) -> Dict[str, Any]:
    """解析用户粘贴的财务数据文本。

    支持格式:
        1. 制表符分隔的表格文本
        2. CSV格式
        3. 带标题的区块式文本

    Args:
        text: 用户粘贴的原始文本。

    Returns:
        dict: 包含三表解析结果的字典:
            {
                "balance_sheet": pd.DataFrame,
                "income_statement": pd.DataFrame,
                "cash_flow": pd.DataFrame,
                "metadata": {...}
            }

    Raises:
        PasteParseError: 文本中无法提取有效财务数据。
    """
    text = text.strip()
    if not text:
        raise PasteParseError("输入文本为空，无法解析。")

    # 尝试识别分隔符
    delimiter: str = _detect_delimiter(text)
    blocks: List[str] = _split_into_blocks(text)

    logger.info("Detected delimiter: %r, blocks: %d", delimiter, len(blocks))

    bs_df: Optional[pd.DataFrame] = None
    is_df: Optional[pd.DataFrame] = None
    cf_df: Optional[pd.DataFrame] = None

    for block in blocks:
        df: Optional[pd.DataFrame] = _parse_block_to_dataframe(block, delimiter)
        if df is None or df.empty:
            continue

        label: str = _classify_block(df)
        if label == "balance_sheet" and bs_df is None:
            bs_df = df
        elif label == "income_statement" and is_df is None:
            is_df = df
        elif label == "cash_flow" and cf_df is None:
            cf_df = df

    if bs_df is None and is_df is None and cf_df is None:
        raise PasteParseError(
            "未能从粘贴文本中识别出任何财务报表数据。"
            "请确认文本包含资产负债表、利润表或现金流量表中的至少一个。"
        )

    data_quality: Dict[str, Any] = _assess_data_quality(bs_df, is_df, cf_df)

    return {
        "balance_sheet": bs_df,
        "income_statement": is_df,
        "cash_flow": cf_df,
        "metadata": {
            "source_format": "paste",
            "extraction_method": "direct",
            "extraction_confidence": data_quality.get("credibility", 50.0),
            "warnings": [],
            "audit_report_detected": False,
            "delimiter": delimiter,
            "total_blocks": len(blocks),
            "data_quality": data_quality,
        },
    }


def _detect_delimiter(text: str) -> str:
    """自动检测文本分隔符。

    Args:
        text: 原始文本。

    Returns:
        str: 检测到的分隔符 ('\t', ',' 或 r'\s{2,}')。
    """
    lines: List[str] = text.split("\n")[:20]
    tab_count: int = sum(line.count("\t") for line in lines)
    comma_count: int = sum(line.count(",") for line in lines)

    if tab_count > comma_count and tab_count > len(lines):
        return "\t"
    if comma_count > tab_count and comma_count > len(lines):
        return ","
    return r"\s{2,}"


def _split_into_blocks(text: str) -> List[str]:
    """将文本按空行或关键词分割为数据块。

    Args:
        text: 原始文本。

    Returns:
        分割后的文本块列表。
    """
    # 先用双换行分割
    blocks: List[str] = re.split(r"\n\s*\n", text)
    # 过滤掉过短的块（可能是噪声）
    blocks = [b.strip() for b in blocks if len(b.strip().split("\n")) >= 2]
    # 如果只有一个大块，尝试按关键词分割
    if len(blocks) == 1:
        split_patterns: List[str] = [
            r"(?=资产负债表)", r"(?=利润表)", r"(?=现金流量表)",
            r"(?=Balance Sheet)", r"(?=Income Statement)", r"(?=Cash Flow)",
        ]
        for pat in split_patterns:
            parts: List[str] = re.split(pat, blocks[0])
            if len(parts) > 1:
                blocks = [p.strip() for p in parts if p.strip()]
                break
    return blocks


def _parse_block_to_dataframe(block: str, delimiter: str) -> Optional[pd.DataFrame]:
    """将文本块解析为DataFrame。

    Args:
        block: 文本块。
        delimiter: 分隔符。

    Returns:
        pd.DataFrame 或 None。
    """
    try:
        df: pd.DataFrame = pd.read_csv(
            io.StringIO(block),
            sep=delimiter,
            header=None,
            engine="python",
            on_bad_lines="skip",
        )
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty or df.shape[1] < 2:
            return None

        # 尝试用第一行做表头
        first_row: pd.Series = df.iloc[0]
        numeric_count: int = sum(
            1 for v in first_row[1:]
            if _is_numeric(str(v))
        )
        if numeric_count >= len(first_row) // 2:
            # 第一行可能是数值，说明没有独立表头
            df.columns = ["科目"] + [f"期间{i+1}" for i in range(df.shape[1] - 1)]
        else:
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
            df.columns = [str(c).strip() for c in df.columns]

        return df
    except Exception:
        return None


def _classify_block(df: pd.DataFrame) -> str:
    """通过关键词分类DataFrame属于哪个报表。

    Args:
        df: 数据DataFrame。

    Returns:
        str: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'unknown'
    """
    first_col_text: str = " ".join(
        str(v).strip() for v in df.iloc[:, 0].dropna().head(30)
    )

    bs_score: int = sum(1 for kw in _BALANCE_SHEET_KEYWORDS if kw in first_col_text)
    is_score: int = sum(1 for kw in _INCOME_STATEMENT_KEYWORDS if kw in first_col_text)
    cf_score: int = sum(1 for kw in _CASH_FLOW_KEYWORDS if kw in first_col_text)

    scores: List[Tuple[str, int]] = [
        ("balance_sheet", bs_score),
        ("income_statement", is_score),
        ("cash_flow", cf_score),
    ]
    scores.sort(key=lambda x: x[1], reverse=True)

    if scores[0][1] > 0:
        return scores[0][0]
    return "unknown"


def _is_numeric(text: str) -> bool:
    """判断文本是否为数值。

    Args:
        text: 文本。

    Returns:
        是否为数值。
    """
    text = text.strip().replace(",", "").replace(" ", "").replace("%", "")
    try:
        float(text)
        return True
    except ValueError:
        return False


def _assess_data_quality(
    bs_df: Optional[pd.DataFrame],
    is_df: Optional[pd.DataFrame],
    cf_df: Optional[pd.DataFrame],
) -> Dict[str, Any]:
    """评估解析数据质量。

    Args:
        bs_df: 资产负债表DataFrame。
        is_df: 利润表DataFrame。
        cf_df: 现金流量表DataFrame。

    Returns:
        数据质量评估字典。
    """
    available_tables: int = sum(1 for df in [bs_df, is_df, cf_df] if df is not None)
    credibility: float = 100.0

    if cf_df is None:
        credibility -= 25.0
    if available_tables < 3:
        credibility -= 10.0

    # 检查数据期数
    min_periods: int = 99
    for df in [bs_df, is_df, cf_df]:
        if df is not None:
            num_cols: int = df.shape[1] - 1  # 减去科目列
            min_periods = min(min_periods, num_cols)

    if min_periods < 2:
        credibility -= 15.0

    return {
        "available_tables": available_tables,
        "credibility": max(credibility, 0.0),
        "min_periods": min_periods,
        "has_bs": bs_df is not None,
        "has_is": is_df is not None,
        "has_cf": cf_df is not None,
    }

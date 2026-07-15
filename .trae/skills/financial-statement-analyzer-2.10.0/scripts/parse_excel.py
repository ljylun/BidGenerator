#!/usr/bin/env python3
"""Excel报表解析模块 — 使用 openpyxl + pandas 解析企业财务报表。

支持 .xlsx / .xls 格式，自动识别资产负债表、利润表、现金流量表。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class ExcelParseError(Exception):
    """Excel解析异常。"""


def parse_excel(
    filepath: str,
    sheet_names: Optional[List[str]] = None,
    header_row: int = 0,
) -> Dict[str, Any]:
    """解析Excel财务报表文件。

    Args:
        filepath: Excel文件路径。
        sheet_names: 需要解析的工作表名称列表。默认自动识别所有工作表。
        header_row: 表头所在行号（0-based）。

    Returns:
        dict: 包含三表数据的字典，结构为:
            {
                "balance_sheet": pd.DataFrame,
                "income_statement": pd.DataFrame,
                "cash_flow": pd.DataFrame,
                "metadata": {...}
            }

    Raises:
        ExcelParseError: 文件格式不正确或数据缺失。
    """
    try:
        xls = pd.ExcelFile(filepath)
    except Exception as exc:
        raise ExcelParseError(f"无法打开Excel文件 '{filepath}': {exc}") from exc

    available_sheets: List[str] = xls.sheet_names
    logger.info("Available sheets: %s", available_sheets)

    sheets_to_parse: List[str] = sheet_names or available_sheets
    parsed_data: Dict[str, pd.DataFrame] = {}

    for sheet in sheets_to_parse:
        if sheet not in available_sheets:
            logger.warning("Sheet '%s' not found, skipping.", sheet)
            continue
        df: pd.DataFrame = pd.read_excel(filepath, sheet_name=sheet, header=header_row)
        df = _clean_dataframe(df)
        parsed_data[sheet] = df

    result: Dict[str, Any] = {
        "balance_sheet": _identify_and_extract(parsed_data, "balance_sheet"),
        "income_statement": _identify_and_extract(parsed_data, "income_statement"),
        "cash_flow": _identify_and_extract(parsed_data, "cash_flow"),
        "metadata": {
            "source": filepath,
            "source_format": "excel",
            "extraction_method": "direct",
            "extraction_confidence": 100.0,
            "warnings": [],
            "audit_report_detected": False,
            "total_sheets": len(available_sheets),
            "parsed_sheets": len(parsed_data),
        },
    }
    return result


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """清洗DataFrame：去除全空行/列，填充合并单元格。

    Args:
        df: 原始DataFrame。

    Returns:
        清洗后的DataFrame。
    """
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df = df.ffill().fillna(0)
    # 清理列名
    df.columns = [str(col).strip() for col in df.columns]
    return df


def _identify_and_extract(
    data: Dict[str, pd.DataFrame],
    table_type: str,
) -> Optional[pd.DataFrame]:
    """通过关键词自动识别并提取指定报表。

    Args:
        data: 所有已解析的工作表数据。
        table_type: 报表类型 ('balance_sheet', 'income_statement', 'cash_flow')。

    Returns:
        匹配的DataFrame，若未识别则返回None。
    """
    keywords: Dict[str, List[str]] = {
        "balance_sheet": [
            "资产负债表", "balance sheet", "资产总计", "负债总计",
            "所有者权益", "流动负债", "非流动资产",
        ],
        "income_statement": [
            "利润表", "income statement", "营业收入", "营业成本",
            "净利润", "营业利润", "综合收益",
        ],
        "cash_flow": [
            "现金流量表", "cash flow", "经营活动产生", "投资活动产生",
            "筹资活动产生", "现金及现金等价物",
        ],
    }

    search_terms: List[str] = keywords.get(table_type, [])
    for sheet_name, df in data.items():
        sheet_lower: str = sheet_name.lower()
        if any(term in sheet_lower for term in search_terms[:1]):
            logger.info("Table '%s' matched by sheet name: '%s'", table_type, sheet_name)
            return df

    for sheet_name, df in data.items():
        first_col_text: str = " ".join(
            str(v) for v in df.iloc[:, 0].dropna().head(20)
        ).lower()
        if any(term in first_col_text for term in search_terms):
            logger.info("Table '%s' matched by content in sheet: '%s'", table_type, sheet_name)
            return df

    logger.warning("Could not identify '%s' in any sheet.", table_type)
    return None


def extract_numeric_timeseries(
    df: pd.DataFrame,
    item_column: int = 0,
    value_columns: Optional[List[int]] = None,
) -> Dict[str, Dict[str, float]]:
    """从报表DataFrame提取数值时间序列。

    Args:
        df: 报表DataFrame，首列应为科目名称。
        item_column: 科目名称所在列索引。
        value_columns: 数值列索引列表，默认自动识别所有数值列。

    Returns:
        dict: {科目名称: {期间: 数值}} 格式的时间序列字典。
    """
    if df is None:
        return {}

    if value_columns is None:
        value_columns = [
            i for i, col in enumerate(df.columns)
            if i != item_column and pd.api.types.is_numeric_dtype(df[col])
        ]

    result: Dict[str, Dict[str, float]] = {}
    for _, row in df.iterrows():
        item_name: str = str(row.iloc[item_column]).strip()
        if not item_name or item_name == "nan":
            continue
        values: Dict[str, float] = {}
        for col_idx in value_columns:
            period_name: str = str(df.columns[col_idx])
            raw_val: Any = row.iloc[col_idx]
            try:
                values[period_name] = float(raw_val) if not pd.isna(raw_val) else 0.0
            except (ValueError, TypeError):
                values[period_name] = 0.0
        result[item_name] = values

    return result

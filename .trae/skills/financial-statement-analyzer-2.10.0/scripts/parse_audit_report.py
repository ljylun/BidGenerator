#!/usr/bin/env python3
"""审计报告专项解析模块 — 识别审计报告结构并提取财务报表段落。

支持从 PDF 文本/DOCX 文本中检测审计报告特征，定位并提取财务报表段。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 审计报告结构关键词
# ---------------------------------------------------------------------------

_AUDIT_REPORT_KEYWORDS: List[str] = [
    # 中文
    "审计报告", "审计意见", "独立审计", "审计师",
    "注册会计师", "审计准则", "审计程序", "审计证据",
    "审计风险", "关键审计事项", "审计结论",
    # 英文
    "auditor's report", "independent auditor", "audit opinion",
    "audit report", "independent audit", "unqualified opinion",
    "qualified opinion", "adverse opinion", "disclaimer of opinion",
    "key audit matters", "audit procedures",
]

_FINANCIAL_STATEMENT_SECTION_KEYWORDS: List[str] = [
    # 中文
    "财务报表", "资产负债表", "利润表", "现金流量表",
    "所有者权益变动表", "合并资产负债表", "合并利润表",
    "合并现金流量表",
    # 英文
    "balance sheet", "income statement", "statement of cash flows",
    "statement of financial position", "statement of comprehensive income",
    "statement of changes in equity", "consolidated financial statements",
]

_NOTES_SECTION_KEYWORDS: List[str] = [
    "会计报表附注", "财务报表附注", "附注",
    "notes to the financial statements", "notes to financial statements",
    "accounting policies", "significant accounting",
]


def is_audit_report(text: str) -> bool:
    """判断文本是否为审计报告。

    通过关键词匹配判断文本是否具备审计报告的结构特征。
    检测标准：至少命中 2 个审计关键词 + 1 个财务报表段关键词。

    Args:
        text: 待检测的文本。

    Returns:
        bool: True 表示该文本来自审计报告。
    """
    if not text or not text.strip():
        return False

    text_lower: str = text.lower()

    # 审计关键词命中数
    audit_hits: int = sum(
        1 for kw in _AUDIT_REPORT_KEYWORDS if kw.lower() in text_lower
    )

    # 财务报表段关键词命中数
    fs_hits: int = sum(
        1 for kw in _FINANCIAL_STATEMENT_SECTION_KEYWORDS if kw.lower() in text_lower
    )

    # 判定：至少 2 个审计关键词 + 1 个财务报表关键词
    is_audit: bool = audit_hits >= 2 and fs_hits >= 1

    if is_audit:
        logger.info(
            "Detected audit report: audit_hits=%d, fs_hits=%d",
            audit_hits, fs_hits,
        )

    return is_audit


def extract_financial_sections(text: str) -> List[str]:
    """从审计报告全文提取财务报表相关段落。

    策略：
        1. 按财务报表段关键词分割文本
        2. 提取每个关键词后的段落，到下一个关键词或附注开始为止
        3. 返回可能包含三表的文本段落列表

    Args:
        text: 审计报告全文。

    Returns:
        List[str]: 财务报表相关段落列表。
    """
    if not text or not text.strip():
        return []

    sections: List[str] = []

    # 找到财务报表段的起始位置
    text_lower: str = text.lower()

    # 找到第一个财务报表段关键词的位置
    first_fs_pos: int = -1
    for kw in _FINANCIAL_STATEMENT_SECTION_KEYWORDS:
        pos: int = text_lower.find(kw.lower())
        if pos >= 0 and (first_fs_pos < 0 or pos < first_fs_pos):
            first_fs_pos = pos

    if first_fs_pos < 0:
        # 未找到财务报表段，返回全文
        return [text]

    # 找到附注段的起始位置（截断点）
    notes_pos: int = len(text)
    for kw in _NOTES_SECTION_KEYWORDS:
        pos = text_lower.find(kw.lower(), first_fs_pos + 10)
        if pos >= 0 and pos < notes_pos:
            notes_pos = pos

    # 提取财务报表段
    fs_section: str = text[first_fs_pos:notes_pos].strip()
    if fs_section:
        sections.append(fs_section)

    # 尝试按三表标题进一步分割
    table_headers: Dict[str, List[str]] = {
        "balance_sheet": ["资产负债表", "合并资产负债表", "balance sheet"],
        "income_statement": ["利润表", "合并利润表", "income statement"],
        "cash_flow": ["现金流量表", "合并现金流量表", "cash flow"],
    }

    for table_type, headers in table_headers.items():
        for header in headers:
            pos = fs_section.lower().find(header.lower())
            if pos >= 0:
                # 提取此表标题到下一个表标题的段落
                sub_start: int = pos
                sub_end: int = len(fs_section)

                # 找下一个表格标题
                for other_type, other_headers in table_headers.items():
                    if other_type == table_type:
                        continue
                    for other_header in other_headers:
                        other_pos = fs_section.lower().find(
                            other_header.lower(), sub_start + len(header)
                        )
                        if other_pos >= 0 and other_pos < sub_end:
                            sub_end = other_pos

                sub_section: str = fs_section[sub_start:sub_end].strip()
                if len(sub_section) > 20:
                    sections.append(sub_section)
                break

    return sections


def parse_audit_report_from_pdf(filepath: str) -> Dict[str, Any]:
    """从 PDF 格式审计报告中解析财务报表。

    先使用 pdfplumber 提取全文和表格，然后识别审计报告结构，
    定位并提取财务报表段。

    Args:
        filepath: PDF 文件路径。

    Returns:
        dict: 统一输出格式，含三表 DataFrame + 审计报告元数据。
    """
    warnings: List[str] = []
    metadata: Dict[str, Any] = {
        "source": filepath,
        "source_format": "audit_report",
        "extraction_method": "hybrid",
        "extraction_confidence": 0.0,
        "warnings": [],
        "audit_report_detected": True,
    }

    bs_df: Optional[pd.DataFrame] = None
    is_df: Optional[pd.DataFrame] = None
    cf_df: Optional[pd.DataFrame] = None

    try:
        import pdfplumber
    except ImportError:
        warnings.append("pdfplumber 未安装。请执行: pip install pdfplumber>=0.10.0")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    try:
        with pdfplumber.open(filepath) as pdf:
            all_tables: List[List[List[Optional[str]]]] = []
            all_text: List[str] = []

            for page in pdf.pages:
                tables = page.extract_tables()
                for tbl in tables:
                    if tbl:
                        all_tables.append(tbl)
                text = page.extract_text()
                if text:
                    all_text.append(text)
    except Exception as exc:
        warnings.append(f"PDF 解析失败: {exc}")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    full_text: str = "\n".join(all_text)

    # 提取财务报表段落
    fs_sections: List[str] = extract_financial_sections(full_text)

    if not fs_sections:
        warnings.append("未能从审计报告中定位财务报表段落。")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    # 从表格中识别三表
    bs_table = _identify_pdf_table_by_type(all_tables, "balance_sheet")
    is_table = _identify_pdf_table_by_type(all_tables, "income_statement")
    cf_table = _identify_pdf_table_by_type(all_tables, "cash_flow")

    # 如果表格识别失败，尝试从财务段落的文本构建 DataFrame
    if bs_table is None and fs_sections:
        bs_df = _text_section_to_dataframe(fs_sections, "balance_sheet")
    elif bs_table is not None:
        bs_df = _raw_table_to_dataframe(bs_table)

    if is_table is None and fs_sections:
        is_df = _text_section_to_dataframe(fs_sections, "income_statement")
    elif is_table is not None:
        is_df = _raw_table_to_dataframe(is_table)

    if cf_table is None and fs_sections:
        cf_df = _text_section_to_dataframe(fs_sections, "cash_flow")
    elif cf_table is not None:
        cf_df = _raw_table_to_dataframe(cf_table)

    # 置信度评估
    found_count: int = sum(1 for df in [bs_df, is_df, cf_df] if df is not None)
    confidence: float = (found_count / 3.0) * 100.0
    if len(fs_sections) < 3:
        confidence = min(confidence, 75.0)
    metadata["extraction_confidence"] = round(confidence, 1)
    metadata["financial_sections_count"] = len(fs_sections)

    if found_count == 0:
        warnings.append(
            "审计报告中未能提取到完整的财务报表数据。"
            "审计报告中的报表可能以扫描图片形式存在，建议使用 OCR 模式。"
        )

    metadata["warnings"] = warnings

    return {
        "balance_sheet": bs_df,
        "income_statement": is_df,
        "cash_flow": cf_df,
        "metadata": metadata,
    }


def parse_audit_report_from_docx(filepath: str) -> Dict[str, Any]:
    """从 DOCX 格式审计报告中解析财务报表。

    使用 python-docx 提取表格和全文，识别审计报告结构。

    Args:
        filepath: .docx 文件路径。

    Returns:
        dict: 统一输出格式。
    """
    warnings: List[str] = []
    metadata: Dict[str, Any] = {
        "source": filepath,
        "source_format": "audit_report",
        "extraction_method": "hybrid",
        "extraction_confidence": 0.0,
        "warnings": [],
        "audit_report_detected": True,
    }

    bs_df: Optional[pd.DataFrame] = None
    is_df: Optional[pd.DataFrame] = None
    cf_df: Optional[pd.DataFrame] = None

    try:
        from docx import Document
    except ImportError:
        warnings.append("python-docx 未安装。请执行: pip install python-docx")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    try:
        doc = Document(filepath)
    except Exception as exc:
        warnings.append(f"无法打开 Word 文档: {exc}")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    # 提取全文
    full_text_parts: List[str] = []
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            full_text_parts.append(t)
    full_text: str = "\n".join(full_text_parts)

    # 提取财务报表段落
    fs_sections: List[str] = extract_financial_sections(full_text)

    # 使用 parse_docx 的表格解析能力
    try:
        from .parse_docx import parse_docx as _parse_docx
    except ImportError:
        _parse_docx = None

    if _parse_docx is not None:
        try:
            docx_result = _parse_docx(filepath)
            bs_df = docx_result.get("balance_sheet")
            is_df = docx_result.get("income_statement")
            cf_df = docx_result.get("cash_flow")
        except Exception as exc:
            logger.warning("parse_docx delegation failed: %s", exc)

    found_count: int = sum(1 for df in [bs_df, is_df, cf_df] if df is not None)
    confidence: float = (found_count / 3.0) * 100.0
    metadata["extraction_confidence"] = round(confidence, 1)
    metadata["financial_sections_count"] = len(fs_sections)

    if found_count == 0:
        warnings.append(
            "审计报告（DOCX）中未能提取到完整的财务报表数据。"
        )

    metadata["warnings"] = warnings

    return {
        "balance_sheet": bs_df,
        "income_statement": is_df,
        "cash_flow": cf_df,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------

# 三表关键词（与项目其他模块保持一致）
_BALANCE_KEYWORDS: List[str] = [
    "资产总计", "负债总计", "所有者权益", "流动负债",
    "流动资产", "非流动资产",
]

_INCOME_KEYWORDS: List[str] = [
    "营业收入", "营业成本", "净利润", "利润总额", "营业利润",
]

_CASHFLOW_KEYWORDS: List[str] = [
    "经营活动", "投资活动", "筹资活动", "现金及现金等价物",
]


def _identify_pdf_table_by_type(
    tables: List[List[List[Optional[str]]]],
    table_type: str,
) -> Optional[List[List[Optional[str]]]]:
    """通过关键词在 PDF 表格中识别特定类型报表。

    Args:
        tables: PDF 表格列表。
        table_type: 'balance_sheet' | 'income_statement' | 'cash_flow'

    Returns:
        匹配的表格，未找到返回 None。
    """
    keyword_map: Dict[str, List[str]] = {
        "balance_sheet": _BALANCE_KEYWORDS,
        "income_statement": _INCOME_KEYWORDS,
        "cash_flow": _CASHFLOW_KEYWORDS,
    }
    search_terms: List[str] = keyword_map.get(table_type, [])

    for table in tables:
        for row in table:
            row_text: str = " ".join(str(cell) for cell in row if cell)
            if any(term in row_text for term in search_terms):
                return table

    return None


def _raw_table_to_dataframe(
    table: List[List[Optional[str]]],
) -> Optional[pd.DataFrame]:
    """将 PDF 原始表格转换为 DataFrame。

    Args:
        table: PDF 原始表格。

    Returns:
        pd.DataFrame 或 None。
    """
    if not table or len(table) < 2:
        return None

    # 清理：去除全空行
    cleaned: List[List[str]] = []
    for row in table:
        str_row: List[str] = [str(cell or "").strip() for cell in row]
        if any(cell for cell in str_row):
            cleaned.append(str_row)

    if len(cleaned) < 2:
        return None

    # 标准化列数
    max_cols: int = max(len(r) for r in cleaned)
    for row in cleaned:
        while len(row) < max_cols:
            row.append("")

    # 判断表头
    first_row: List[str] = cleaned[0]
    numeric_count: int = sum(1 for c in first_row if _is_numeric_str(c))
    if numeric_count >= len(first_row) // 2:
        columns: List[str] = ["科目"] + [f"期间{i+1}" for i in range(max_cols - 1)]
        data_rows = cleaned
    else:
        columns = first_row
        data_rows = cleaned[1:]

    try:
        df: pd.DataFrame = pd.DataFrame(data_rows, columns=columns)
        df = df.dropna(how="all")
        return df
    except Exception:
        return None


def _text_section_to_dataframe(
    sections: List[str],
    table_type: str,
) -> Optional[pd.DataFrame]:
    """从财务报表段落文本中提取并构建 DataFrame。

    Args:
        sections: 财务报表段落列表。
        table_type: 目标报表类型。

    Returns:
        pd.DataFrame 或 None。
    """
    header_map: Dict[str, List[str]] = {
        "balance_sheet": ["资产负债表", "合并资产负债表", "balance sheet"],
        "income_statement": ["利润表", "合并利润表", "income statement"],
        "cash_flow": ["现金流量表", "合并现金流量表", "cash flow"],
    }

    headers: List[str] = header_map.get(table_type, [])

    target_section: Optional[str] = None
    for section in sections:
        section_lower: str = section.lower()
        for header in headers:
            if header.lower() in section_lower:
                target_section = section
                break
        if target_section:
            break

    if not target_section:
        return None

    # 按行分割，构建表格
    lines: List[str] = [
        line.strip() for line in target_section.split("\n") if line.strip()
    ]
    if len(lines) < 3:
        return None

    # 使用正则分割每一行
    rows: List[List[str]] = []
    for line in lines:
        cells: List[str] = re.split(r"\s{2,}|\t", line)
        cells = [c.strip() for c in cells if c.strip()]
        if cells:
            rows.append(cells)

    if not rows:
        return None

    max_cols: int = max(len(r) for r in rows)
    for row in rows:
        while len(row) < max_cols:
            row.append("")

    # 判断表头
    first_row: List[str] = rows[0]
    numeric_count: int = sum(1 for c in first_row if _is_numeric_str(c))
    if numeric_count >= len(first_row) // 2:
        columns: List[str] = ["科目"] + [f"期间{i+1}" for i in range(max_cols - 1)]
        data_rows = rows
    else:
        columns = first_row
        data_rows = rows[1:]

    try:
        df: pd.DataFrame = pd.DataFrame(data_rows, columns=columns)
        df = df.dropna(how="all")
        return df
    except Exception:
        return None


def _is_numeric_str(text: str) -> bool:
    """判断字符串是否为数值。

    Args:
        text: 输入字符串。

    Returns:
        bool: 是否为数值。
    """
    text = text.strip().replace(",", "").replace(" ", "").replace("%", "")
    text = text.replace("(", "").replace(")", "")
    text = re.sub(r"[¥€$万亿千百十元整]", "", text)
    if not text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False

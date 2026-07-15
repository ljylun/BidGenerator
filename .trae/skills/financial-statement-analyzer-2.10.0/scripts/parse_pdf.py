#!/usr/bin/env python3
"""PDF报表解析模块 — 使用 pdfplumber 解析PDF格式财务报表。

支持从PDF中提取表格数据，自动识别三表结构。
v1.1.0: 集成审计报告检测，更好的多表格页面处理。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PDFParseError(Exception):
    """PDF解析异常。"""


def parse_pdf(filepath: str, **kwargs: Any) -> Dict[str, Any]:
    """解析PDF格式财务报表。

    增强功能 (v1.1.0):
        - 自动检测审计报告并委托给 parse_audit_report 处理
        - 更好的多表格页面处理（表格合并、跨页表格拼接）

    Args:
        filepath: PDF文件路径。
        **kwargs: 传递给 pdfplumber.open() 的额外参数。

    Returns:
        dict: 包含三表提取数据与元信息的字典:
            {
                "tables": [...],     # 所有表格（list of list）
                "text": "全文",
                "metadata": {
                    "source": str,
                    "source_format": "pdf",
                    "extraction_method": "direct" | "hybrid",
                    "extraction_confidence": float,
                    "warnings": [...],
                    "audit_report_detected": bool,
                },
                "balance_sheet": {...},
                "income_statement": {...},
                "cash_flow": {...},
            }

    Raises:
        PDFParseError: PDF解析失败或无可提取数据。
    """
    warnings: List[str] = []

    try:
        import pdfplumber
    except ImportError:
        raise PDFParseError(
            "pdfplumber 未安装。请执行: pip install pdfplumber>=0.10.0"
        )

    try:
        with pdfplumber.open(filepath, **kwargs) as pdf:
            all_tables: List[List[List[Optional[str]]]] = []
            all_text: List[str] = []

            for page_num, page in enumerate(pdf.pages, start=1):
                # 提取表格 — 尝试多种 table_settings 以提高提取率
                tables = page.extract_tables()
                if not tables:
                    # 回退：使用更宽松的表格提取设置
                    try:
                        tables = page.extract_tables({
                            "vertical_strategy": "text",
                            "horizontal_strategy": "text",
                        })
                    except Exception:
                        pass

                for tbl in tables:
                    if tbl and _is_valid_table(tbl):
                        all_tables.append(tbl)

                # 提取文本
                text = page.extract_text()
                if text:
                    all_text.append(text)

                logger.debug(
                    "Page %d: extracted %d tables, text length %d",
                    page_num, len(tables), len(text) if text else 0,
                )

    except Exception as exc:
        raise PDFParseError(f"PDF解析失败 '{filepath}': {exc}") from exc

    if not all_tables and not all_text:
        raise PDFParseError(
            f"PDF '{filepath}' 中未提取到任何表格或文本数据。"
            "文件可能为扫描图片，请使用 parse_image 通过 OCR 处理。"
        )

    if not all_tables:
        logger.warning("PDF中未提取到任何表格数据，将仅基于文本分析。")
        warnings.append(
            "PDF中未提取到表格数据，可能是扫描图片。"
            "建议使用 parse_image 进行 OCR 识别。"
        )

    full_text: str = "\n".join(all_text)

    # --- 审计报告检测 (v1.1.0) ---
    audit_detected: bool = False
    try:
        from .parse_audit_report import is_audit_report as _is_audit

        if _is_audit(full_text):
            audit_detected = True
            logger.info(
                "Audit report detected in PDF '%s', "
                "delegating to parse_audit_report.",
                filepath,
            )
            try:
                from .parse_audit_report import parse_audit_report_from_pdf

                audit_result: Dict[str, Any] = parse_audit_report_from_pdf(filepath)
                # 合并原始表格数据
                audit_result["tables"] = all_tables
                audit_result["text"] = full_text
                audit_meta: Dict[str, Any] = audit_result.get("metadata", {})
                audit_meta["total_tables"] = len(all_tables)
                audit_meta["total_pages_text"] = len(all_text)
                audit_meta["warnings"] = (
                    audit_meta.get("warnings", []) + warnings
                )
                return audit_result
            except ImportError:
                logger.warning(
                    "parse_audit_report module not available, "
                    "falling back to standard PDF parsing."
                )
                warnings.append(
                    "检测到审计报告但无法加载专用解析器，使用标准PDF解析。"
                )
    except ImportError:
        logger.debug("parse_audit_report module not available, skipping audit check.")
    except Exception as exc:
        logger.warning("Audit report detection failed: %s", exc)

    # --- 标准财务报表解析 ---
    # 尝试合并跨页表格
    merged_tables: List[List[List[Optional[str]]]] = _merge_split_tables(all_tables)

    # 识别三表
    bs_table = _identify_pdf_table(merged_tables, "balance_sheet")
    is_table = _identify_pdf_table(merged_tables, "income_statement")
    cf_table = _identify_pdf_table(merged_tables, "cash_flow")

    # 置信度计算
    found_count: int = sum(1 for t in [bs_table, is_table, cf_table] if t is not None)
    confidence: float = (found_count / 3.0) * 100.0
    if not all_tables:
        confidence = min(confidence, 40.0)

    result: Dict[str, Any] = {
        "tables": all_tables,
        "text": full_text,
        "metadata": {
            "source": filepath,
            "source_format": "pdf",
            "extraction_method": "direct",
            "extraction_confidence": round(confidence, 1),
            "warnings": warnings,
            "audit_report_detected": audit_detected,
            "total_tables": len(all_tables),
            "total_pages_text": len(all_text),
        },
        "balance_sheet": bs_table,
        "income_statement": is_table,
        "cash_flow": cf_table,
    }
    return result


def _is_valid_table(table: List[List[Optional[str]]]) -> bool:
    """检查提取的表格是否包含有效数据。

    Args:
        table: pdfplumber 提取的表格。

    Returns:
        bool: 表格是否包含有效数据。
    """
    if not table:
        return False
    # 至少要有 2 行和 2 列
    if len(table) < 2:
        return False
    max_cols: int = max(len(row) for row in table)
    if max_cols < 2:
        return False
    # 至少有一些非空单元格
    non_empty: int = sum(
        1 for row in table for cell in row if cell and str(cell).strip()
    )
    return non_empty >= 3


def _merge_split_tables(
    tables: List[List[List[Optional[str]]]],
) -> List[List[List[Optional[str]]]]:
    """尝试合并跨页分割的表格。

    启发式方法：如果连续两个表格的列数相同且第一个表格的
    最后一行和第二个表格的第一行的首列文本相似，则可能为跨页表格。

    Args:
        tables: PDF 提取的全部表格。

    Returns:
        合并后的表格列表。
    """
    if len(tables) < 2:
        return tables

    merged: List[List[List[Optional[str]]]] = []
    skip_next: bool = False

    for i, table in enumerate(tables):
        if skip_next:
            skip_next = False
            continue

        if i + 1 < len(tables):
            current = table
            next_table = tables[i + 1]

            # 检查列数是否一致
            current_cols: int = max(len(row) for row in current)
            next_cols: int = max(len(row) for row in next_table)

            if current_cols == next_cols and current_cols >= 3:
                # 检查最后一行和第一行的首列相似度
                last_first_col: str = str(current[-1][0] or "").strip()
                next_first_col: str = str(next_table[0][0] or "").strip()

                # 如果首列差异大，可能是下一页的续表
                if last_first_col and next_first_col and last_first_col != next_first_col:
                    # 合并两张表
                    combined: List[List[Optional[str]]] = current + next_table
                    merged.append(combined)
                    skip_next = True
                    logger.info("Merged split table (indices %d and %d)", i, i + 1)
                    continue

        merged.append(table)

    return merged


def _identify_pdf_table(
    tables: List[List[List[Optional[str]]]],
    table_type: str,
) -> Optional[List[List[Optional[str]]]]:
    """通过关键词在PDF表格中识别三表。

    Args:
        tables: PDF提取的全部表格。
        table_type: 报表类型。

    Returns:
        匹配的表格，未找到返回None。
    """
    keywords: Dict[str, List[str]] = {
        "balance_sheet": ["资产总计", "负债总计", "所有者权益", "流动负债"],
        "income_statement": ["营业收入", "营业成本", "净利润", "利润总额"],
        "cash_flow": ["经营活动", "投资活动", "筹资活动", "现金流量"],
    }
    search_terms: List[str] = keywords.get(table_type, [])

    for table in tables:
        for row in table:
            row_text: str = " ".join(str(cell) for cell in row if cell)
            if any(term in row_text for term in search_terms):
                return table

    logger.warning("Could not identify '%s' in PDF tables.", table_type)
    return None


def pdf_table_to_dict(
    table: List[List[Optional[str]]],
) -> Dict[str, Dict[str, float]]:
    """将PDF表格转换为科目-数值字典。

    Args:
        table: PDF提取的单个表格 (list of rows, each row is list of cells)。

    Returns:
        dict: {科目名称: {期间: 数值}} 格式。
    """
    if not table or len(table) < 2:
        return {}

    header_row: List[str] = [str(cell or "").strip() for cell in table[0]]
    result: Dict[str, Dict[str, float]] = {}

    for row in table[1:]:
        item_name: str = str(row[0] or "").strip()
        if not item_name:
            continue
        values: Dict[str, float] = {}
        for i, cell in enumerate(row[1:], start=1):
            if i >= len(header_row):
                break
            period: str = header_row[i]
            raw_val: str = str(cell or "0").replace(",", "").replace(" ", "")
            try:
                values[period] = float(raw_val)
            except ValueError:
                values[period] = 0.0
        result[item_name] = values

    return result

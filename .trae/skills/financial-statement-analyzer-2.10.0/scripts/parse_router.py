#!/usr/bin/env python3
"""统一解析路由器 — 根据文件类型自动分派到正确的解析器。

支持格式：
    - Excel: .xlsx / .xls / .csv
    - PDF:   .pdf
    - 图片:  .png / .jpg / .jpeg / .tiff / .bmp / .webp
    - Word:  .docx
    - 审计报告: PDF/DOCX 自动检测

通过文件扩展名 + 文件头魔数双重检测，防止扩展名伪造。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 文件魔数签名
# ---------------------------------------------------------------------------

_MAGIC_SIGNATURES: Dict[str, List[bytes]] = {
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "tiff": [b"\x49\x49\x2a\x00", b"\x4d\x4d\x00\x2a"],
    "bmp": [b"\x42\x4d"],
    "webp": [b"\x52\x49\x46\x46"],  # RIFF....WEBP, 需要额外校验
    "pdf": [b"\x25\x50\x44\x46"],
    "xlsx": [b"\x50\x4b\x03\x04"],  # ZIP-based (also xlsx/docx)
    "xls": [b"\xd0\xcf\x11\xe0"],  # OLE compound document
    "docx": [b"\x50\x4b\x03\x04"],  # ZIP-based (also xlsx/docx)
    "csv": [],  # 纯文本，无魔数
}

# WEBP 的完整魔数标记
_WEBP_FULL_MAGIC: bytes = b"RIFF"


def _read_file_header(filepath: str, num_bytes: int = 8) -> bytes:
    """读取文件头的原始字节。

    Args:
        filepath: 文件路径。
        num_bytes: 读取字节数。

    Returns:
        bytes: 文件头字节，读取失败返回空字节串。
    """
    try:
        with open(filepath, "rb") as f:
            return f.read(num_bytes)
    except Exception as exc:
        logger.warning("Cannot read file header from '%s': %s", filepath, exc)
        return b""


def _detect_by_extension(filepath: str) -> Optional[str]:
    """通过文件扩展名检测文件类型。

    Args:
        filepath: 文件路径。

    Returns:
        Optional[str]: 'excel' | 'pdf' | 'image' | 'docx' | None
    """
    ext: str = os.path.splitext(filepath)[1].lower()

    excel_exts: set = {".xlsx", ".xls", ".csv"}
    image_exts: set = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
    pdf_exts: set = {".pdf"}
    docx_exts: set = {".docx"}

    if ext in excel_exts:
        return "excel"
    if ext in image_exts:
        return "image"
    if ext in pdf_exts:
        return "pdf"
    if ext in docx_exts:
        return "docx"

    return None


def _detect_by_magic(filepath: str) -> Optional[str]:
    """通过文件头魔数检测文件类型（防扩展名伪造）。

    Args:
        filepath: 文件路径。

    Returns:
        Optional[str]: 'excel' | 'pdf' | 'image' | 'docx' | None
    """
    header: bytes = _read_file_header(filepath, 8)
    if not header:
        return None

    # PDF: %PDF
    if header[:4] == b"\x25\x50\x44\x46":
        return "pdf"

    # PNG
    if header[:8] == b"\x89PNG\r\n\x1a\n":
        return "image"

    # JPEG
    if header[:3] == b"\xff\xd8\xff":
        return "image"

    # TIFF
    if header[:4] in (b"\x49\x49\x2a\x00", b"\x4d\x4d\x00\x2a"):
        return "image"

    # BMP
    if header[:2] == b"\x42\x4d":
        return "image"

    # WEBP: RIFF????WEBP
    if header[:4] == b"\x52\x49\x46\x46":
        # 读取更多字节确认 WEBP
        extended: bytes = _read_file_header(filepath, 16)
        if extended[8:12] == b"WEBP":
            return "image"

    # ZIP-based: xlsx / docx
    if header[:4] == b"\x50\x4b\x03\x04":
        ext: str = os.path.splitext(filepath)[1].lower()
        if ext == ".docx":
            return "docx"
        if ext in (".xlsx", ".xls", ".csv"):
            return "excel"
        # 如果扩展名也不确定，尝试从 ZIP 内文件判断
        return _zip_content_type(filepath)

    # OLE-based: .xls
    if header[:4] == b"\xd0\xcf\x11\xe0":
        return "excel"

    return None


def _zip_content_type(filepath: str) -> Optional[str]:
    """尝试通过 ZIP 内部文件判断是 xlsx 还是 docx。

    Args:
        filepath: 文件路径。

    Returns:
        Optional[str]: 'excel' | 'docx' | None
    """
    try:
        import zipfile
        with zipfile.ZipFile(filepath, "r") as zf:
            names: List[str] = zf.namelist()
            for name in names:
                lower_name: str = name.lower()
                if "xl/" in lower_name or "xl\\" in lower_name:
                    return "excel"
                if "word/" in lower_name or "word\\" in lower_name:
                    return "docx"
    except Exception as exc:
        logger.warning("Cannot inspect ZIP content of '%s': %s", filepath, exc)
    return None


def detect_file_type(filepath: str) -> str:
    """综合检测文件类型（扩展名 + 魔数兜底）。

    优先使用扩展名，当扩展名与魔数冲突时以魔数为准。

    Args:
        filepath: 文件路径。

    Returns:
        str: 文件类型 — 'excel' | 'pdf' | 'image' | 'docx' | 'unknown'
    """
    ext_type: Optional[str] = _detect_by_extension(filepath)
    magic_type: Optional[str] = _detect_by_magic(filepath)

    # 魔数优先（防伪造）
    if magic_type is not None:
        if ext_type is not None and ext_type != magic_type:
            logger.warning(
                "Extension type '%s' does not match magic type '%s' for '%s'. "
                "Using magic type.",
                ext_type, magic_type, filepath,
            )
        return magic_type

    if ext_type is not None:
        return ext_type

    return "unknown"


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------

_ROUTE_TABLE: Dict[str, Callable] = {}


def _build_route_table() -> Dict[str, Callable]:
    """延迟构建路由表（避免循环导入）。

    Returns:
        Dict[str, Callable]: 类型到解析函数的映射。
    """
    if _ROUTE_TABLE:
        return _ROUTE_TABLE

    from .parse_excel import parse_excel as _pe
    from .parse_pdf import parse_pdf as _pp
    from .parse_image import parse_image as _pi

    _ROUTE_TABLE["excel"] = _pe
    _ROUTE_TABLE["pdf"] = _pp
    _ROUTE_TABLE["image"] = _pi

    # DOCX 是可选依赖
    try:
        from .parse_docx import parse_docx as _pd
        _ROUTE_TABLE["docx"] = _pd
    except ImportError:
        logger.warning("parse_docx not available; DOCX routing disabled.")

    return _ROUTE_TABLE


# ---------------------------------------------------------------------------
# 统一入口
# ---------------------------------------------------------------------------


def parse_financial_document(filepath: str, **kwargs: Any) -> Dict[str, Any]:
    """统一解析入口 — 自动检测文件类型并分派到正确的解析器。

    支持自动检测以下格式：
        - Excel: .xlsx / .xls / .csv → parse_excel
        - PDF:   .pdf                 → parse_pdf (内部审计报告检测)
        - 图片:  .png / .jpg / .jpeg / .tiff / .bmp / .webp → parse_image
        - Word:  .docx                → parse_docx

    通过文件扩展名 + 魔数双重检测防止伪造。

    Args:
        filepath: 财务报表文件路径。
        **kwargs: 传递给具体解析器的额外参数。

    Returns:
        dict: 统一输出格式:
            {
                "balance_sheet": pd.DataFrame | None,
                "income_statement": pd.DataFrame | None,
                "cash_flow": pd.DataFrame | None,
                "metadata": {
                    "source": str,
                    "source_format": str,
                    "extraction_method": str,
                    "extraction_confidence": float,
                    "warnings": [...],
                    "audit_report_detected": bool,
                }
            }

        对于无法识别的格式，返回空数据 + 详细 warnings。
    """
    # 检查文件是否存在
    if not os.path.isfile(filepath):
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": {
                "source": filepath,
                "source_format": "unknown",
                "extraction_method": "none",
                "extraction_confidence": 0.0,
                "warnings": [f"文件不存在: {filepath}"],
                "audit_report_detected": False,
            },
        }

    file_type: str = detect_file_type(filepath)
    logger.info("Detected file type: %s for '%s'", file_type, filepath)

    if file_type == "unknown":
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": {
                "source": filepath,
                "source_format": "unknown",
                "extraction_method": "none",
                "extraction_confidence": 0.0,
                "warnings": [
                    f"无法识别的文件格式: {filepath}。"
                    "支持的格式: .xlsx/.xls/.csv/.pdf/.png/.jpg/.jpeg/.tiff/.bmp/.webp/.docx"
                ],
                "audit_report_detected": False,
            },
        }

    route_table: Dict[str, Callable] = _build_route_table()

    if file_type not in route_table:
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": {
                "source": filepath,
                "source_format": file_type,
                "extraction_method": "none",
                "extraction_confidence": 0.0,
                "warnings": [
                    f"文件类型 '{file_type}' 已识别但缺少对应解析器。"
                    f"请安装必要依赖: pip install python-docx"
                ],
                "audit_report_detected": False,
            },
        }

    parser: Callable = route_table[file_type]
    try:
        result: Dict[str, Any] = parser(filepath, **kwargs)
    except Exception as exc:
        logger.exception("Parser for '%s' raised an exception: %s", file_type, exc)
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": {
                "source": filepath,
                "source_format": file_type,
                "extraction_method": "direct",
                "extraction_confidence": 0.0,
                "warnings": [
                    f"解析器 '{file_type}' 执行异常: {exc}"
                ],
                "audit_report_detected": False,
            },
        }

    # 统一标准化 metadata
    metadata: Dict[str, Any] = result.setdefault("metadata", {})
    metadata.setdefault("source", filepath)
    metadata.setdefault("warnings", [])

    # 确保关键字段存在
    metadata.setdefault("source_format", file_type)
    metadata.setdefault("extraction_method", "direct")
    metadata.setdefault("extraction_confidence", 0.0)
    metadata.setdefault("audit_report_detected", False)

    # 标准化 balance_sheet / income_statement / cash_flow
    result.setdefault("balance_sheet", None)
    result.setdefault("income_statement", None)
    result.setdefault("cash_flow", None)

    return result


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------


def parse_pasted_text_as_document(text: str) -> Dict[str, Any]:
    """以统一文档格式解析粘贴的文本数据。

    委托给 parse_paste.parse_pasted_text，并标准化输出格式。

    Args:
        text: 粘贴的原始文本。

    Returns:
        dict: 统一输出格式。
    """
    from . import parse_paste as _pp

    try:
        result: Dict[str, Any] = _pp.parse_pasted_text(text)
    except Exception as exc:
        logger.warning("Paste parsing failed: %s", exc)
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": {
                "source_format": "paste",
                "extraction_method": "direct",
                "extraction_confidence": 0.0,
                "warnings": [
                    f"粘贴文本解析失败: {exc}"
                ],
                "audit_report_detected": False,
            },
        }

    metadata: Dict[str, Any] = result.setdefault("metadata", {})
    metadata.setdefault("source_format", "paste")
    metadata.setdefault("extraction_method", "direct")
    metadata.setdefault("extraction_confidence", 0.0)
    metadata.setdefault("audit_report_detected", False)

    # 从 parse_paste 的数据质量中提取置信度
    data_quality: Dict[str, Any] = metadata.get("data_quality", {})
    if data_quality:
        metadata["extraction_confidence"] = data_quality.get("credibility", 50.0)

    return result


# 已知图像扩展名集合（供外部使用）
KNOWN_IMAGE_EXTENSIONS: set = frozenset({
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp",
})

KNOWN_EXCEL_EXTENSIONS: set = frozenset({".xlsx", ".xls", ".csv"})
KNOWN_PDF_EXTENSIONS: set = frozenset({".pdf"})
KNOWN_DOCX_EXTENSIONS: set = frozenset({".docx"})

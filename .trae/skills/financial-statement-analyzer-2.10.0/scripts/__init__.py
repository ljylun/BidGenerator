"""财务报表分析专家 — V1.1.0

新增 (v1.1.0):
    - 图片 OCR 解析 (parse_image)
    - Word 文档解析 (parse_docx)
    - 审计报告专项解析 (parse_audit_report)
    - 统一解析路由 (parse_router)

作者: 优方皑尔 Uform Ai
"""

__version__ = "1.1.0"
__author__ = "优方皑尔 Uform Ai"

# ---------------------------------------------------------------------------
# 解析器导出 — 向后兼容 v1.0.0
# ---------------------------------------------------------------------------

from .parse_excel import parse_excel, extract_numeric_timeseries
from .parse_pdf import parse_pdf, pdf_table_to_dict
from .parse_paste import parse_pasted_text

# v1.1.0 新增
from .parse_image import parse_image
from .parse_docx import parse_docx
from .parse_audit_report import (
    is_audit_report,
    extract_financial_sections,
    parse_audit_report_from_pdf,
    parse_audit_report_from_docx,
)
from .parse_router import (
    parse_financial_document,
    parse_pasted_text_as_document,
    detect_file_type,
    KNOWN_IMAGE_EXTENSIONS,
    KNOWN_EXCEL_EXTENSIONS,
    KNOWN_PDF_EXTENSIONS,
    KNOWN_DOCX_EXTENSIONS,
)

# ---------------------------------------------------------------------------
# 分析模块导出
# ---------------------------------------------------------------------------

from .compute_ratios import compute_all_ratios
from .compute_mscore import compute_mscore
from .scan_redflags import scan_red_flags
from .detect_anomalies import detect_anomalies
from .verify_crosschecks import verify_crosschecks
from .match_cases import match_cases
from .generate_advice import generate_advice
from .render_charts import render_charts_bundle
from .generate_report import generate_report

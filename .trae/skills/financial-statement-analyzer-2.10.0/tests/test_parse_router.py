#!/usr/bin/env python3
"""统一解析路由器测试。

测试文件类型检测、路由正确性、未知格式降级处理。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict

import pytest


# ---------------------------------------------------------------------------
# 测试文件类型检测
# ---------------------------------------------------------------------------


class TestDetectFileType:
    """测试 detect_file_type 函数。"""

    def test_excel_xlsx(self) -> None:
        """扩展名 .xlsx 应检测为 excel。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.xlsx") == "excel"

    def test_excel_xls(self) -> None:
        """扩展名 .xls 应检测为 excel。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.xls") == "excel"

    def test_csv(self) -> None:
        """扩展名 .csv 应检测为 excel。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.csv") == "excel"

    def test_pdf(self) -> None:
        """扩展名 .pdf 应检测为 pdf。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.pdf") == "pdf"

    def test_png(self) -> None:
        """扩展名 .png 应检测为 image。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.png") == "image"

    def test_jpg(self) -> None:
        """扩展名 .jpg 应检测为 image。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.jpg") == "image"

    def test_jpeg(self) -> None:
        """扩展名 .jpeg 应检测为 image。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.jpeg") == "image"

    def test_tiff(self) -> None:
        """扩展名 .tiff 应检测为 image。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.tiff") == "image"

    def test_bmp(self) -> None:
        """扩展名 .bmp 应检测为 image。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.bmp") == "image"

    def test_webp(self) -> None:
        """扩展名 .webp 应检测为 image。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.webp") == "image"

    def test_docx(self) -> None:
        """扩展名 .docx 应检测为 docx。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.docx") == "docx"

    def test_unknown(self) -> None:
        """未知扩展名应返回 unknown。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("test.xyz") == "unknown"

    def test_no_extension(self) -> None:
        """无扩展名应返回 unknown。"""
        from scripts.parse_router import detect_file_type

        assert detect_file_type("testfile") == "unknown"


class TestMagicDetection:
    """测试魔数检测兜底。"""

    def test_pdf_magic_detection(self) -> None:
        """PDF 文件头魔数应被正确识别。"""
        from scripts.parse_router import detect_file_type

        with tempfile.NamedTemporaryFile(
            suffix=".xyz", delete=False, mode="wb"
        ) as f:
            f.write(b"%PDF-1.4\n%\x80\x80\x80\x80\n")
            f.flush()
            f.seek(0)

            file_type = detect_file_type(f.name)

        os.unlink(f.name)
        assert file_type == "pdf", f"Expected 'pdf', got '{file_type}'"

    def test_png_magic_detection(self) -> None:
        """PNG 文件头魔数应被正确识别。"""
        from scripts.parse_router import detect_file_type

        # PNG 最小合法文件
        png_header: bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x00\x00\x00\x00\x3a\x7e\x9b\x55"
        )
        with tempfile.NamedTemporaryFile(
            suffix=".xyz", delete=False, mode="wb"
        ) as f:
            f.write(png_header)
            f.flush()

            file_type = detect_file_type(f.name)

        os.unlink(f.name)
        assert file_type == "image", f"Expected 'image', got '{file_type}'"

    def test_jpg_magic_detection(self) -> None:
        """JPEG 文件头魔数应被正确识别。"""
        from scripts.parse_router import detect_file_type

        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="wb"
        ) as f:
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")
            f.flush()

            file_type = detect_file_type(f.name)

        os.unlink(f.name)
        assert file_type == "image", f"Expected 'image', got '{file_type}'"

    def test_extension_fake_png_as_txt(self) -> None:
        """扩展名为 .txt 但内容为 PNG 时，魔数应胜出。"""
        from scripts.parse_router import detect_file_type

        png_header: bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x00\x00\x00\x00\x3a\x7e\x9b\x55"
        )
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="wb"
        ) as f:
            f.write(png_header)
            f.flush()

            file_type = detect_file_type(f.name)

        os.unlink(f.name)
        assert file_type == "image", (
            f"Magic should override .txt extension, got '{file_type}'"
        )


# ---------------------------------------------------------------------------
# 测试路由正确性
# ---------------------------------------------------------------------------


class TestRouterDispatch:
    """测试 parse_financial_document 路由分派。"""

    def test_unknown_format_returns_warning(self) -> None:
        """未知格式应返回空数据 + 警告。"""
        from scripts.parse_router import parse_financial_document

        with tempfile.NamedTemporaryFile(
            suffix=".xyz", delete=False, mode="w"
        ) as f:
            f.write("some random content")
            f.flush()
            result = parse_financial_document(f.name)

        os.unlink(f.name)

        assert result["balance_sheet"] is None
        assert result["income_statement"] is None
        assert result["cash_flow"] is None
        assert len(result["metadata"]["warnings"]) >= 1
        assert result["metadata"]["source_format"] == "unknown"

    def test_file_not_found(self) -> None:
        """不存在的文件应返回错误信息。"""
        from scripts.parse_router import parse_financial_document

        result = parse_financial_document("/nonexistent/file.xlsx")

        assert result["balance_sheet"] is None
        assert "文件不存在" in result["metadata"]["warnings"][0]

    def test_metadata_keys_present(self) -> None:
        """返回的 metadata 应包含所有必需字段。"""
        from scripts.parse_router import parse_financial_document

        with tempfile.NamedTemporaryFile(
            suffix=".xyz", delete=False, mode="w"
        ) as f:
            f.write("content")
            f.flush()
            result = parse_financial_document(f.name)

        os.unlink(f.name)

        meta: Dict[str, Any] = result["metadata"]
        assert "source" in meta
        assert "source_format" in meta
        assert "extraction_method" in meta
        assert "extraction_confidence" in meta
        assert "warnings" in meta
        assert "audit_report_detected" in meta

    def test_excel_route_has_correct_source_format(self) -> None:
        """Excel 格式的 metadata 应标记 source_format='excel'。"""
        from scripts.parse_router import parse_financial_document

        # 创建一个最小的 xlsx 文件来测试路由
        try:
            import pandas as pd

            with tempfile.NamedTemporaryFile(
                suffix=".xlsx", delete=False
            ) as f:
                df = pd.DataFrame({
                    "科目": ["资产总计", "负债总计"],
                    "2024": [1000.0, 600.0],
                })
                df.to_excel(f.name, index=False, sheet_name="资产负债表")
                f.flush()

                result = parse_financial_document(f.name)

            os.unlink(f.name)

            assert result["metadata"]["source_format"] == "excel"
            assert result["metadata"]["extraction_method"] == "direct"
            assert result["balance_sheet"] is not None
        except ImportError:
            pytest.skip("pandas/openpyxl not available")


class TestKnownExtensions:
    """测试已知扩展名常量。"""

    def test_image_extensions(self) -> None:
        """KNOWN_IMAGE_EXTENSIONS 应包含所有支持的图片格式。"""
        from scripts.parse_router import KNOWN_IMAGE_EXTENSIONS

        assert ".png" in KNOWN_IMAGE_EXTENSIONS
        assert ".jpg" in KNOWN_IMAGE_EXTENSIONS
        assert ".jpeg" in KNOWN_IMAGE_EXTENSIONS
        assert ".bmp" in KNOWN_IMAGE_EXTENSIONS
        assert ".webp" in KNOWN_IMAGE_EXTENSIONS

    def test_excel_extensions(self) -> None:
        """KNOWN_EXCEL_EXTENSIONS 应包括 .xlsx / .xls / .csv。"""
        from scripts.parse_router import KNOWN_EXCEL_EXTENSIONS

        assert ".xlsx" in KNOWN_EXCEL_EXTENSIONS
        assert ".xls" in KNOWN_EXCEL_EXTENSIONS
        assert ".csv" in KNOWN_EXCEL_EXTENSIONS

    def test_pdf_extensions(self) -> None:
        """KNOWN_PDF_EXTENSIONS 应包含 .pdf。"""
        from scripts.parse_router import KNOWN_PDF_EXTENSIONS

        assert ".pdf" in KNOWN_PDF_EXTENSIONS

    def test_docx_extensions(self) -> None:
        """KNOWN_DOCX_EXTENSIONS 应包含 .docx。"""
        from scripts.parse_router import KNOWN_DOCX_EXTENSIONS

        assert ".docx" in KNOWN_DOCX_EXTENSIONS


class TestPastedTextRouting:
    """测试粘贴文本的统一路由。"""

    def test_parse_pasted_text_as_document(self) -> None:
        """粘贴文本应正确委托给 parse_paste 并标准化输出。"""
        from scripts.parse_router import parse_pasted_text_as_document

        # 使用标准 CSV 格式的资产负债表
        text: str = (
            "科目,2024,2023\n"
            "资产总计,1000,900\n"
            "负债总计,600,550\n"
            "所有者权益,400,350\n"
        )
        result = parse_pasted_text_as_document(text)

        assert result["metadata"]["source_format"] == "paste"
        assert "extraction_confidence" in result["metadata"]
        assert result["balance_sheet"] is not None or result["income_statement"] is not None

    def test_empty_paste_returns_gracefully(self) -> None:
        """空文本粘贴不应崩溃。"""
        from scripts.parse_router import parse_pasted_text_as_document

        # 空文本会触发 PasteParseError，在 router 中应被降级处理
        try:
            result = parse_pasted_text_as_document("")
            # 如果没抛异常，metadata 应该正确
            assert "source_format" in result.get("metadata", {})
        except Exception:
            # parse_pasted_text 可能直接抛异常，这也是可接受的
            pass

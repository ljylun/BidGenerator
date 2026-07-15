#!/usr/bin/env python3
"""图片 OCR 解析器测试。

测试图片预处理、OCR 提取、关键词检测和置信度计算。

作者: 优方皑尔 Uform Ai
版本: v1.1.0
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List

import pytest


# ---------------------------------------------------------------------------
# 测试图片预处理
# ---------------------------------------------------------------------------


class TestImagePreprocessing:
    """测试 _preprocess_image 函数。"""

    def test_preprocess_valid_image(self) -> None:
        """有效图片应成功预处理。"""
        from scripts.parse_image import _preprocess_image

        # 用 Pillow 创建一个简单的测试图片
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not available")

        img = Image.new("RGB", (200, 100), color=(255, 255, 255))
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as f:
            img.save(f.name, "PNG")
            f.flush()

            result = _preprocess_image(f.name)

        os.unlink(f.name)

        assert result is not None
        assert result.mode == "L"  # 灰度

    def test_preprocess_nonexistent_file(self) -> None:
        """不存在的文件应抛出 FileNotFoundError。"""
        from scripts.parse_image import _preprocess_image

        with pytest.raises(FileNotFoundError):
            _preprocess_image("/nonexistent/image.png")

    def test_preprocess_small_image(self) -> None:
        """小尺寸图片也应正确处理。"""
        from scripts.parse_image import _preprocess_image

        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not available")

        img = Image.new("RGB", (10, 10), color=(128, 128, 128))
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as f:
            img.save(f.name, "PNG")
            f.flush()

            result = _preprocess_image(f.name)

        os.unlink(f.name)

        assert result is not None
        assert result.size == (10, 10)

    def test_preprocess_dark_image(self) -> None:
        """暗色图片应被正确二值化。"""
        from scripts.parse_image import _preprocess_image

        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not available")

        # 创建暗背景白文字的图片
        img = Image.new("RGB", (100, 50), color=(20, 20, 20))
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as f:
            img.save(f.name, "PNG")
            f.flush()

            result = _preprocess_image(f.name)

        os.unlink(f.name)

        assert result is not None
        # 暗图二值化后应大部分为黑色 (0)
        histogram = result.histogram()
        if len(histogram) >= 256:
            # 暗像素（0-127）应该比亮像素多
            dark_pixels = sum(histogram[:128])
            bright_pixels = sum(histogram[128:])
            # 原始背景是暗的，所以二值化后暗像素应该占主导
            assert dark_pixels > 0, "Should have dark pixels after binarization"
            assert dark_pixels >= bright_pixels, (
                f"Dark image should have more dark pixels after binarization, "
                f"got dark={dark_pixels}, bright={bright_pixels}"
            )


# ---------------------------------------------------------------------------
# 测试关键词检测
# ---------------------------------------------------------------------------


class TestKeywordDetection:
    """测试 _classify_table_keywords 和相关的关键词检测函数。"""

    def test_balance_sheet_keywords(self) -> None:
        """资产负债表关键词应被检测到。"""
        from scripts.parse_image import _classify_table_keywords

        text: str = (
            "资产负债表\n"
            "资产总计 1000 万元\n"
            "负债总计 600 万元\n"
            "所有者权益 400 万元\n"
        )
        result = _classify_table_keywords(text)
        assert result == "balance_sheet", f"Expected balance_sheet, got {result}"

    def test_income_statement_keywords(self) -> None:
        """利润表关键词应被检测到。"""
        from scripts.parse_image import _classify_table_keywords

        text: str = (
            "利润表\n"
            "营业收入 5000 万元\n"
            "营业成本 3000 万元\n"
            "净利润 500 万元\n"
        )
        result = _classify_table_keywords(text)
        assert result == "income_statement", f"Expected income_statement, got {result}"

    def test_cash_flow_keywords(self) -> None:
        """现金流量表关键词应被检测到。"""
        from scripts.parse_image import _classify_table_keywords

        text: str = (
            "现金流量表\n"
            "经营活动产生 200 万元\n"
            "投资活动产生 -100 万元\n"
            "筹资活动产生 50 万元\n"
        )
        result = _classify_table_keywords(text)
        assert result == "cash_flow", f"Expected cash_flow, got {result}"

    def test_no_keywords_returns_none(self) -> None:
        """无财务关键词的文本应返回 None。"""
        from scripts.parse_image import _classify_table_keywords

        text: str = "这是一段没有财务关键词的文本。"
        result = _classify_table_keywords(text)
        assert result is None, f"Expected None, got {result}"

    def test_single_keyword_insufficient(self) -> None:
        """仅匹配 1 个关键词不足以分类。"""
        from scripts.parse_image import _classify_table_keywords

        text: str = "资产总计"  # 仅 1 个关键词
        result = _classify_table_keywords(text)
        assert result is None, f"Single keyword should not classify, got {result}"


# ---------------------------------------------------------------------------
# 测试表格检测
# ---------------------------------------------------------------------------


class TestTableDetection:
    """测试 _detect_table_structure 函数。"""

    def test_simple_table_detection(self) -> None:
        """简单制表符分隔的文本应正确检测为表格。"""
        from scripts.parse_image import _detect_table_structure

        text: str = (
            "科目          2024      2023\n"
            "资产总计      1000      900\n"
            "负债总计       600      550\n"
            "所有者权益     400      350\n"
        )
        df = _detect_table_structure(text)

        assert df is not None
        assert df.shape[0] >= 3  # 至少 3 行数据

    def test_no_table_structure(self) -> None:
        """纯文本段落不应被识别为表格。"""
        from scripts.parse_image import _detect_table_structure

        text: str = "这是一段普通的描述性文字，没有任何表格结构。"
        df = _detect_table_structure(text)

        assert df is None

    def test_two_column_table(self) -> None:
        """两列表格应被正确检测。"""
        from scripts.parse_image import _detect_table_structure

        text: str = (
            "科目          金额\n"
            "营业收入      5000\n"
            "营业成本      3000\n"
        )
        df = _detect_table_structure(text)

        assert df is not None
        assert df.shape[1] >= 2


# ---------------------------------------------------------------------------
# 测试置信度计算
# ---------------------------------------------------------------------------


class TestConfidence:
    """测试 _compute_confidence 函数。"""

    def test_high_confidence_with_keywords(self) -> None:
        """含财务关键词的长文本应有较高置信度。"""
        from scripts.parse_image import _compute_confidence

        text: str = (
            "资产负债表 资产总计 负债总计 所有者权益 "
            "利润表 营业收入 营业成本 净利润 "
            "现金流量表 经营活动 投资活动 筹资活动 "
            * 5  # 重复以获得足够长度
        )
        blocks: List[Dict[str, Any]] = [
            {"conf": 90.0, "text": t} for t in text.split()
        ]

        confidence = _compute_confidence(text, blocks)
        assert confidence > 50.0, f"Expected high confidence, got {confidence}"

    def test_low_confidence_with_no_keywords(self) -> None:
        """无财务关键词的短文本应有较低置信度。"""
        from scripts.parse_image import _compute_confidence

        text: str = "a b c"
        blocks: List[Dict[str, Any]] = [
            {"conf": 10.0, "text": "a"},
            {"conf": 15.0, "text": "b"},
            {"conf": 20.0, "text": "c"},
        ]

        confidence = _compute_confidence(text, blocks)
        assert confidence < 50.0, f"Expected low confidence, got {confidence}"

    def test_confidence_in_range(self) -> None:
        """置信度应始终在 0-100 范围。"""
        from scripts.parse_image import _compute_confidence

        # 极端情况
        confidence = _compute_confidence("", [])
        assert 0.0 <= confidence <= 100.0

        confidence = _compute_confidence("x" * 1000, [{"conf": 100.0, "text": "x"}] * 100)
        assert 0.0 <= confidence <= 100.0


# ---------------------------------------------------------------------------
# 测试主入口 parse_image
# ---------------------------------------------------------------------------


class TestParseImageMain:
    """测试 parse_image 主函数。"""

    def test_nonexistent_file_returns_gracefully(self) -> None:
        """不存在的文件应返回空数据 + 警告，不抛异常。"""
        from scripts.parse_image import parse_image

        result = parse_image("/nonexistent/image.png")

        assert result["balance_sheet"] is None
        assert result["income_statement"] is None
        assert result["cash_flow"] is None
        assert len(result["metadata"]["warnings"]) >= 1

    def test_parse_image_return_structure(self) -> None:
        """返回结构应包含所有必需字段。"""
        from scripts.parse_image import parse_image

        # 创建一个带有财务表格样式的测试图片
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            pytest.skip("Pillow not available")

        img = Image.new("RGB", (600, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 在图片上绘制模拟的财务数据
        draw.text((10, 10), "资产负债表", fill=(0, 0, 0))
        draw.text((10, 40), "资产总计  1000  900", fill=(0, 0, 0))
        draw.text((10, 70), "负债总计   600  550", fill=(0, 0, 0))
        draw.text((10, 100), "所有者权益 400  350", fill=(0, 0, 0))

        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as f:
            img.save(f.name, "PNG")
            f.flush()

            result = parse_image(f.name)

        os.unlink(f.name)

        # 检查结构
        assert "balance_sheet" in result
        assert "income_statement" in result
        assert "cash_flow" in result
        assert "metadata" in result

        meta = result["metadata"]
        assert meta["source_format"] == "image"
        assert meta["extraction_method"] == "ocr"
        assert "extraction_confidence" in meta
        assert "warnings" in meta

    def test_parse_image_with_default_lang(self) -> None:
        """默认语言应正常解析。"""
        from scripts.parse_image import parse_image

        try:
            from PIL import Image, ImageDraw
        except ImportError:
            pytest.skip("Pillow not available")

        img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test Financial Data", fill=(0, 0, 0))

        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as f:
            img.save(f.name, "PNG")
            f.flush()

            result = parse_image(f.name)

        os.unlink(f.name)

        # 不应抛异常
        assert result is not None
        assert isinstance(result, dict)


class TestSectionExtraction:
    """测试 _extract_section_for_table。"""

    def test_extract_balance_sheet_section(self) -> None:
        """应能从全文提取资产负债表段落。"""
        from scripts.parse_image import _extract_section_for_table

        text: str = (
            "一些前置文字\n"
            "资产负债表\n"
            "资产总计 1000\n"
            "负债总计 600\n"
            "所有者权益 400\n"
            "利润表\n"
            "营业收入 5000\n"
            "营业成本 3000\n"
        )
        section = _extract_section_for_table(text, "balance_sheet")
        assert section is not None
        assert "资产总计" in section
        assert "利润表" not in section  # 应在利润表开始前被截断

    def test_extract_nonexistent_section(self) -> None:
        """不存在的表类型应返回 None。"""
        from scripts.parse_image import _extract_section_for_table

        text: str = "只有资产负债表的内容，资产总计 1000。"
        section = _extract_section_for_table(text, "income_statement")
        assert section is None


class TestNumericDetection:
    """测试 _is_numeric 辅助函数。"""

    def test_plain_number(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("1234.56") is True

    def test_number_with_comma(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("1,234.56") is True

    def test_negative_number(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("-500") is True

    def test_percentage(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("25.5%") is True

    def test_non_numeric(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("abc") is False

    def test_currency_symbols(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("¥12,000") is True
        assert _is_numeric("$500") is True

    def test_chinese_units(self) -> None:
        from scripts.parse_image import _is_numeric

        assert _is_numeric("500万元") is True
        assert _is_numeric("1.5亿") is True

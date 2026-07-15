#!/usr/bin/env python3
"""图片OCR解析模块 — 使用 pytesseract + Pillow 从图片中提取财务报表数据。

支持 PNG / JPG / TIFF / BMP / WEBP 格式。
通过 OCR 提取文本后识别表格结构，自动检测三表。

作者: 优方皑尔 Uform Ai
版本: v1.2.0
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 关键词模式 — 与现有 parse_paste / parse_excel 保持一致
# ---------------------------------------------------------------------------

_BALANCE_SHEET_KEYWORDS: List[str] = [
    "资产负债表", "资产总计", "负债总计", "所有者权益",
    "流动资产", "非流动资产", "流动负债", "非流动负债",
    "balance sheet", "total assets", "total liabilities",
]

_INCOME_STATEMENT_KEYWORDS: List[str] = [
    "利润表", "营业收入", "营业成本", "净利润", "利润总额",
    "营业利润", "销售费用", "管理费用", "综合收益",
    "income statement", "revenue", "net income",
]

_CASH_FLOW_KEYWORDS: List[str] = [
    "现金流量表", "经营活动产生", "投资活动产生", "筹资活动产生",
    "现金及现金等价物", "期初现金", "期末现金",
    "cash flow", "operating activities",
]


def _preprocess_image_light(image_path: str) -> Any:
    """轻量级图片预处理：灰度 → 对比度增强 → 锐化 → 轻度去噪。

    适用于扫描件 / 中文财务报表等场景。与 _preprocess_image_heavy 不同，
    此函数不进行二值化，避免破坏中文字符边缘信息。

    Args:
        image_path: 图片文件路径。

    Returns:
        PIL.Image: 预处理后的图片对象。
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    except ImportError:
        raise ImportError("Pillow 未安装。请执行: pip install Pillow")

    img = Image.open(image_path)

    # Step 1: 灰度化
    img = ImageOps.grayscale(img)

    # Step 2: 对比度增强 (1.3x ~ 1.5x)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.4)

    # Step 3: 锐化
    img = img.filter(ImageFilter.SHARPEN)

    # Step 4: 轻度去噪 (1px 中值滤波，不过度)
    img = img.filter(ImageFilter.MedianFilter(1))

    logger.info(
        "Image preprocessed (light): size=%s, mode=%s", img.size, img.mode
    )
    return img


def _preprocess_image_heavy(image_path: str) -> Any:
    """重量级图片预处理：灰度 → 二值化 → 去噪 → 倾斜校正。

    此函数为旧版 _preprocess_image 的保留实现，适用于：
    - 高对比度、黑白分明的文档扫描件
    - 英文文档或数字表格
    对于中文财务报表，推荐使用 _preprocess_image_light()。

    Args:
        image_path: 图片文件路径。

    Returns:
        PIL.Image: 预处理后的图片对象。
    """
    try:
        from PIL import Image, ImageFilter, ImageOps
    except ImportError:
        raise ImportError("Pillow 未安装。请执行: pip install Pillow")

    img = Image.open(image_path)

    # Step 1: 灰度化
    img = ImageOps.grayscale(img)

    # Step 2: 二值化 — 使用自适应阈值（OTSU近似）
    histogram = img.histogram()
    total_pixels = sum(histogram)
    if total_pixels > 0:
        sum_brightness = sum(i * histogram[i] for i in range(256))
        threshold = sum_brightness // total_pixels
        threshold = min(threshold + 20, 240)

        def _threshold_fn(pixel: int) -> int:
            return 255 if pixel > threshold else 0

        img = img.point(_threshold_fn)

    # Step 3: 去噪 — 中值滤波
    img = img.filter(ImageFilter.MedianFilter(3))

    # Step 4: 倾斜校正
    img = img.filter(ImageFilter.SHARPEN)

    logger.info(
        "Image preprocessed (heavy): size=%s, mode=%s", img.size, img.mode
    )
    return img


# 向后兼容 — _preprocess_image 默认使用轻量模式
_preprocess_image = _preprocess_image_light


def _ocr_image(image: Any, lang: str = "chi_sim+eng", config: str = "--psm 4 --oem 3") -> str:
    """对图片执行 OCR，提取纯文本。

    Args:
        image: PIL.Image 对象。
        lang: Tesseract 语言代码，默认中英文混合。
        config: Tesseract 额外配置参数，默认 '--psm 4 --oem 3'。

    Returns:
        str: OCR 提取的文本。

    Raises:
        RuntimeError: OCR 引擎不可用时返回明确提示。
    """
    try:
        import pytesseract
    except ImportError:
        raise RuntimeError(
            "pytesseract 未安装。请执行: pip install pytesseract"
        )

    # 设置 tesseract 可执行路径（Windows 常见安装路径）
    _possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
    ]
    for p in _possible_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break

    # 设置 TESSDATA_PREFIX 环境变量
    user_tessdata = os.path.join(os.path.expanduser("~"), ".workbuddy", "tessdata")
    if os.path.exists(user_tessdata) and "TESSDATA_PREFIX" not in os.environ:
        os.environ["TESSDATA_PREFIX"] = user_tessdata

    try:
        _ = pytesseract.get_tesseract_version()
    except Exception:
        raise RuntimeError(
            "Tesseract OCR 引擎未安装或不可用。"
            "Windows: 安装 Tesseract-OCR 至 C:\\Program Files\\Tesseract-OCR\\"
        )

    try:
        text: str = pytesseract.image_to_string(image, lang=lang, config=config)
    except Exception as exc:
        # 降级：尝试只用英文
        logger.warning(
            "OCR with lang=%s failed (%s), falling back to eng", lang, exc
        )
        try:
            text = pytesseract.image_to_string(image, lang="eng", config="--psm 6")
        except Exception as exc2:
            raise RuntimeError(
                f"OCR 引擎执行失败: {exc2}"
            ) from exc2

    return text


def _ocr_image_with_boxes(image: Any, lang: str = "chi_sim+eng") -> List[Dict[str, Any]]:
    """对图片执行 OCR，获取带位置信息的文字块。

    Args:
        image: PIL.Image 对象。
        lang: Tesseract 语言代码。

    Returns:
        文字块列表，每项包含 text / left / top / width / height / conf。
    """
    try:
        import pytesseract
    except ImportError:
        return []

    try:
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    except Exception:
        return []

    blocks: List[Dict[str, Any]] = []
    n = len(data["text"])
    for i in range(n):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        try:
            conf = float(data["conf"][i])
        except (ValueError, TypeError):
            conf = 0.0
        blocks.append({
            "text": text,
            "left": data["left"][i],
            "top": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
            "conf": conf,
        })
    return blocks


def _detect_table_structure(ocr_text: str) -> Optional[pd.DataFrame]:
    """从 OCR 文本中识别表格结构并转为 DataFrame。

    策略：
        1. 按行分割文本
        2. 使用连续空白符作为分隔符
        3. 识别数值列和科目列
        4. 清理噪声行

    Args:
        ocr_text: OCR 提取的原始文本。

    Returns:
        解析出的 DataFrame，若无法识别表格则返回 None。
    """
    lines: List[str] = [line.strip() for line in ocr_text.split("\n") if line.strip()]
    if len(lines) < 3:
        return None

    # 使用正则分割每一行（2+个空格或制表符）
    rows: List[List[str]] = []
    for line in lines:
        cells: List[str] = re.split(r"\s{2,}|\t", line)
        cells = [c.strip() for c in cells if c.strip()]
        if cells:
            rows.append(cells)

    if not rows:
        return None

    # 标准化列数：取最大列数
    max_cols: int = max(len(r) for r in rows)
    if max_cols < 2:
        return None

    # 填充不足的列
    for row in rows:
        while len(row) < max_cols:
            row.append("")

    # 尝试判断是否有表头行
    header_candidate: List[str] = rows[0]
    numeric_in_header: int = sum(
        1 for cell in header_candidate if _is_numeric(cell)
    )
    if numeric_in_header > len(header_candidate) // 2:
        # 第一行大多是数值，无表头
        columns: List[str] = ["科目"] + [f"期间{i+1}" for i in range(max_cols - 1)]
        data_rows: List[List[str]] = rows
    else:
        columns = header_candidate
        data_rows = rows[1:]

    # 确保列名唯一
    seen: Dict[str, int] = {}
    unique_columns: List[str] = []
    for col in columns:
        c = col or "col"
        if c in seen:
            seen[c] += 1
            c = f"{c}_{seen[c]}"
        else:
            seen[c] = 0
        unique_columns.append(c)

    try:
        df: pd.DataFrame = pd.DataFrame(data_rows, columns=unique_columns)
    except Exception:
        return None

    # 清理：丢弃全空行
    df = df.dropna(how="all")
    if df.empty:
        return None

    return df


def _classify_table_keywords(text: str) -> Optional[str]:
    """通过关键词识别文本属于哪个财务报表。

    Args:
        text: OCR 全文本。

    Returns:
        str: 'balance_sheet' | 'income_statement' | 'cash_flow' | None
    """
    bs_score: int = sum(1 for kw in _BALANCE_SHEET_KEYWORDS if kw.lower() in text.lower())
    is_score: int = sum(1 for kw in _INCOME_STATEMENT_KEYWORDS if kw.lower() in text.lower())
    cf_score: int = sum(1 for kw in _CASH_FLOW_KEYWORDS if kw.lower() in text.lower())

    scores: List[Tuple[str, int]] = [
        ("balance_sheet", bs_score),
        ("income_statement", is_score),
        ("cash_flow", cf_score),
    ]
    scores.sort(key=lambda x: x[1], reverse=True)

    # 需要至少匹配 2 个关键词才认为有效
    if scores[0][1] >= 2:
        return scores[0][0]
    return None


def _compute_confidence(ocr_text: str, blocks: List[Dict[str, Any]]) -> float:
    """计算 OCR 提取置信度评分 (0-100)。

    基于：
        - OCR 文字块的平均置信度
        - 文本中检测到的关键词数量
        - 文本长度合理性

    Args:
        ocr_text: OCR 提取文本。
        blocks: OCR 文字块列表（含 conf 字段）。
        tables: 检测到的表格数据。

    Returns:
        float: 0-100 的置信度评分。
    """
    score: float = 0.0

    # 1. OCR 引擎置信度 (0-40 分)
    if blocks:
        conf_values: List[float] = [b["conf"] for b in blocks if b["conf"] > 0]
        if conf_values:
            avg_conf: float = sum(conf_values) / len(conf_values)
            score += min(avg_conf, 100.0) * 0.4
    else:
        # 无位置信息，给基本分
        score += 20.0

    # 2. 关键词检测 (0-30 分)
    all_keywords: List[str] = (
        _BALANCE_SHEET_KEYWORDS
        + _INCOME_STATEMENT_KEYWORDS
        + _CASH_FLOW_KEYWORDS
    )
    keyword_hits: int = sum(
        1 for kw in all_keywords if kw.lower() in ocr_text.lower()
    )
    score += min(keyword_hits * 5.0, 30.0)

    # 3. 文本长度合理性 (0-30 分)
    text_len: int = len(ocr_text.strip())
    if text_len > 500:
        score += 30.0
    elif text_len > 200:
        score += 20.0
    elif text_len > 50:
        score += 10.0

    return min(score, 100.0)


def _is_numeric(text: str) -> bool:
    """判断文本是否为数值。

    Args:
        text: 输入文本。

    Returns:
        bool: 是否为数值。
    """
    text = text.strip().replace(",", "").replace(" ", "").replace("%", "")
    # 移除可能的括号和货币符号
    text = text.replace("(", "").replace(")", "")
    text = text.replace("¥", "").replace("$", "").replace("€", "")
    # 移除中文单位
    text = re.sub(r"[万亿千百十元整]", "", text)
    if not text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def parse_image(
    filepath: str,
    lang: str = "chi_sim+eng",
    preprocess_mode: str = "light",
    psm: int = 4,
) -> Dict[str, Any]:
    """从图片中解析财务报表数据。

    预处理流程（默认轻量模式）：灰度 → 对比度增强 → 锐化 → 轻度去噪。
    对于中文财务报表，轻量模式效果显著优于二值化模式。
    OCR 提取文本后，通过关键词识别三表结构，输出统一接口格式。

    Args:
        filepath: 图片文件路径。支持 PNG/JPG/TIFF/BMP/WEBP。
        lang: OCR 语言代码，默认 'chi_sim+eng'（中英文混合）。
        preprocess_mode: 预处理模式，'light'（推荐，默认）或 'heavy'（旧版二值化）。
        psm: Tesseract PSM 模式，默认 4（单列文本），可设为 3（自动）或 6（均匀文本块）。

    Returns:
        dict: 统一输出格式，解析失败时返回部分数据 + warnings。"""
    warnings: List[str] = []
    metadata: Dict[str, Any] = {
        "source": filepath,
        "source_format": "image",
        "extraction_method": "ocr",
        "extraction_confidence": 0.0,
        "warnings": [],
        "preprocess_mode": preprocess_mode,
        "psm": psm,
    }

    bs_df: Optional[pd.DataFrame] = None
    is_df: Optional[pd.DataFrame] = None
    cf_df: Optional[pd.DataFrame] = None

    # Step 1: 预处理 — 选择合适的预处理函数
    try:
        if preprocess_mode == "heavy":
            img = _preprocess_image_heavy(filepath)
        else:
            img = _preprocess_image_light(filepath)
    except FileNotFoundError:
        warnings.append(f"图片文件不存在: {filepath}")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }
    except Exception as exc:
        warnings.append(f"图片预处理失败: {exc}")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    # Step 2: OCR 提取 — 使用可配置的 PSM
    ocr_text: str = ""
    blocks: List[Dict[str, Any]] = []
    psm_config: str = f"--psm {psm} --oem 3"
    try:
        ocr_text = _ocr_image(img, lang=lang, config=psm_config)
        blocks = _ocr_image_with_boxes(img, lang=lang)
    except RuntimeError as exc:
        warnings.append(str(exc))
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }
    except Exception as exc:
        warnings.append(f"OCR 提取异常: {exc}")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    if not ocr_text.strip():
        warnings.append("OCR 未能从图片中提取到文字，请检查图片质量。")
        metadata["warnings"] = warnings
        return {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "metadata": metadata,
        }

    # Step 3: 计算置信度
    confidence: float = _compute_confidence(ocr_text, blocks)
    metadata["extraction_confidence"] = round(confidence, 1)

    if confidence < 30.0:
        warnings.append(
            f"OCR 置信度较低 ({confidence:.1f}%)，"
            "图片质量可能较差，解析结果仅供参考。"
        )

    # Step 4: 检测表格结构
    df: Optional[pd.DataFrame] = _detect_table_structure(ocr_text)

    # Step 5: 关键词分类
    if df is not None and not df.empty:
        table_type: Optional[str] = _classify_table_keywords(ocr_text)
        if table_type == "balance_sheet":
            bs_df = df
        elif table_type == "income_statement":
            is_df = df
        elif table_type == "cash_flow":
            cf_df = df
        else:
            # 无法分类，尝试用全文关键词判断并将数据赋给最可能的那一类
            logger.warning("Cannot classify the detected table; assigning best guess.")
            bs_score: int = sum(
                1 for kw in _BALANCE_SHEET_KEYWORDS if kw.lower() in ocr_text.lower()
            )
            is_score: int = sum(
                1 for kw in _INCOME_STATEMENT_KEYWORDS if kw.lower() in ocr_text.lower()
            )
            cf_score: int = sum(
                1 for kw in _CASH_FLOW_KEYWORDS if kw.lower() in ocr_text.lower()
            )
            max_score: int = max(bs_score, is_score, cf_score)
            if max_score >= 2:
                if bs_score == max_score:
                    bs_df = df
                elif is_score == max_score:
                    is_df = df
                else:
                    cf_df = df
            else:
                warnings.append(
                    "未能识别图片中的报表类型，数据可在 raw_text 中查看。"
                )

    # Step 6: 尝试分段提取三表（如果 OCR 文本包含多个表格标记）
    # 检查是否可以按关键词分割出多个表格区域
    if bs_df is None and is_df is None and cf_df is None:
        bs_section: Optional[str] = _extract_section_for_table(ocr_text, "balance_sheet")
        is_section: Optional[str] = _extract_section_for_table(ocr_text, "income_statement")
        cf_section: Optional[str] = _extract_section_for_table(ocr_text, "cash_flow")

        if bs_section:
            bs_df = _detect_table_structure(bs_section)
        if is_section:
            is_df = _detect_table_structure(is_section)
        if cf_section:
            cf_df = _detect_table_structure(cf_section)

    metadata["warnings"] = warnings
    metadata["ocr_text_length"] = len(ocr_text)

    return {
        "balance_sheet": bs_df,
        "income_statement": is_df,
        "cash_flow": cf_df,
        "metadata": metadata,
    }


def _extract_section_for_table(ocr_text: str, table_type: str) -> Optional[str]:
    """从 OCR 全文中提取某个报表的近似段落。

    Args:
        ocr_text: OCR 提取全文。
        table_type: 报表类型。

    Returns:
        提取的子文本，未找到返回 None。
    """
    section_keywords: Dict[str, List[str]] = {
        "balance_sheet": ["资产负债表", "balance sheet"],
        "income_statement": ["利润表", "income statement"],
        "cash_flow": ["现金流量表", "cash flow"],
    }

    all_other_keywords: List[str] = []
    for k, v in section_keywords.items():
        if k != table_type:
            all_other_keywords.extend(v)

    target_kws: List[str] = section_keywords.get(table_type, [])

    # 找到目标标题位置
    target_pos: int = -1
    for kw in target_kws:
        pos = ocr_text.lower().find(kw.lower())
        if pos >= 0 and (target_pos < 0 or pos < target_pos):
            target_pos = pos

    if target_pos < 0:
        return None

    # 找到下一个其他报表标题位置（截断点）
    end_pos: int = len(ocr_text)
    for kw in all_other_keywords:
        pos = ocr_text.lower().find(kw.lower(), target_pos + len(target_kws[0]))
        if pos >= 0 and pos < end_pos:
            end_pos = pos

    section_text: str = ocr_text[target_pos:end_pos].strip()
    if len(section_text) < 20:
        return None
    return section_text


# 向后兼容别名 — 支持 parse_image 和 parse_image_file 两种调用方式
parse_image_file = parse_image

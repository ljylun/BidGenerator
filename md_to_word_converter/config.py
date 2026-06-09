"""
配置文件 - Markdown转Word转换器
包含样式配置、路径配置和常量定义
"""

import os
from pathlib import Path

# ==================== 路径配置 ====================
# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()

# 默认输入文件路径
DEFAULT_INPUT_FILE = r"h:\DEV\MyProjects\BidGenerator\doc\技术标\技术标_完整版.md"

# 默认输出文件路径
DEFAULT_OUTPUT_DIR = r"h:\DEV\MyProjects\BidGenerator\doc\技术标"
DEFAULT_OUTPUT_FILE = os.path.join(DEFAULT_OUTPUT_DIR, "技术标_完整版.docx")

# 日志和报告输出路径
LOG_FILE = os.path.join(DEFAULT_OUTPUT_DIR, "conversion.log")
REPORT_FILE = os.path.join(DEFAULT_OUTPUT_DIR, "conversion_report.txt")

# 资源基础目录（用于解析相对路径）
RESOURCE_BASE_DIR = r"h:\DEV\MyProjects\BidGenerator\doc\技术标"

# ==================== 页面配置 ====================
# 页边距（单位：厘米）
PAGE_MARGIN_TOP = 2.54
PAGE_MARGIN_BOTTOM = 2.54
PAGE_MARGIN_LEFT = 3.17
PAGE_MARGIN_RIGHT = 3.17

# 页面宽度（A4纸，单位：厘米）
PAGE_WIDTH = 21.0
PAGE_HEIGHT = 29.7

# ==================== 字体配置 ====================
# 中文字体
FONT_CHINESE = "宋体"
FONT_CHINESE_HEADING = "黑体"

# 英文字体
FONT_ENGLISH = "Times New Roman"
FONT_ENGLISH_HEADING = "Arial"

# 代码字体
FONT_CODE = "Consolas"

# ==================== 字号配置（单位：磅） ====================
# 标题字号
HEADING_SIZES = {
    1: 22,  # 二号
    2: 16,  # 三号
    3: 14,  # 四号
    4: 12,  # 小四（加粗）
    5: 12,  # 小四
    6: 12,  # 小四（斜体）
}

# 正文字号
BODY_FONT_SIZE = 12  # 小四

# 代码字号
CODE_FONT_SIZE = 10

# ==================== 行距配置 ====================
# 行距（单位：磅）- 固定值22磅
LINE_SPACING = 22

# 段落间距（单位：磅）
PARAGRAPH_SPACING_BEFORE = 0
PARAGRAPH_SPACING_AFTER = 0

# ==================== 标题样式配置 ====================
HEADING_CONFIG = {
    1: {
        "font_name": FONT_CHINESE_HEADING,
        "font_size": HEADING_SIZES[1],
        "bold": True,
        "color": None,  # 黑色
    },
    2: {
        "font_name": FONT_CHINESE_HEADING,
        "font_size": HEADING_SIZES[2],
        "bold": True,
        "color": None,
    },
    3: {
        "font_name": FONT_CHINESE_HEADING,
        "font_size": HEADING_SIZES[3],
        "bold": True,
        "color": None,
    },
    4: {
        "font_name": FONT_CHINESE_HEADING,
        "font_size": HEADING_SIZES[4],
        "bold": True,
        "color": None,
    },
    5: {
        "font_name": FONT_CHINESE,
        "font_size": HEADING_SIZES[5],
        "bold": False,
        "color": None,
    },
    6: {
        "font_name": FONT_CHINESE,
        "font_size": HEADING_SIZES[6],
        "bold": False,
        "italic": True,
        "color": None,
    },
}

# ==================== 正文样式配置 ====================
BODY_CONFIG = {
    "font_name": FONT_CHINESE,
    "font_size": BODY_FONT_SIZE,
    "bold": False,
    "italic": False,
    "color": None,
}

# ==================== 表格配置 ====================
TABLE_STYLE = "Table Grid"
TABLE_FONT_SIZE = 10
TABLE_FONT_NAME = FONT_CHINESE

# ==================== 代码块配置 ====================
CODE_BLOCK_CONFIG = {
    "font_name": FONT_CODE,
    "font_size": CODE_FONT_SIZE,
    "background_color": "F0F8FF",  # 浅蓝色背景
}

# ==================== 引用块配置 ====================
BLOCKQUOTE_CONFIG = {
    "font_name": FONT_CHINESE,
    "font_size": BODY_FONT_SIZE,
    "italic": True,
    "left_indent": 1.0,  # 厘米
}

# ==================== 列表配置 ====================
LIST_CONFIG = {
    "indent": 0.74,  # 厘米（首行缩进2字符）
    "bullet_indent": 0.74,
    "number_indent": 0.74,
}

# ==================== 图片配置 ====================
# 最大图片宽度（厘米）
MAX_IMAGE_WIDTH = 16.0
# 最大图片高度（厘米）
MAX_IMAGE_HEIGHT = 20.0

# ==================== 目录配置 ====================
TOC_CONFIG = {
    "max_levels": 4,  # 目录最大层级
    "heading": "目录",
    "font_name": FONT_CHINESE_HEADING,
    "font_size": 16,
}

# ==================== 日志配置 ====================
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"

# ==================== 大文件处理配置 ====================
# 分块读取大小（字节）
CHUNK_SIZE = 1024 * 1024  # 1MB
# 最大内存使用（字节）
MAX_MEMORY_USAGE = 512 * 1024 * 1024  # 512MB

# ==================== 校验配置 ====================
# 内容校验阈值（允许的差异百分比）
CONTENT_DIFF_THRESHOLD = 0.01  # 1%
# 字数校验阈值
WORD_COUNT_DIFF_THRESHOLD = 0.02  # 2%

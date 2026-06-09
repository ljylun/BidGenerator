"""
测试脚本 - Markdown转Word转换器
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from md_to_word_converter import MarkdownToWordConverter, setup_logging
from config import DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_FILE, LOG_FILE, REPORT_FILE


def test_conversion():
    """测试转换功能"""
    print("=" * 60)
    print("Markdown转Word转换器 - 测试")
    print("=" * 60)

    # 检查输入文件
    if not os.path.exists(DEFAULT_INPUT_FILE):
        print(f"错误: 输入文件不存在: {DEFAULT_INPUT_FILE}")
        return False

    print(f"输入文件: {DEFAULT_INPUT_FILE}")
    print(f"输出文件: {DEFAULT_OUTPUT_FILE}")
    print(f"日志文件: {LOG_FILE}")
    print(f"报告文件: {REPORT_FILE}")
    print()

    # 设置日志
    logger = setup_logging(LOG_FILE)

    # 创建转换器
    converter = MarkdownToWordConverter(
        input_file=DEFAULT_INPUT_FILE,
        output_file=DEFAULT_OUTPUT_FILE,
        logger=logger
    )

    # 执行转换
    print("开始转换...")
    success = converter.convert()

    if success:
        print()
        print("=" * 60)
        print("转换成功!")
        print("=" * 60)
        print(f"输出文件: {DEFAULT_OUTPUT_FILE}")
        print(f"文件大小: {os.path.getsize(DEFAULT_OUTPUT_FILE) / 1024 / 1024:.2f} MB")
        print(f"校验报告: {REPORT_FILE}")
        return True
    else:
        print()
        print("=" * 60)
        print("转换失败!")
        print("=" * 60)
        print(f"请查看日志文件: {LOG_FILE}")
        return False


if __name__ == "__main__":
    success = test_conversion()
    sys.exit(0 if success else 1)

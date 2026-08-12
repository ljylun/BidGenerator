# -*- coding: utf-8 -*-
"""
修复脚本：修复append_chapter3_a.py中的字符串问题
"""

file_path = r"g:\Projects\BidGenerator\ebooks\GenerativeAI轻松学\append_chapter3_a.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 将content = r"""替换为content = '''
content = content.replace('content = r"""', 'content = \'\'\'')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("修复完成")

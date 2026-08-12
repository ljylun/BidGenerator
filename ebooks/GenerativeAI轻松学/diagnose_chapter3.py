# -*- coding: utf-8 -*-
"""
诊断脚本：统计append_chapter3_a.py中三个连续双引号的数量
"""

file_path = r"g:\Projects\BidGenerator\ebooks\GenerativeAI轻松学\append_chapter3_a.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

count = content.count('"""')
print(f"三个连续双引号的数量：{count}")

# 找到所有出现位置
index = 0
positions = []
while True:
    index = content.find('"""', index)
    if index == -1:
        break
    positions.append(index)
    index += 1

print(f"出现位置（前20个）：{positions[:20]}")

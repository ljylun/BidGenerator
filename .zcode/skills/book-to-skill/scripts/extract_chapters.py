#!/usr/bin/env python3
"""Extract individual chapters from full_text.txt for book-to-skill converter."""
import os
import sys

workdir = r'C:\Users\sun\AppData\Local\Temp\book_skill_work_dmt0wle6'
path = os.path.join(workdir, 'full_text.txt')
outdir = os.path.join(workdir, 'chapters')
os.makedirs(outdir, exist_ok=True)

lines = open(path, 'r', encoding='utf-8').read().split('\n')

# Chapter boundaries (line numbers) - detected from analysis
# Format: (start_line, end_line, chapter_num, title)
chapters = [
    (940, 1646, 1, "Introduction to agents and their world"),
    (1646, 2884, 2, "Harnessing the power of large language models"),
    (2884, 3960, 3, "Engaging GPT assistants"),
    (3960, 5425, 4, "Exploring multi-agent systems"),
    (5425, 7273, 5, "Empowering agents with actions"),
    (7273, 8976, 6, "Building autonomous assistants"),
    (8976, 9980, 7, "Assembling and using an agent platform"),
    (9980, 11460, 8, "Understanding agent memory and knowledge"),
    (11460, 12768, 9, "Mastering agent prompts with prompt flow"),
    (12768, 14244, 10, "Agent reasoning and evaluation"),
    (14244, 15700, 11, "Agent planning and feedback"),
]

for start, end, num, title in chapters:
    chapter_text = '\n'.join(lines[start:end])
    outpath = os.path.join(outdir, f'ch{num:02d}.txt')
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(f'# Chapter {num}: {title}\n\n')
        f.write(chapter_text)
    print(f'ch{num:02d}: lines {start}-{end} ({end-start} lines) -> {outpath}')

print(f'\nDone. {len(chapters)} chapters extracted to {outdir}')

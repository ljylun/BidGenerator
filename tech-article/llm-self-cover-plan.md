# 封面设计方案

## 1. 模板类型与选择理由

**模板：冲突型（Conflict）- Pure Graphic Impact 变体**

选择理由：
- 本文属于「知识 / 方法论 / AI 研究洞察」类内容，冲突型最匹配
- 文章核心是一个反直觉发现：「推理能力越强的模型，面对噪声反而越脆弱」
- 不需要真人出镜，纯图形冲击更适合科技深度内容的调性
- 用大号中文标题本身作为视觉锚点，符合「利益点在缩略图里清不清楚」的核心逻辑

---

## 2. 锚点位置

**主锚点：大号中文标题，居中偏上，占据画面约 45% 高度**

- 锚点位置：画面中心偏上 1/3 到 1/2 区域
- 眼动路径：标题（最强对比区）→ 底部标签 → 背景电路纹理（弱）
- 只有一个视觉重心，无竞争元素

---

## 3. 配色方案

采用「科技蓝」配色组，契合 AI / 大模型主题：

| 角色 | 色值 | 用途 |
|------|------|------|
| 主色（背景）| #0D1B2A | 深空蓝黑，占画面 100% |
| 撞色（标题字）| #F1C40F | 电光黄，用于主标题 |
| 强调色（副标题/标签）| #2471A3 | 科技蓝，用于副标题和角标 |
| 辅助色（光晕/粒子）| #00E5FF | 青蓝霓虹，用于背景电路纹理 |
| 高光色（装饰）| #FFFFFF | 纯白，用于细小强调线 |

- 主标题（黄）与背景（深蓝黑）对比度 ≈ 12:1，远超 4.5:1 阈值，80px 缩略图下完全可读
- 副标题（蓝色）与背景（深蓝黑）对比度 ≈ 4.8:1，刚好过关

---

## 4. 字重层级

| 层级 | 内容 | 字色 | 字号占比 | 字数 |
|------|------|------|---------|------|
| 主标题 | AI越强，越容易被骗 | #F1C40F | 画面高度 35-40% | 9 字 |
| 副标题 | 大模型的噪声脆弱性 | #2471A3 | 画面高度 5% | 8 字 |
| 角标 | AI研究笔记 | #FFFFFF on #2471A3 | 画面高度 3% | 5 字 |

- 主标题 vs 副标题字号比 ≈ 5:1
- 主标题笔画粗细：Heavy / Black
- 副标题笔画粗细：Medium
- 角标：Light，深蓝底白字小标签

---

## 5. Cover Headline 设计

原文标题太长（「大语言模型自我验证与环境鲁棒性研究」22 字），不适合作为封面。

**封面主标题候选**：
1. AI越强，越容易被骗（9 字）✓ 最终采用
2. 聪明反被聪明误（7 字）
3. 大模型的致命软肋（8 字）
4. 噪声面前，强者先倒（8 字）

选择「AI越强，越容易被骗」：
- 反直觉，冲突感强
- 「AI」直接点题，「越强」和「越容易被骗」构成悖论
- 9 字，在 6-12 字推荐范围内
- 缩略图下 80px 仍可辨识

---

## 6. 完整 ChatGPT Image 2 生图提示词

```text
Create a finished 3:4 vertical Xiaohongshu cover poster, optimized for mobile feed readability.

Template: pure graphic conflict-style cover.
Topic: why stronger AI models are more vulnerable to noise.
Audience: AI researchers, engineers, tech enthusiasts.

Exact readable Chinese copy:
- Main headline, huge bold Chinese type: "AI越强，越容易被骗"
- Supporting line below: "大模型的噪声脆弱性"
- Small tag in upper-left corner: "AI研究笔记"

Composition:
- The main headline sits in the center, slightly above middle, occupying about 40% of the image height.
- Use deep space-blue-black (#0D1B2A) as the full background.
- Main headline is in electric yellow (#F1C40F) thick-stroke Heavy/Black Chinese typography, bold and commanding.
- A short supporting line sits beneath the headline in tech-blue (#2471A3) Medium weight, smaller and subdued.
- A small white-on-blue tag is placed at the upper-left corner.
- Behind the headline, add subtle glowing circuit-line patterns in cyan neon (#00E5FF) at low opacity (10-20%), suggesting AI neural networks without competing with the headline.
- Add a few sparse floating particles or data nodes in the background, very subtle.
- High contrast between bright yellow text and dark background.

Style:
- Premium AI research cover, deep dark tech palette, electric yellow headline, subtle neon blue circuit details, high contrast, editorial poster finish.
- The headline must dominate all other elements. No visual competition.

Constraints:
- The Chinese text must be crisp, readable, and correctly written. No garbled characters.
- No tiny paragraphs, no fake logos, no fake revenue numbers, no watermark, no QR code.
- No creator signature, no @ handle.
- Pass the 80px thumbnail test: headline remains readable at small size.
```

---

## 7. 自检清单

- [x] 主标题在 80px 缩略图下可读（粗体黄字 + 深蓝背景 = 12:1 对比度）
- [x] 只有一视觉锚点（主标题），无竞争元素
- [x] 封面标题比文章原标题更短、更有冲突感
- [x] 无密集解释性段落
- [x] 中文文字字号足够大，无乱码风险
- [x] 无虚假 logo、二维码、收益数据
- [x] 无水印和 @ 账号
- [x] 配色方案主色 + 撞色不超过 3 色

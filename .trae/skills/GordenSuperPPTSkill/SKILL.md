---
name: GordenSuperPPTSkill
description: >-
  一键全流程 PPT：先用 GordenImagePPTGen 生成「图片格式的 PPT」，再用 GordenImage2PPTX 把它逆向还原成「可编辑 .pptx」。
  打包并依次编排这两个子技能，最终同时交付 图片型 PPT + 可编辑 pptx + 全部中间产物。Orchestrates image-PPT
  generation and image→editable-PPTX conversion end to end. 当用户只给主题/内容、要一份"既好看又能编辑"的完整 PPT 成品，
  或没点名具体功能时使用。
---

# GordenSuperPPTSkill — 端到端 PPT 全流程编排

把两个子技能串起来跑：

```
内容 ─▶【阶段1 GordenImagePPTGen】图片型 PPT（每页 .png + 图片版 .pptx）
       ─▶【阶段2 GordenImage2PPTX】对每页图片做 背景图+骨架图+元素图标+文本 还原 ─▶ 可编辑 .pptx
```

本技能本身不重复造轮子——它**依次完整执行两个子技能**。两个子技能需与本技能同处（同一仓库/同一 skills 目录）：
- 阶段 1：**[`../GordenImagePPTGen/SKILL.md`](../GordenImagePPTGen/SKILL.md)**（功能 A：生成图片型 PPT）
- 阶段 2：**[`../GordenImage2PPTX/SKILL.md`](../GordenImage2PPTX/SKILL.md)**（功能 B：图片 → 可编辑 PPTX）

端到端运行手册见 **[`references/pipeline.md`](references/pipeline.md)**。

## 阶段 1 图片生成硬门禁

阶段 1 的“生成图片”只允许解释为：**实际调用 Codex 内置 imagegen 图像模型生成每一页幻灯片成品图**。

禁止用以下方式替代阶段 1 出图：
- Python/PIL、SVG、HTML、Canvas、matplotlib、PowerPoint shapes、截图渲染。
- 用代码绘制整页幻灯片图，再把它当作“图片型 PPT”。
- 先用可编辑 PPTX / 原生 shapes 做页面，再导出为 PNG 充当阶段 1 结果。
- 用代码在已生成图片上补字、盖字、改字。

Codex 运行时必须满足：
- 每页都调用一次或多次 imagegen，最终选定一张模型生成图。
- 生成源图必须来自 `$CODEX_HOME/generated_images/<thread-id>/...png`。
- 只能把源图**复制**到本任务 `slides/NN-*.png`；不要删除默认生成目录中的原图。
- 必须写入 `imagegen-manifest.json`，逐页记录 `generated_source` 与 `copied_to`。

如果 imagegen 不可用，必须停止并说明阻塞原因，不能使用代码绘图兜底。

## 何时用哪个

| 用户意图 | 用哪个技能 |
|---|---|
| 「做一份 PPT / 生成图片版 PPT / AI 出图幻灯片」 | 只用 **GordenImagePPTGen** |
| 「把这些 PPT 图片/截图转成可编辑 PPTX / 抠图标 / 提取文字」 | 只用 **GordenImage2PPTX** |
| 没点名，只给主题/内容要一份能用的成品；或要"既能看又能编辑" | 用 **本技能**（A→B 串联） |

- 用户**明确**点名某一功能 → 直接用对应子技能，不必走 Super。
- 没点名时默认走 Super：先完整出图，再逐页还原为可编辑，最后一次性交付全部产物。

## 编排流程（逐项打勾）

```
== 阶段 1：GordenImagePPTGen（完整跑功能 A）==
- [ ] 读 ../GordenImagePPTGen/SKILL.md，按 A1–A5 执行
- [ ] 每页实际调用 imagegen 生成成品图
- [ ] 产出：outline.json、prompts/NN-*.md、imagegen-manifest.json、slides/NN-*.png、图片型 .pptx
- [ ] 铁律：每页图必须含【全部真实文字 verbatim】，绝不出占位符/无字模板图
- [ ] 门禁：没有 imagegen-manifest.json 或任一页缺 generated_source，则阶段 1 失败，不能进入阶段 2

== 阶段 2：GordenImage2PPTX（对阶段1每张图完整跑功能 B）==
- [ ] 读 ../GordenImage2PPTX/SKILL.md，对每页图片按 B1–B9 执行
- [ ] 强制四层：背景图 → 骨架图(绿幕抠图) → 元素图标(绿幕抠图) → 文本(OCR)，缺一不可
- [ ] 背景图、骨架图、元素图标图必须由 imagegen 提取式生成
- [ ] 禁止用 PPT 色块、原生 shapes、代码绘图、裁原图局部替代背景/骨架/图标图片层
- [ ] 产出：每页 imagegen-assets-manifest.json + background/frame/icons/layout.json + 合成的可编辑 .pptx

== 交付 ==
- [ ] 一次性交付：① 所有 PPT 图片 ② 每页背景图 ③ 每页骨架图 ④ 每页图标/装饰 ⑤ 每页文本数据(layout.json) ⑥ 图片型 .pptx ⑦ 可编辑 .pptx
```

## 关键约束（两阶段都要守）

1. 🔴 阶段1**必须调用  imagegen 出图，绝不用代码绘图替代，且绝不出占位符图**；阶段2**背景/骨架/图标图片层也必须调用 imagegen 生成，绝不跳过骨架图与元素图标**（四层强制）。这两条是上一版退化的根因，务必守住。
2. **比例统一**：A 和 B 全程同一比例（默认 16:9；用户要 3:2 就全套 3:2）。
3. **配色统一、每页框架不重复**（阶段1）；**抠图保色保线、图标尺寸对照原图**（阶段2）。
4. 数据零编造；语言跟随用户；页脚干净；少用纯绿（绿幕抠图会冲突）。

## 输出目录结构（建议）

```
<topic-slug>/
├── outline.json / imagegen-manifest.json / prompts/ / slides/   # 阶段1
├── out/<topic>-image-deck.pptx              # 阶段1 图片型成品
└── editable/                                # 阶段2
    ├── NN/{background.png, frame.png, icons/*.png, layout.json}
    ├── deck.json
    ├── preview/slide_*.png
    └── <topic>-editable.pptx                # 阶段2 可编辑成品
```

> 子技能各自自带脚本与 references；本技能只负责编排与交付。若两个子技能不在同处，请先安装它们，或直接分别调用。

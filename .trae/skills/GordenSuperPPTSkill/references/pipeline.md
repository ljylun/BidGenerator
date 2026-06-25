# 端到端运行手册（A → B 串联）

本技能 = 依次完整执行两个子技能。本文件是落地细节；每阶段的**完整**规范以子技能的 SKILL.md / references 为准。

## 阶段 1 · 生成图片型 PPT（GordenImagePPTGen）

1. **A1 确认**：风格 / 受众 / 页数 / 语言（用户说"直接生成"则跳过，并声明所用设定）。比例跟随用户（默认 16:9；用户要 3:2 就全套 3:2）。
2. **A2 大纲 `outline.json`**：解构内容；为**每页指派不重复的复杂框架**；**统一一套配色**；写厚每页 `detailed_content`（真实数据，禁编造）。
3. **A3 提示词**：把 outline 落地成每页 self-contained 提示词，**【页面文字】写满全部真实文字(verbatim)**。
4. **A4 出图**：必须逐页调用 imagegen 图像模型出图；**每页必须是含全部真实文字的成品图，绝不占位符/空模板**；错字/失败只重出该页；把 `$CODEX_HOME/generated_images/<thread-id>/...png` 源图复制到 `slides/`，保留原图；写 `imagegen-manifest.json`。
5. **A5 合成**：`compose_pptx.py deck.json out/<topic>-image-deck.pptx`（每页只一个 `background`）。

### A4 阻塞门禁

- “生成图片”只指调用图像生成模型，不指用 Python/PIL、SVG、HTML、Canvas、matplotlib、PowerPoint shapes 或截图渲染生成 PNG。
- 禁止先做可编辑 PPTX / 原生 shapes，再导出图片充当阶段 1。
- 禁止用代码在生成图上补字、盖字、改字。
- 若 imagegen 不可用，必须停止并说明阻塞原因，不能用代码绘图兜底。
- 没有 `imagegen-manifest.json`，或任一页缺 `generated_source` 与 `copied_to`，阶段 1 判失败，不能进入阶段 2。

> 详见 `../GordenImagePPTGen/references/image-prompt-guide.md`（§0 内容优先、§1.5 复杂度、§1.7 唯一框架+清晰优先、§4 图表目录、§7 outline 结构）。

## 阶段 2 · 还原为可编辑 PPTX（GordenImage2PPTX）

对阶段 1 的**每一张** `slides/NN-*.png`，按强制四层执行：

1. **B1 探色** → 定抠图底色（默认绿，含绿改非绿）。
2. **B2 背景**：用 imagegen 复刻干净背景（无文字/图标/框架/卡片），禁止 PPT 色块或裁原图。
3. **B3 骨架图**：用 imagegen 在抠图底色上提取容器/卡片(含填充/标题条)/分隔线/图表骨架，**不含文字图标** → 抠图成全幅透明 `frame`。
4. **B4 元素图标**：用 imagegen 把所有图标/装饰排成 N×N 绿底网格 → 抠图 → 切片；禁止从原图裁图标。
5. **B5–B7**：`chroma_key.py` 保色抠图（骨架+图标）→ `slice_grid.py` 切图标 → 定位(尺寸对照原图) → 视觉 OCR 文字 → 写 `layout.json`。
6. **B8 合成**：`compose_pptx.py` 出可编辑 .pptx + `--preview-dir` 预览。
7. **B9 QA**：预览对比原图，调 `layout.json` 重合成至贴合。

每页必须写 `imagegen-assets-manifest.json`，记录 B2/B3/B4 的模型生成源图 `generated_source` 与复制路径 `copied_to`；缺失则阶段 2 判失败。

> 详见 `../GordenImage2PPTX/references/image-to-pptx.md`（B1–B9 全流程 + schema + 抠图保真铁律）。

## 两条防退化铁律（必须守）

- 🔴 阶段 1：**绝不生成占位符/无文字模板图**。`visual_generation_prompt` 只是画面半成品，禁止单独出图——必须合并全部文字。
- 🔴 阶段 1：**必须调用 imagegen 生成每页图片**，禁止任何代码绘制整页幻灯片图替代。
- 🔴 阶段 2：**B2 背景、B3 骨架图、B4 元素图标图都必须调用 imagegen 生成**。禁止用原生 `shapes`、PPT 色块、代码绘图或裁原图局部替代图片层。

## 最终交付

① 所有 PPT 图片 ② `imagegen-manifest.json` ③ 每页 `imagegen-assets-manifest.json` ④ 每页背景图 ⑤ 每页骨架图 ⑥ 每页图标/装饰 ⑦ 每页文本数据 `layout.json` ⑧ 图片型 `.pptx` ⑨ 可编辑 `.pptx`。

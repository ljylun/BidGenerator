---
name: GordenImage2PPTX
description: >-
  把「图片格式的 PPT 文档 / 幻灯片截图 / 任意图片页」逆向还原成**可编辑的 .pptx**。强制四层流程：
  复刻背景图 + 绿幕抠出整体框架图 + 绿幕抠出元素图标/装饰 + GPT 视觉提取文字，再合成（文字是真文本框、框架图/图标是可移动图片；只有用户明确要求框架切分时才切成框架部件）。
  Converts slide images back into an editable PPTX via background + skeleton + icons + text layers. 当用户要
  "把 PPT 图片/截图转可编辑 PPTX、把图片PPT还原为可编辑PPT、抠图标、复刻背景、提取文字、还原排版"时使用。输入是图片，输出是可编辑 .pptx。
---

# GordenImage2PPTX — 图片 PPT → 可编辑 PPTX

**一张一张处理**每张图片，强制拆成四层再合成可编辑 .pptx（从下到上）。其中前三个图片层必须由 imagegen 生成或提取，文字层由 GPT 视觉能力提取并写成真文本框：

```
背景图(复刻) + 整体框架图(绿幕抠图,默认不切分) + 元素图标/装饰(绿幕抠图,切片) + 文字(GPT视觉提取)
```

> 🟣 **直接转换原则**：用户给出图片并要求转可编辑 PPTX 时，**不要先扫描当前目录、历史输出或其它项目，去寻找/复用类似源页**。直接把用户提供的当前图片作为唯一源图，按 B1-B9 流程提取背景图、框架图、元素图标和文字，建立新的 PPTX 文档。只有用户明确要求复用旧素材、续做某个历史输出、或指定已有源文件时，才读取对应历史文件。

> 🧱 **任务隔离原则（防串文件）**：每次转换开始前必须创建唯一任务根目录 `RUN_ROOT`，例如 `image2pptx_runs/<时间戳>_<源图slug>/`，并把本次所有中间产物、prompt、manifest、layout、预览、QA 和最终 PPTX 都写到该目录下。禁止把新任务直接写到工作区固定的 `editable/01`、`out/`、`qa/` 或 `slide-01/`，也禁止从这些固定路径读取素材。若目录已存在，必须换一个新目录，不得复用或覆盖。
>
> `layout.json` 的图片路径必须在同一个 `RUN_ROOT` 内解析：单页 layout 优先**省略** `assets_dir`（让 `compose_pptx.py` 自动用 layout 所在目录），或写成绝对页目录；不得写 `"assets_dir": "editable/01"` 这类会受当前工作目录影响的相对路径。manifest 的 `copied_to` 也必须是 `RUN_ROOT` 内的绝对路径。

> 🟦 **框架图 = 一页里「背景、元素图标/装饰/艺术字、普通文本」之外的所有图像**：容器/卡片(含底色填充与标题条)、分隔/连接线、**全部图表图形（折线/柱状/阶梯/饼图/坐标网格/趋势线）**、缎带、装饰线条与色块——统统归框架图，一次性提取，且**形状·大小·位置与原图 1:1 一致**（别漏数据折线/装饰）。
>
> 🟨 **艺术字 = 装饰元素，不是普通文本**：凡是带有渐变颜色、书法/笔刷造型、形变、描边/阴影/纹理、徽章式排版或普通字体无法直接写出的文字，都归入 B4 图标/装饰层，以图片元素提取和摆放。例如封面大字“灵芝”。B7 GPT 视觉文本层只处理普通字体可直接还原的文字。

> 🔴 **强制四层，缺一不可（核心铁律）**：**背景图 → 整体框架图 → 元素图标 → 文本**。这四步是本技能的本质，**任何一页都必须实打实地出"框架图(B3)"和"元素图标图(B4)"并绿幕抠图**，默认用整张透明 `frame.png` 作为框架视觉层合成；只有用户明确要求"框架可移动部件/切分框架/拆成一块块"时，才把框架图按透明区域切成 `frame_parts/` 后合成。
> **禁止的退化做法**：① 直接拿原图当背景叠文字（双重文字）；② 用 PPT 原生 `shapes` / 色块 / 线条重画背景、卡片、标题条、图表、时间轴、装饰；③ 从原图裁切局部当作背景、框架或图标素材；④ 省略框架/图标；⑤ 用代码/PIL/SVG/HTML/Canvas 画出图片层。
> 背景图、框架图、元素图标图都必须来自 **imagegen 提取式生成**：背景用 imagegen 复刻干净背景；框架图用固定 B3 提示词在纯色抠图底上生成全幅框架层；图标/装饰用 imagegen 在纯色抠图底上生成图标表，图标表里不画网格分割线。`chroma_key.py` 只负责去底，`slice_grid.py` 只允许切分 **imagegen 生成并已去底的图标表**；若用户明确要求框架切分，才允许切分已去底的 `frame.png`。不得切原始幻灯片截图。
> **生成证据硬门禁**：B2/B3/B4 必须在 `imagegen-assets-manifest.json` 中记录真实 imagegen 调用证据：`backend` 必须是 imagegen 类后端，`generated_source` 必须指向或描述真实生成结果，`prompt_file` 必须指向本页使用的提示词文件，且 `copied_to` 必须是交付目录内对应图片。若 manifest 显示 `programmatic`、`local layer generator`、`PIL`、`SVG`、`HTML`、`Canvas`、`matplotlib`、`screenshot renderer`、`null prompt_file` 等非 imagegen 生成迹象，本页转换失败，必须重做，不能交付。

## 图片层生成硬门禁

本技能中的“图片 → 可编辑 PPTX”不是用 PPT 色块重画页面。可编辑边界是：
- 文字：写成可编辑文本框。
- 背景/框架/图标/装饰/图表图形：由 imagegen 生成为图片层；框架图默认以整张透明 `frame.png` 放入 PPT（可整体移动、替换、缩放），图标放入 PPT 后可移动、可替换、可缩放。只有用户明确要求框架切分时，才把框架图去底后按透明区域切成可移动框架部件。

禁止使用以下方式替代图片层：
- 在 PPTX 中用原生 shapes、填充色块、线条、箭头、表格、图表组件重画背景/卡片/框架/图标/装饰/图表。
- 从原始幻灯片截图裁切局部作为背景、框架、车辆、图标或装饰素材。
- 用 Python/PIL、SVG、HTML、Canvas、matplotlib 或截图渲染生成背景/框架/图标图片。
- 先用原生 PPT 元素搭页面，再导出为图片层。

允许代码做的事仅限：
- `probe_palette.py` 探色。
- 复制 imagegen 生成的图片到本次 `RUN_ROOT/editable/NN/`。
- `chroma_key.py` 给 imagegen 生成的框架图/图标图去底。
- `slice_grid.py --auto/--grid` 切分 imagegen 生成的图标表。
- 可选：仅当用户明确要求框架切分时，使用 `slice_grid.py --components` 按透明区域切分 imagegen 生成并去底后的 `frame.png`，再用 `frame_parts_to_icons.py` 生成 `icons[] role:"frame_part"`。
- 写 `layout.json` / `deck.json`，合成 PPTX 和预览。
- `layout_guard.py` 校验或修正 `layout.json` 的坐标契约：`ref_width/ref_height` 必须匹配源图实际像素尺寸，`source_bbox` 与 `x/y/w/h` 必须一致。
- `visual_compare_qa.py` 把源图和最终 PPTX 预览统一尺寸后生成并排图、叠图、差异热图和诊断指标，供 GPT 视觉判断文字/图标是否与原始 PPT 图片对位。
- 可选地裁切/缩放**整张 imagegen 生成图**以统一比例；不得裁原图局部冒充素材。

每页必须写 `imagegen-assets-manifest.json`，记录 B2/B3/B4 的 `generated_source`、`copied_to`、`layer`、`prompt_file`、`backend`、`key_color`。没有 manifest，或任一图片层缺 `generated_source` / `prompt_file`，或任一图片层的 `backend` 不是 imagegen，本页转换失败，不能交付。

完整流水线、提示词、坐标/字号换算、QA 反馈环见 **[`references/image-to-pptx.md`](references/image-to-pptx.md)**；运行时与图片后端见 **[`references/runtime-notes.md`](references/runtime-notes.md)**。

## 运行时与图片后端（先读）

1. 出图（复刻背景、框架图、图标图）必须用 raster 图像生成后端：Codex 用内置 `imagegen`  / imagegen（**支持把原图作为输入做"提取式"出图**）；其它运行时用其原生出图工具。**禁止** SVG/HTML/Canvas/代码画图、PPT shapes、裁原图局部冒充。
2. 抠透明用本技能自带 **`scripts/chroma_key.py`（保色保线/保形）**——内部不透明像素颜色 100% 保留（红/藏青/灰/白绝不褪色），默认不腐蚀边缘（细线/辉光不丢）；`frame-safe` / `icon-safe` 会增强半透明边缘 alpha，并只用二值 gap repair 修补细线断点，避免横竖线不齐、圆弧残缺。框架/图标默认加 `--scale 2` 先超采样抠图，再在 PPT 里缩回目标尺寸，让横竖线和圆弧更顺。**别用激进的 `--soft-matte --despill --edge-contract` 组合**去抠扁平图（会变色+丢线）。
3. 看图（文字/图标定位）必须用 GPT 自身视觉能力，输出结构化 JSON。不要先跑 tesseract、EasyOCR、系统 OCR 等传统 OCR 引擎。

### imagegen 传图 / edit target 硬门禁

Codex 内置 `image_gen` 生成 B2/B3/B4 时，**必须先用 `view_image` 打开当前页源图**，让这张图成为当前对话里可见的 **edit target**，然后再调用 `image_gen`。Prompt 必须明确写“以刚刚显示的这张图片作为唯一编辑目标 / edit target，在它的基础上提取或擦除生成目标层”。**不要只把源图当作风格参考图**，更禁止只在 prompt 里写本地文件路径来冒充传图：路径文本不会自动把图片传给 imagegen，模型会凭描述猜，框架图和图标图会跑偏。

多页任务必须一页一页处理：生成第 1 页 B2/B3/B4 前只显示第 1 页源图；生成第 2 页前重新 `view_image` 第 2 页源图，并在 prompt 中指向“刚刚显示的这张图是本次编辑目标”。若 imagegen 产物无法证明基于当前 edit target 提取，或明显与源图不一致，本页 B2/B3/B4 判失败，必须重出，不能进入 B5-B9。

## 每页工作流（逐项打勾）

```
- [ ] B0 隔离目录：为本次任务创建唯一 `RUN_ROOT`，所有文件只写入/读取该目录；不得复用工作区固定 `editable/01`、`out/`、`qa/`
- [ ] B0a 传图：每页 B2/B3/B4 调 imagegen 前，必须先 `view_image` 当前页源图；prompt 写“以刚刚显示的这张图片作为唯一编辑目标 / edit target，在它的基础上提取或擦除生成目标层”；不得只写本地路径、不得只作为风格参考或凭文字描述猜图
- [ ] B1 探色：probe_palette.py 判断该页是否含绿 → 定本页抠图底色（默认 #00ff00；含绿改 #ff00ff 等）
- [ ] B2 背景：用 imagegen 复刻干净背景（无任何文字/图标/框架/卡片/占位块），禁止用 PPT 色块、程序绘图或裁原图；写 prompt 文件并登记真实 imagegen 调用记录
- [ ] B3 框架图：用 imagegen 在抠图底色上提取框架图，生成图片提示词固定为“生成一张图片，提取这张图片中的框架图，纯色背景，背景色值为XXXXXX，「框架图」= 原图里**除背景/图标/装饰/艺术字/普通文本外的一切**（容器轮廓与**底色填充/标题条/辉光**、分隔/连接线、**全部图表图形：折线/柱状/阶梯/饼图/坐标网格/趋势线**、缎带/装饰）→ 形状·大小·位置与原图 **1:1 一致**，保留原色与填充，别漏数据折线/装饰、别自己额外加空心线框、占位框；不要出现文字、不要出现图标；”；只允许把 XXXXXX 替换为 B1 决定的背景色值（默认 #00ff00；原图有绿色则改 #ff00ff、#8000ff 等原图没有的颜色）；写 prompt 文件并登记真实 imagegen 调用记录
- [ ] B4 图标图：先用 GPT 视觉对比**原图 vs B3 frame 预览**，列出「源图全部图标/装饰/艺术字清单」和「已误入 frame 的图标清单」；B4 prompt 只生成 frame 里没有的元素，避免同一图标在 frame 与 icons 双重出现；用 imagegen 把缺失元素排成 N×N 等分方格网（小图标 4×4，大装饰/物品图/艺术字 2×2 或单独大格），多了出多张；方格网不要画分割线，不画实线和虚线，提示词里要明确写出这一点；如果最终生成的图片不小心有了方格分割线也没关系，先抠图，然后裁剪掉分割线就好（因为每个网格有留白）；禁止从原图裁图标、程序绘制图标或艺术字；写 prompt 文件并登记真实 imagegen 调用记录
- [ ] B5 抠图与图标切分：scripts/chroma_key.py 给 imagegen 生成的框架图+图标图去底（框架用 `--preset frame-safe`，图标/艺术字用 `--preset icon-safe` 保边）→ 默认保留整张透明 `frame.png`，不做框架切分；图标表用 `slice_grid.py --auto --pad 24 --contact-sheet` 按透明空隙切成单个透明图标 → 查看 `icons_contact_sheet.png`、`frame.png` 灰底自检；任一图标被切断、粘连、缺边、edge_touch 异常，必须重出或重切，不能交付。若用户明确要求框架切分，再运行 `slice_grid.py --components --pad 0 --contact-sheet --prefix fp` 把 `frame.png` 切成 `frame_parts/`
- [ ] B6 定位：默认最终 `layout.json` 使用整张 `frame.png` 作为框架视觉层：写 `"frame":"frame.png"`，不要把框架切成 `frame_parts`。再逐个量出每个普通图标/艺术字在**源图实际像素坐标系**里的 `x/y/w/h` bbox，并换算成比例写入：`x=x_px/ref_width`、`y=y_px/ref_height`、`w=w_px/ref_width`、`h=h_px/ref_height`（manifest 只有素材表尺寸，必须补原图实测坐标；保持宽高比、尺寸贴合原图）→ `layout.json` 默认用 `units:"fraction"`；`view_image`/浏览器/预览图显示的缩略坐标不能直接写入，必须按 `源图宽/显示宽` 与 `源图高/显示高` 分别换回源图像素；禁止只把 x 放大、y 不放大这类混合坐标。首次合成后必须按预览反向校准普通图标尺寸/位置，缩放一律以源图 bbox 中心点为锚点，禁止按切片素材尺寸或视觉感觉直接摆放。若用户明确要求框架切分，才运行 `frame_parts_to_icons.py` 读取 `frame_parts/icons_manifest.json`，按每个框架切片在 `frame.png` 中的 bbox 映射成比例坐标，生成 `icons[] role:"frame_part"` 条目；这个 bbox 回放是拼回原 `frame.png` 布局的保证
- [ ] B7 文字：用 GPT 视觉读取原图所有**普通字体文字**(内容/像素位置/字号/颜色/粗细/对齐) → 先量**源图实际像素 bbox**，再按比例写入 layout：`x/y/w/h` 用 fraction，字号优先用 `size_ratio = 源图实际文字高度像素 / ref_height`（或 `size_pct = size_ratio*100`），如果用户或源 PPT 期望 PowerPoint 号数字号，也可以直接写 `size` 绝对 pt；不要把缩略图上的文字高度当作源图 `size_px`。换算公式是 `pt = size_ratio × (slide_height_in×72) = size_px × (slide_height_in×72) / ref_height`，反推为 `size_px = 目标pt × ref_height / (slide_height_in×72)`。如果坐标来自 2048×1143 这类缩略显示，而源图是 4096×2286，必须先把 `x/y/w/h/source_bbox/size_px` 全部乘以 2 后再写入；例如 7.441in 高、2286px 源图中，20px 只会得到 4.69pt，9pt 应写约 38.4px。艺术字只记录为 B4 图标/装饰定位，不写入普通文本框；首次预览后必须对照源图微调文本框比例、字号比例和行距，确保换行、基线和相对图标位置还原原图。**先定字体粗细/字号/行距，再回校位置**：`bold` 默认 `false`，普通正文不要全加粗，只有各级标题、按钮标题、重点词按原图加粗；多行正文段落优先用约 `line_spacing:1.2`，否则后续改粗细/行距会改变换行和视觉 bbox，让已量好的坐标再次漂移。
- [ ] B7a 坐标与样式契约校验：合成前必须运行 `layout_guard.py 源图 layout.json --strict`。`ref_width/ref_height` 必须等于源图实际像素尺寸；`source_bbox` 必须覆盖源图中真实对象，而不是覆盖 `view_image` 缩略坐标位置。若量测来自同宽高比缩略图，先把 bbox 与 `size_px` 缩放回源图像素，或用 `--fix-ref-to-source --fix-fractions --in-place` 归一化，再重新人工复查关键文本和图标。`layout_guard --strict` 还会拦截疑似半分辨率字号（默认低于 6pt、或 `source_bbox` 行高明显大于 `size_px`）和“正文全加粗”（6 个以上文本框超过 85% bold）；真实小字必须显式写 `small_text_ok:true`，真实全粗体页必须写 `allow_all_bold_text:true` 并在 QA 备注说明。`layout_guard` 不用页面覆盖高度判错；任何 `source_bbox` 与 `x/y/w/h` 不一致、字号/粗细警告未处理，都不能进入 B8。
- [ ] B7b 源图 bbox 视觉复核：合成前先运行 `placement_qa.py` 只画源图框并打开 `slide_01_source_boxes.png`，确认每个文本/图标框真实圈住源图对象。`layout_guard` 只能发现坐标字段不一致，不能发现“bbox 一致但量错对象/量到错误行”的问题；发现错框必须先改 `source_bbox`，再让 `x/y/w/h` 由 bbox 换算。
- [ ] B7c 框架锚点回校：B7a/B7b 通过后，必须再看**最终合成预览中的 `frame.png`**，对贴在框架上的文本做二次校准：分区标题条、面板标题、按钮文字、底部总结条、页脚/横幅、步骤标签等，不只按源图 bbox 放置，还要按生成后的 `frame.png` 标题条/按钮/底栏的视觉中心线或内边距回校。若 `frame.png` 相对源图有轻微漂移，文本应跟随最终 frame 锚点移动；`layout_guard` 通过不代表这些文本已经视觉对位。记录每个被调整文本的 `frame_anchor`（如 `left_panel_title_bar`、`bottom_summary_bar`）、`dy_px` 和原因到 QA 笔记或 layout 旁文件。
- [ ] B8 合成：compose_pptx.py 生成 .pptx，并 --preview-dir 出预览图
- [ ] B9 QA：检查 `imagegen-assets-manifest.json` 中 B2/B3/B4 是否都有 imagegen 后端、生成源、prompt 文件、交付复制路径，且没有 programmatic/local/PIL/SVG/HTML/Canvas/matplotlib 等违规来源；检查 `frame.png` 叠背景后完整对位、线条/圆弧/填充干净，检查 `icons_contact_sheet.png` 无缺边；运行 `visual_compare_qa.py 源图 最终预览 --out-dir ...`，打开 `side_by_side.png`、`blend.png`、`diff_heatmap.png`，用 GPT 视觉对比源图与最终预览，逐项核对：图标无缺失、无重复叠影、无被切断、位置/大小贴合、文字可读；再用 placement_qa.py 在源图和预览图上画 bbox → 至少执行一轮 `layout.json` 回校（先修图标中心点/尺寸，再修文字框/字号/行距，最后修贴框文本的 frame_anchor 偏移）→ 对比整页预览；图标明显偏小/偏大、压字、离源位置漂移，或文字换行/位置不贴合，都不得交付
```

> 叠放顺序（从下到上）：背景 → 整体框架图(`frame`) → 元素图标(`icons`) → 文字(`texts`)。如果用户明确要求框架切分，则顺序为：背景 → 框架部件(`icons[]` 中 `role:"frame_part"`) → 元素图标(`icons`) → 文字(`texts`)。默认不使用 `shapes`；除非用户明确要求原生形状重建，否则 `shapes` 不得承载任何视觉内容。

## 关键命令

```bash
# B0 本次任务隔离目录（<task-slug> 用源图名或用户任务名的安全短名）
mkdir -p "$PWD/image2pptx_runs"
export RUN_ROOT="$(mktemp -d "$PWD/image2pptx_runs/$(date +%Y%m%d-%H%M%S)_<task-slug>_XXXXXX")"
mkdir -p "$RUN_ROOT/editable/01/icons" "$RUN_ROOT/editable/01/prompts" "$RUN_ROOT/out/preview"

# B1 探色（含绿则推荐改非绿底色）
python3 scripts/probe_palette.py "$RUN_ROOT/editable/01/slide-01.png"

# B5 去底（框架图 + 图标图都去底，保色保线）→ 默认保留整张 frame.png + 图标切片 → 合到灰底自检
python3 scripts/chroma_key.py --input "$RUN_ROOT/editable/01/frame_raw.png" --out "$RUN_ROOT/editable/01/frame.png" --preset frame-safe --scale 2 --force
python3 scripts/chroma_key.py --input "$RUN_ROOT/editable/01/icons_raw_1.png" --out "$RUN_ROOT/editable/01/icons_t_1.png" --preset icon-safe --scale 2 --force
python3 scripts/slice_grid.py "$RUN_ROOT/editable/01/icons_t_1.png" "$RUN_ROOT/editable/01/icons" --auto --pad 24 --contact-sheet --prefix ic
# 非绿底：--auto-key none --key-color "#ff00ff"；只有严格等分且元素居中时才用 --grid 4x4

# 可选：仅当用户明确要求框架切分/框架部件可移动时执行
mkdir -p "$RUN_ROOT/editable/01/frame_parts"
python3 scripts/slice_grid.py "$RUN_ROOT/editable/01/frame.png" "$RUN_ROOT/editable/01/frame_parts" --components --pad 0 --contact-sheet --prefix fp
python3 scripts/frame_parts_to_icons.py "$RUN_ROOT/editable/01/frame_parts/icons_manifest.json" --ref-width <源图宽px> --ref-height <源图高px> --out "$RUN_ROOT/editable/01/frame_parts/frame_parts_layout_icons.json"

# B8 合成 + 预览 + 摆放 QA
python3 scripts/layout_guard.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --strict
python3 scripts/placement_qa.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --slide-index 1 --out-dir "$RUN_ROOT/editable/01/qa-source-boxes"
python3 scripts/compose_pptx.py "$RUN_ROOT/editable/01/layout.json" "$RUN_ROOT/out/<task-slug>.pptx" --preview-dir "$RUN_ROOT/out/preview"
python3 scripts/placement_qa.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --slide-index 1 --preview "$RUN_ROOT/out/preview/slide_01.png" --out-dir "$RUN_ROOT/editable/01/qa-placement"
python3 scripts/visual_compare_qa.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/out/preview/slide_01.png" --out-dir "$RUN_ROOT/editable/01/qa-visual"
```

要点：
- **目录隔离**：每次转换必须先建唯一 `RUN_ROOT`，所有 `background.png`、`frame_raw.png`、`frame.png`、可选的 `frame_parts/`、`icons_raw_*.png`、`layout.json`、`imagegen-assets-manifest.json`、预览图和最终 PPTX 都在 `RUN_ROOT` 下；不要读写工作区固定同名目录。
- **imagegen 必须传图且作为 edit target**：每页每次生成 B2/B3/B4 之前，先 `view_image` 当前源图，让源图成为 imagegen 可用的可见编辑目标；prompt 中写“以刚刚显示的这张图片作为唯一编辑目标 / edit target，在它的基础上提取或擦除生成目标层”。不要只写 `/path/to/slide.png`，本地路径文本不是传图；也不要只把源图当作风格参考。
- **抠图底色**：默认纯绿 `#00ff00`；B1 报告含绿则改非绿（如品红 `#ff00ff`），B3/B4 出图底色与 B5 `--key-color` 同步。
- **图片层来源**：`background.png`、`frame_raw.png`、`icons_raw_*.png` 必须是 imagegen 生成图；不得来自 PPT 色块绘制、代码绘图或原图局部裁切。
- **不做历史源页搜索**：除非用户明确要求复用旧文件，否则不要为了转换图片而扫描当前目录或历史 `outputs/` 寻找相似源页；直接处理用户给出的当前图片。
- **B3 提示词固定**：框架图生成 prompt 固定为“生成一张图片，提取这张图片中的框架图，纯色背景，背景色值为XXXXXX，「框架图」= 原图里**除背景/图标/装饰/艺术字/普通文本外的一切**（容器轮廓与**底色填充/标题条/辉光**、分隔/连接线、**全部图表图形：折线/柱状/阶梯/饼图/坐标网格/趋势线**、缎带/装饰）→ 形状·大小·位置与原图 **1:1 一致**，保留原色与填充，别漏数据折线/装饰、别自己额外加空心线框、占位框；不要出现文字、不要出现图标；”。只替换 XXXXXX 为 B1 选出的背景色值。
- **框架图保真与默认整图**：框架图 = 除背景/图标/装饰/艺术字/普通文本外的一切（含**全部图表图形与装饰**），连同卡片**底色填充/标题条/辉光/渐变**一起提取——抠出的框架合到背景上应≈原图去掉普通文本、图标和艺术字，且与原图 **1:1 一致**。别漏标题下短线、卡片顶部色条、下划线、**数据折线/阶梯/饼图**、坐标轴/网格线、缎带装饰。**不能额外添加原图没有的占位框、线框**。去底后的 `frame.png` 默认作为整体框架视觉层放入 PPT；只有用户明确要求框架切分时，才按透明连通区域切成 `frame_parts/` 并以 `icons[] role:"frame_part"` 放入 PPT。
- **图标生成前先去重**：B3 之后必须看 `frame.png` 叠背景的预览，列出已经出现在 frame 的图标/装饰；B4 只生成 frame 中没有的元素。若某元素已经在 frame 里且位置正确，就不要再放进 `icons[]`，否则会出现重叠双影。
- **图标/艺术字切片保边**：一张图里生成多个图标可以保留，但必须留足空隙；切片优先 `slice_grid.py --auto --pad 24 --contact-sheet`，固定网格只在元素严格居中时用。必须查看 `icons_contact_sheet.png`：任一图标缺角、缺边、被裁半截、或 manifest 里任一 `edge_touch` 为 true，说明边框可能被切坏，必须重出图标表（加大格子/留白/拆成多张）或重切，不能交付。
- **图标缺失硬门禁**：最终预览必须和源图并排做视觉核对，源图中每个普通图标/装饰/艺术字必须满足二选一：已在 `frame` 中正确出现，或已在 `icons[]` 中正确摆放。不能因为图标层偏移、遮挡或难切就从最终 layout 删除图标后交付。
- **坐标契约硬门禁**：`ref_width/ref_height` 必须写源图实际像素尺寸；`source_bbox` 也必须是同一源图像素坐标。`view_image`、浏览器截图、PPT 预览 PNG 常常是缩略图，不是源图坐标系；若在缩略图上量到坐标，必须按 `scale_x=源图宽/缩略图宽`、`scale_y=源图高/缩略图高` 分别换回源图像素，并同步缩放 `size_px`。禁止把 2048px 预览坐标和 4096px 源图尺寸混用，尤其禁止 x 已按源图估、y 仍停留在缩略图高度，结果会让文字/图标全部挤到 PPTX 上半部分。`layout_guard.py --strict` 不负责判断视觉对位，视觉对位必须看最终合成预览与源图。
- **源图框视觉硬门禁**：`layout_guard` 通过只表示 bbox 与 fraction 数学一致，不表示 bbox 量对了对象。合成前必须打开 `qa-source-boxes/slide_01_source_boxes.png`，逐项确认文本/图标框覆盖源图真实位置；像“关键动作”这种文本框若圈到上方流程区而非底部按钮，即使 guard 通过也必须重测。
- **框架锚点回校硬门禁**：`source_bbox` 对了仍可能错位，因为 B3 的 `frame.png` 是 imagegen 生成层，标题条、按钮、底栏可能相对源图有轻微纵向/横向漂移。凡是贴在框架上的文本（分区标题、按钮文字、底栏总结、页脚横幅、卡片标题）必须在最终预览里按 `frame.png` 的视觉锚点再次回校：以标题条/按钮/底栏的中心线、内边距或框内留白为准，必要时整体下移/上移几个到几十个源图像素，并记录 `frame_anchor` 与 `dx/dy_px`。这一步在 `layout_guard --strict` 之后执行。
- **摆放坐标精度**：默认用比例坐标。先在源图上量 `x/y/w/h` 像素 bbox，再按 `x/ref_width`、`y/ref_height`、`w/ref_width`、`h/ref_height` 写入 `layout.json`，并设置 `units:"fraction"`。保留 `source_bbox:[x_px,y_px,w_px,h_px]` 方便 QA。
- **图标/艺术字尺寸定位**：**对照原图逐个量出 `x/y/w/h` 像素 bbox，再换算成比例写进 layout.json**（manifest 只有素材表尺寸，没有原图位置；用宽高比定 h、别给方形）；摆放后必须跑 `placement_qa.py`，在源图和预览图上看 bbox 是否压准，不能只看最终 PPT 预览。
- **图标预览回校硬门禁**：首次预览后必须逐个图标检查“预览视觉 bbox vs 源图视觉 bbox”。若偏小/偏大，按中心点锚定调整：`new_x = cx - new_w/2`、`new_y = cy - new_h/2`；不得只改 `w/h` 导致图标漂移，也不得按切片素材原始尺寸直接摆。图标与文字重叠时，优先恢复源图相对位置；若源图无重叠而预览重叠，必须改图标或文字 bbox 后重跑 B8/B9。
- **最终视觉对位硬门禁**：必须打开 `qa-visual/side_by_side.png`、`qa-visual/blend.png`、`qa-visual/diff_heatmap.png`，用 GPT 视觉判断合成 PPTX 预览里的文字和图标是否与原始 PPT 图片对应。页面内容只在上半页、下半页或局部区域都可以；判断标准是源图中对应对象的位置/大小/相对关系是否一致，而不是元素覆盖了页面多少高度。
- **生成证据**：每页必须包含 `imagegen-assets-manifest.json`，记录背景、框架图、图标表的真实 imagegen 生成源路径、后端和 prompt 文件；缺失、`prompt_file:null`、或显示程序生成来源即不合格。
- **文字抽取**：用 GPT 视觉直接看原图，按 `texts[]` JSON schema 输出逐段文本和像素位置样式；禁止把外部 OCR 输出当最终文本结果。长文本框 bbox 要覆盖原文字整块，不要用视觉中心点估算。
- **文字位置回校**：最终预览里的文本必须与源图的文本块左/中/右边界、首行基线、换行节奏和相邻图标间距一致。若可编辑字体与源图手写字体宽度不同，优先微调 `w/h` 比例、`size_ratio/size_pct`、`line_spacing` 和 `align`，不要为了避开错位把图标删除或缩小到不符合源图。文字回校顺序固定为：先定 `bold` / 字号 / `line_spacing`，再修 bbox；否则全粗体或行距变化会改变字宽、换行和视觉高度，导致刚校准过的位置再次漂移。
- **坐标/字号**：layout.json 推荐 `units:"fraction"`；字号推荐 `size_ratio = 源图实际文字高度像素 / ref_height`，compose 时换算为 `pt = size_ratio × (页高in×72)`。旧字段 `size_px`/`size` 仍兼容，但 `size_px` 必须是源图实际像素，不是 2048px 预览测量值；若需要正常 PowerPoint 号数，直接写 `size` 绝对 pt 更稳。反推公式：`size_px = 目标pt × ref_height / (页高in×72)`。
- **文字粗细硬门禁**：`bold` 默认 `false`；不得为了“更像截图”把所有 `texts[]` 都设成 `bold:true`。只有标题、按钮标题、重点数字/关键词按原图加粗；普通正文和说明段默认常规字重。`layout_guard --strict` 会对疑似全粗体正文报错，除非原图确实全粗体并显式写 `allow_all_bold_text:true`。
- 多页：把每页 `slides[]` 汇进一个 deck.json 一次合成整本。
- 交付：最终答复必须给出可点击的最终 `.pptx` 绝对路径；若另存了便捷副本，也同时给出 RUN_ROOT 内原始输出路径和副本路径。

## 脚本与依赖

| 脚本 | 干嘛 |
|---|---|
| `scripts/probe_palette.py` | 探测某页是否含绿，推荐安全抠图底色 |
| `scripts/chroma_key.py` | **保色保线/保形**抠图：绿幕(或指定底色)变透明，不褪色；预设会增强抗锯齿边缘并修补细小 alpha 断点，配合 `--scale 2` 超采样，避免横竖线和圆弧被抠毛 |
| `scripts/slice_grid.py` | `--grid N×N` 或 `--auto` 把透明图标表切成单个图标；可选 `--components` 按透明连通区域把框架图切成可移动框架部件；产出 manifest |
| `scripts/frame_parts_to_icons.py` | 可选框架切分辅助：把 `frame_parts/icons_manifest.json` 的 bbox 映射到源图坐标，生成可直接并入 `layout.icons[]` 的 `role:"frame_part"` 条目，保证框架部件按原 `frame.png` 布局拼回 |
| `scripts/layout_guard.py` | 合成前校验坐标契约：源图实际尺寸、`ref_width/ref_height`、`source_bbox`、`x/y/w/h` 是否一致；可把同宽高比缩略图坐标归一化回源图像素；不做页面覆盖高度启发式判断 |
| `scripts/placement_qa.py` | 把 layout 的图标/文本 bbox 画回源图和预览图，生成摆放 QA 标注图与源/预览叠图 |
| `scripts/visual_compare_qa.py` | 把源图和最终 PPTX 预览统一尺寸后输出并排图、叠图、差异热图和诊断指标，用于 GPT 视觉核对文字/图标是否真正对位 |
| `scripts/compose_pptx.py` | 把 背景+整体框架图(frame)+图标(icons)+文字(texts) 按 layout/deck.json 合成可编辑 .pptx，`--preview-dir` 出预览；用户要求框架切分时也支持 frame_parts；默认不使用 shapes 承载视觉内容 |

- 依赖：`python3` + `python-pptx`、`Pillow`、`numpy`（缺就 `pip3 install python-pptx pillow numpy`）。
- 输入若是"图片型 PPT"，通常由 **GordenImagePPTGen** 产出；要一键"先出图再转可编辑" → 用 **GordenSuperPPTSkill**。

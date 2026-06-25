# 功能 B：PPT 图片 → 可编辑 PPTX 流水线

把每张 PPT 图片拆成多层再合成可编辑 .pptx（从下到上叠放）：

```
背景图(复刻) + 整体框架图(绿幕抠图,默认不切分) + 元素图标/装饰(绿幕抠图,切片) + 文字(GPT视觉提取)
```

> 🔴 **强制四层，缺一不可（核心铁律）**：**背景图 → 整体框架图 → 元素图标 → 文本**。这四步是功能 B 的本质，**任何一页都必须实打实地用 imagegen 生成 B2 背景图、B3 框架图、B4 元素图标图**，再绿幕抠图，默认把整张透明 `frame.png` 作为框架视觉层 compose。只有用户明确要求"框架切分/框架部件可移动/拆成一块块"时，才把框架图按透明区域切成 `frame_parts/` 后 compose。
> **严禁的退化做法**：① 直接拿原图当背景叠文字（会双重文字）；② 用原生 `shapes`、PPT 填充色块、线条、箭头、表格或图表组件重画背景/卡片/框架/图表；③ 从原图裁切局部当作车辆、图标、框架或背景素材；④ 用 Python/PIL、SVG、HTML、Canvas、matplotlib 画图片层；⑤ 省略框架/图标。
> 背景图、框架图、图标图都必须来自 **imagegen  提取式生成**。`chroma_key.py` 只负责给生成图去底；`slice_grid.py` 只允许切分 **imagegen 生成并已去底的图标表**。只有用户明确要求框架切分时，才允许切分已去底的 `frame.png`；不得切原始幻灯片截图。
> **直接转换原则**：用户给出图片要转可编辑 PPTX 时，不要先扫描当前目录、历史输出或其它项目来寻找相似源页。直接把当前图片作为唯一源图，按 B1-B9 提取背景、框架、图标和文字并新建 PPTX。只有用户明确要求复用旧素材、续做历史输出或指定已有源文件时，才读取对应历史文件。
> **任务隔离原则**：每次转换必须先创建唯一 `RUN_ROOT`，所有本次文件都写入该目录；不得直接使用工作区固定 `editable/01`、`out/`、`qa/`、`slide-01/`，否则同一文件夹内多个转换任务会互相读错或覆盖。
> **生成证据硬门禁**：B2/B3/B4 必须在 `imagegen-assets-manifest.json` 中记录真实 imagegen 调用证据。`backend` 必须是 imagegen 类后端，`generated_source` 必须指向或描述真实生成结果，`prompt_file` 必须指向本页使用的提示词文件，`copied_to` 必须是交付目录内对应图片。若 manifest 显示 `programmatic`、`local layer generator`、`PIL`、`SVG`、`HTML`、`Canvas`、`matplotlib`、`screenshot renderer`、`null prompt_file` 等非 imagegen 生成迹象，本页转换失败。
> **imagegen 传图 / edit target 硬门禁**：Codex 内置 `image_gen` 生成 B2/B3/B4 时，必须先用 `view_image` 打开当前页源图，让这张图成为当前对话里可见的 **edit target**，然后再调用 `image_gen`。Prompt 必须明确写“以刚刚显示的这张图片作为唯一编辑目标 / edit target，在它的基础上提取或擦除生成目标层”。禁止只把源图当作风格参考图；也禁止只在 prompt 里写本地文件路径来冒充传图：路径文本不会自动把图片传给 imagegen，模型会凭描述猜，框架图和图标图会跑偏。多页任务必须一页一页处理，每页生成前重新 `view_image` 当前源图。

**一张一张处理**。下面是单页流程；多页时把每页 `slides[]` 汇总进一个 `deck.json` 一次合成。

---

## B0. 创建任务隔离输出目录

在任何复制、出图、抠图、合成之前，先创建本次任务唯一根目录：

```bash
mkdir -p "$PWD/image2pptx_runs"
export RUN_ROOT="$(mktemp -d "$PWD/image2pptx_runs/$(date +%Y%m%d-%H%M%S)_<task-slug>_XXXXXX")"
mkdir -p "$RUN_ROOT/editable/01/icons" "$RUN_ROOT/editable/01/prompts" "$RUN_ROOT/out/preview"
```

规则：
- `<task-slug>` 用源图文件名或用户任务名的安全短名；`mktemp -d` 负责追加随机后缀，确保同一秒连续任务也不撞目录。
- 多页任务使用 `$RUN_ROOT/editable/01`、`$RUN_ROOT/editable/02` ...；最终 deck、预览、QA 仍放在同一个 `$RUN_ROOT` 下。
- `layout.json` 优先省略 `assets_dir`，让 `compose_pptx.py` 自动以 layout 所在目录解析 `background.png`、`frame.png`、`icons/...`；若用户明确要求框架切分，也会解析 `frame_parts/...`。若必须写 `assets_dir`，必须写绝对页目录，例如 `"$RUN_ROOT/editable/01"`，不要写 `"editable/01"`。
- manifest 的 `copied_to`、`prompt_file` 和透明输出路径都写 `RUN_ROOT` 下的绝对路径，方便 QA 判断没有串到旧任务。

---

## B0a. 传图：把当前页源图作为 edit target

每页进入 B2/B3/B4 前，必须先调用 `view_image` 打开当前页源图，例如 `$RUN_ROOT/editable/01/slide-01.png`。随后调用 `image_gen` 时，prompt 写“以刚刚显示的这张图片作为唯一编辑目标 / edit target，在它的基础上提取或擦除生成目标层”。这一步是传图并指定编辑目标，不是描述图片，也不是只提供风格参考。

禁止做法：
- 只在 prompt 中写本地路径，例如 `/path/to/slide-01.png`。
- 只把源图当作 reference/style image，让模型凭风格和文字清单复画。
- 同时显示多页后用“第 1 页/第 2 页”含糊引用。
- 未查看当前源图就让 imagegen 根据文字清单猜背景、框架或图标。

任一 B2/B3/B4 产物明显没有基于当前 edit target 提取，本页该层失败，必须重出。

---

## B1. 探色：决定本页抠图底色

```bash
python3 scripts/probe_palette.py "$RUN_ROOT/editable/01/slide-01.png"
```

- 输出 `recommended_key: #00ff00` → 本页用纯绿抠图（默认，效果最好）。
- 若该页含较多绿色，会推荐非绿底色（如 `#ff00ff` 品红、`#ff7a00` 橙、`#ff0033` 红）。**记住这个底色**，B3/B4 出图和 B5 去底都要用它。

> 原因：默认绿幕去底，若框架/图标本身或页面就是绿色，会被一起抠掉。含绿页改用页面里没有的鲜艳色当底色。

---

## B2. 复刻干净背景

用 imagegen  **复刻**本页背景，得到 `$RUN_ROOT/editable/01/background.png`（16:9，与原图同比例）。

硬门禁：
- `background.png` 必须是图像模型生成图。
- 禁止用 PPT 页面填充色、原生矩形、渐变色块、代码绘制或裁切原图来冒充背景。
- 生成源图路径、后端、prompt 文件必须写入本页 `imagegen-assets-manifest.json`；没有真实 imagegen 记录不得交付。

推荐做法（二选一）：

- **复刻式（默认，更干净）**：把当前可见源图作为 **edit target**，在它的基础上擦除文字、图标、框架、卡片和占位块，生成同款空背景。提示词：

```text
复刻这张 PPT 幻灯片的背景：保持完全一致的底色、渐变、光影、纹理和大面积的背景装饰色块，
但生成一张完全空白的背景——不要任何文字、不要任何图标、不要任何卡片/方框/占位块、不要任何分隔条。
16:9 横版，与原图同尺寸。
```

- **擦除式（背景是照片/复杂纹理时）**：对原图做 edit/inpaint，移除所有文字、图标、框架、卡片、装饰块，补全背景。

> 背景里**绝不**保留框架/卡片/容器/分隔线/占位块——这些**统一进 B3 框架图**（imagegen 纯色底出图→抠图→默认整张 `frame.png` 放入 PPT；用户明确要求时才切成框架部件）。
> Codex 用内置 `imagegen`；要 edit 本地图先 `view_image`。生成图记得复制到输出目录并保留默认生成目录原图。详见 [`runtime-notes.md`](runtime-notes.md)。

---

## B3. 提取框架结构（全幅透明层）

🟦 **框架图的定义（先记牢这一条）**：一页里**「背景图」「元素图标/装饰/艺术字」「普通文本」之外的所有图像，统统算框架图，一次性提取到这一层**。包括但不限于：容器/卡片的轮廓与**底色填充面板**、彩色标题条、分区/分隔线、标题下短分割线、下划线、连接线与指示箭头、节点圆点、药丸/标签边框、**所有图表的全部图形**（柱状/折线/阶梯/饼图/环形/雷达/鱼骨/莫比乌斯等的坐标轴、网格线、柱体、折线、数据点、扇区、填充、趋势线）、缎带/横幅、以及任何装饰线条与色块。

🟨 **艺术字归类规则**：艺术字属于 B4 图标/装饰层，不属于 B7 普通文本层。判断标准：带有渐变颜色、书法/笔刷造型、形变、描边/阴影/纹理、徽章式排版，或普通字体无法直接写出的文字。例如封面“灵芝”这类大字必须作为装饰元素提取成图片，不能用普通文本框替代。

🟥 **三条硬要求**：
> 0. **必须用 imagegen 提取式生成**：`frame_raw.png` 必须来自图像模型生成，不能用 PPT shapes/色块/线条、代码绘图或裁原图局部替代。生成源图路径必须写入 `imagegen-assets-manifest.json`。
> 0a. **必须留证据**：框架图 prompt 要保存为文件，manifest 要记录 imagegen 后端、生成源、prompt 文件和交付复制路径；程序绘图生成的框架图一律不合格。
> 1. **不漏**：动手前把原图里每一个"非背景、非图标、非文字"的图形列成清单再提取——尤其别漏**数据折线/柱状/阶梯/饼图等图表图形**和各种**装饰元素**（典型漏项：某页右侧的"阶梯/折线趋势图"、缎带、连接箭头、坐标网格）。漏了 = 不合格。
> 2. **与原图严格一致（1:1）**：框架图与原图里的框架必须**形状、大小、位置一模一样**。提取后**合到背景上应当几乎等于原图去掉文字和图标**；逐元素对照原图核对边框粗细/长度/弧度/颜色/坐标。

⚠️ **框架要"完整还原"，不是"光秃线框"**：要连同卡片的**底色填充、彩色标题条、辉光/阴影、渐变**一起提取——它们是框架的一部分。上一轮把框架做成只剩灰色细 outline（丢了填充和辉光），导致成品比原图"空、廉价、远不如预期"。正确目标：抠出的框架合到背景上应当**几乎等于原图去掉文字和图标**。

⚠️ **不要漏掉小装饰线**：标题下的短强调分割线、卡片顶部的彩色短条、下划线、节点小圆点、药丸/标签的边框、坐标轴与网格线——这些都属于框架，必须一并提取。先把原图所有"非文字、非图标"的线条/边框/**面板/填充**逐一列清，再写进提示词。

提示词（固定模板；只允许替换背景色值 XXXXXX）：

```text
生成一张图片，提取这张图片中的框架图，纯色背景，背景色值为XXXXXX，「框架图」= 原图里**除背景/图标/装饰/艺术字/普通文本外的一切**（容器轮廓与**底色填充/标题条/辉光**、分隔/连接线、**全部图表图形：折线/柱状/阶梯/饼图/坐标网格/趋势线**、缎带/装饰）→ 形状·大小·位置与原图 **1:1 一致**，保留原色与填充，别漏数据折线/装饰、别自己额外加空心线框、占位框；不要出现文字、不要出现图标；
```

`XXXXXX` 默认为 `#00ff00`。若 B1 探色发现原图有绿色或绿色会与内容冲突，只能把 `XXXXXX` 改为原图没有的纯色值，例如 `#ff00ff`、`#8000ff`；不要改模板其它文字，不要追加英文语义清单。

存为 `$RUN_ROOT/editable/01/frame_raw.png`（在 B5 去底成 `frame.png`）。

> 补救：若框架图仍漏掉某些细线（短分割线、下划线等），优先改提示词并重出 `frame_raw.png`。最终 PPT 默认不得用 `shapes` 补线或补色块，除非用户明确要求原生形状重建。

> 不论简单还是复杂，**容器/卡片/图表框架一律走 imagegen 生成的整张框架透明图（B3）**。不要用 PPT shapes、PPT 填充色块或代码绘图替代框架图。

---

## B4. 提取图标/装饰/艺术字到等分方格网

目标：用 imagegen 把本页**所有图标、装饰元素和艺术字**生成到一张**方形**图里，在抠图底色上**等分成 N×N 个相同大小的方格**，每格一个元素，居中、四周留白，便于切片抠图。

先做去重审查（强制）：

1. 把 B3 的 `frame.png` 叠到 `background.png` 上生成预览，和源图并排看。
2. 用 GPT 视觉列两张清单：`source_icon_inventory`（源图里全部图标/装饰/艺术字）与 `already_in_frame`（已经出现在 frame 里的图标/装饰）。
3. B4 prompt 只生成 `source_icon_inventory - already_in_frame` 的元素；已经在 frame 中且位置正确的元素，不再生成、不再写入 `layout.icons[]`。
4. 如果 frame 里误含某图标但位置/样式不对，优先重出 frame，把该图标从 frame 移除，再在 B4 生成；不要让同一个图标同时存在于 frame 和 icons。

> 这一步是硬门禁：同一图标不能同时在 `frame.png` 与 `icons[]` 出现，否则最终会有重叠双影。不能因为图标多或难切，就跳过图标层或把 `icons[]` 清空交付。

硬门禁：
- `icons_raw_*.png` 必须来自图像模型生成。
- 禁止从原始幻灯片截图裁切图标、车辆、插画、装饰块或艺术字。
- 禁止用代码绘制图标表。
- 生成源图路径、后端、prompt 文件必须写入本页 `imagegen-assets-manifest.json`；程序绘图生成的图标表一律不合格。

提示词（用户原文 · verbatim，其余按实际情况调整）：

> 我们生成一张图片，提取这张PPT图片当中所有的图标元素和装饰元素，纯绿色背景，不要文字，不要背景条。

在此基础上补全：

```text
要求：
- 方形画布，纯<底色>背景（底色 = B1 推荐色，默认 #00ff00 纯绿；含绿页改为 #ff00ff 等）。
- 把元素严格排成 <N>×<N> 等分网格，每个格子大小完全相同且为正方形，元素在各自格子内居中并留出均匀边距；任何笔画、阴影、外轮廓都不能接触格子边缘。
- 只要图标/装饰元素/艺术字本身，**不要普通文字、不要背景条、不要卡片底框**。艺术字中的字符必须作为图形保留，例如“灵芝”保留字形、渐变和笔画造型。
- 元素之间不要重叠、不要相连。
- 忠实还原每个图标的造型、颜色、风格（颜色不要用到<底色>）。
- 若元素较多，不要挤在一张图里；宁可拆成多张图标表，也要保证每个元素完整、有足够透明边距，避免切片时齿轮、火箭、箭头等被裁掉。
```

数量与网格规则：

- **小图标**：4×4（每张 16 个）。元素多了就出**多张**。例：一页有 32 个图标 → 出 2 张 4×4 的绿底图。
- **大装饰图 / 艺术字**（不是小图标的装饰性图片或装饰文字）：用 2×2 或单独一张 1×1，把尺寸生成得大一些。
- 同一页可同时有"图标图(4×4)"和"装饰图(2×2)"多张。
- 元素含绿时，整页底色按 B1 改非绿，避免抠不干净。

每张存为 `$RUN_ROOT/editable/01/icons_raw_1.png`、`icons_raw_2.png`…

---

## B5. 去底 + 图标切片（框架默认不切分）

**首选本技能自带的 `scripts/chroma_key.py`（保色保线）**，把**框架图**和**图标图**的底色变透明。框架图默认保留为整张透明 `frame.png`；图标图按透明空隙或网格切片。只有用户明确要求"框架切分/框架部件可移动/拆成一块块"时，才执行可选框架切分分支：

```bash
# 框架图去底 → 透明框架图（保留填充/辉光/细线，绝不褪色）：
python3 scripts/chroma_key.py --input "$RUN_ROOT/editable/01/frame_raw.png" --out "$RUN_ROOT/editable/01/frame.png" --preset frame-safe --scale 2 --force

# 图标图去底（默认自动识别绿底）：
python3 scripts/chroma_key.py --input "$RUN_ROOT/editable/01/icons_raw_1.png" --out "$RUN_ROOT/editable/01/icons_t_1.png" --preset icon-safe --scale 2 --force
# 非绿底（B1 推荐了别的色）则显式指定：
# python3 scripts/chroma_key.py --input ... --out ... --auto-key none --key-color "#ff00ff" --force

# 图标切成单个并裁掉透明边（只允许切 imagegen 生成的图标表；网格按 B4 实际用的 N×N）：
python3 scripts/slice_grid.py "$RUN_ROOT/editable/01/icons_t_1.png" "$RUN_ROOT/editable/01/icons" --auto --pad 24 --contact-sheet --prefix ic1
python3 scripts/slice_grid.py "$RUN_ROOT/editable/01/icons_t_2.png" "$RUN_ROOT/editable/01/icons" --auto --pad 24 --contact-sheet --prefix deco

# 若 AI 没排成完美网格 / 大装饰没居中（常见）：用 --auto 按透明空隙自动分割（更稳健）
python3 scripts/slice_grid.py "$RUN_ROOT/editable/01/icons_t_1.png" "$RUN_ROOT/editable/01/icons" --auto --pad 24 --contact-sheet --prefix ic1

# 可选：仅当用户明确要求框架切分/框架部件可移动时执行
mkdir -p "$RUN_ROOT/editable/01/frame_parts"
python3 scripts/slice_grid.py "$RUN_ROOT/editable/01/frame.png" "$RUN_ROOT/editable/01/frame_parts" --components --pad 0 --contact-sheet --prefix fp
python3 scripts/frame_parts_to_icons.py "$RUN_ROOT/editable/01/frame_parts/icons_manifest.json" --ref-width <源图宽px> --ref-height <源图高px> --out "$RUN_ROOT/editable/01/frame_parts/frame_parts_layout_icons.json"
```

> ⚠️ **抠图保真铁律（务必遵守，否则会"变色严重 + 丢线"）**：
> - **保色**：内部不透明像素的颜色必须 100% 保留。红/藏青/灰/白绝不能被褪成灰白。`chroma_key.py` 的 despill 只对"绿色主导"的像素生效，对正常内容是 no-op。
> - **保线/保形**：默认 `--contract 0`、不做强腐蚀，1px 细线/分割线/辉光必须留住。`frame-safe` / `icon-safe` 会用 `--alpha-gamma < 1` 增强半透明边缘，并用二值 `--alpha-close` 只修补小断点，不直接对灰度 alpha 做 Max/Min，避免横线竖线不齐、圆弧残缺。
> - **超采样**：框架图和图标图默认加 `--scale 2`，先放大再抠，生成更高分辨率透明 PNG；PPT 放置时按 bbox 缩回原尺寸，直线和圆弧会比原尺寸直接抠图更平滑。若文件过大可降回 `--scale 1.5`，但不要低于 1。
> - **不要**用通用绿幕器的 `--soft-matte --despill --edge-contract` 这类激进组合去抠扁平信息图——那正是上一轮"红色图标被抠成灰白、框架线条消失"的元凶。
> - 仅当确有 1px 绿边残留时，才加 `--contract 1`（谨慎，会吃掉极细线）；不要为了“边缘干净”给框架图加大 `--feather`，这会让直线和圆弧发虚。
> - 抠完**务必把透明图合成到灰底 PNG 自检**一眼：颜色对不对、线/辉光在不在、有无残边。

- 框架图默认不切片：`frame.png` 是最终 layout 的整体框架视觉层，写入 `"frame":"frame.png"`。这样最稳地保持框架线条、圆弧、面板填充和相互位置不被切分误差影响。
- 可选框架切片：只有用户明确要求框架切分/框架部件可移动时，才用 `slice_grid.py --components` 按透明连通区域切成 `frame_parts/`，每个切片相互独立、可移动；此时最终 layout 不再直接引用整张 `frame`，改用 `icons[] role:"frame_part"`。
- 图标表推荐用 **`--auto --pad 24 --contact-sheet`** 按透明空隙自动分割，适合 AI 图标表常见的轻微不齐；只有元素严格居中在等分格内时才用 `--grid N×N`。两种都会写出 `icons/icons_manifest.json`（文件名、行列、尺寸、宽高比、edge_touch），并可输出 `icons_contact_sheet.png`。
- 可选切分时，`frame_parts/icons_manifest.json` 的 `bbox` 是框架切片在 `frame.png` 里的坐标；B6 要把它按 `frame.png` 尺寸映射到源图 `ref_width/ref_height` 后写入 `layout.icons[]`。
- 可选切分时，框架部件不要使用 `--square`：它会给切片增加额外透明边，破坏 bbox 回放。框架切片应保持 cutout 尺寸等于 bbox 尺寸。
- 必须查看 `icons_contact_sheet.png`：任一图标被切掉一部分、缺角、缺边、只剩半个、阴影/外轮廓被截断，或 manifest 里任一 `edge_touch` 为 true，均视为 B5 失败。处理顺序：先用更大留白/更少格子重出 `icons_raw_*.png`；再用更大的 `--pad` 重切。禁止从原图或全幅原位图里手工裁局部来补救。
- 切出的图标命名只表网格位，真实摆放位置在 B6 决定。
- 兜底：无 `scripts/chroma_key.py` 时才用 Codex 的 `remove_chroma_key.py`，且**不要**叠加 `--soft-matte --despill`（会褪色），优先纯 `--auto-key border`。

### B5a. 生成证据检查（必须在合成前执行）

合成前读取本页 `imagegen-assets-manifest.json`，逐项检查：

- `background` / `frame` / `icons` 三类资产都存在记录。
- 每条记录的 `backend` 是 imagegen 类后端。
- 每条记录都有非空 `generated_source`、`copied_to`、`prompt_file`。
- `prompt_file` 指向的提示词文件存在，且内容对应本页当前源图与该层目标。
- 记录中不得出现 `programmatic`、`local layer generator`、`PIL`、`SVG`、`HTML`、`Canvas`、`matplotlib`、`screenshot renderer`、`prompt_file:null` 等程序绘图或无提示词证据。

任一项失败，停止合成并重做 B2/B3/B4。不得用程序绘图结果临时补交。

### B5b. 框架图/图标完整性检查（必须在合成前执行）

默认读取 `icons/icons_manifest.json` 并查看 `icons_contact_sheet.png`；同时把透明 `frame.png` 合成到灰底/背景上检查线条、圆弧、面板填充和透明边缘。若用户明确要求框架切分，再额外读取 `frame_parts/icons_manifest.json` 并查看 `frame_parts/icons_contact_sheet.png`：

- 默认整张 `frame.png` 必须视觉完整：框架线条不断裂、圆弧不残缺、面板填充/标题条/辉光不丢失，合到背景上位置应与源图 1:1 贴合。
- 可选切分时，框架部件必须由透明区域自然分割得到；一个切片里若仍包含多个互不相连的大框架块，或一个框架块被错分成多个无法独立还原的碎片 → 不交付，重出或重切。
- 图标 `edge_touch` 任一方向为 true → 不交付，重出或重切。框架部件如果本来贴近页面边缘，可在 QA 备注里保留，但必须视觉完整、不缺边。
- 图标索引图中任何元素被切掉、缺边、错分成多个碎片、多个图标粘连成一个 → 不交付，重出或重切。
- 图标索引图中的元素数量必须覆盖 B4 的缺失元素清单；少一个都要补出新图标表。
- 如果某元素已在 frame 中出现且不应单独摆放，在 `placements.json` 标记为 `covered_by_frame:true`，不要放进 `layout.icons[]`。

---

## B6. 定位框架图与图标 → 写 layout.json

默认最终 `$RUN_ROOT/editable/01/layout.json` 直接使用整张透明 `frame.png` 作为框架视觉层：

```json
{
  "background": "background.png",
  "frame": "frame.png",
  "icons": [],
  "texts": []
}
```

这样能最大限度保持框架整体线条、圆弧、面板填充、标题条、辉光和相互位置一致。再为每个普通图标确定它在原页中的位置和大小。卡片/容器已在 `frame.png` 里，无需再用原生形状重画，也无需默认切成 `frame_parts`。

### 可选：用户要求框架切分时

如果用户明确要求框架切分/框架部件可移动，则不要在最终 layout 使用整张 `frame` 视觉层；改为把 `frame_parts/` 的每个切片作为 `icons[]` 条目放回原位，并标记 `role:"frame_part"`。

**拼回原 frame 布局的保证**：`slice_grid.py --components` 在切出每个框架部件时，会在 `frame_parts/icons_manifest.json` 记录该切片来自 `frame.png` 的原始 `bbox:[l,t,r,b]`。`frame_parts_to_icons.py` 用这个 bbox 生成 `layout.icons[]`，所以每个切片按自己的原始位置和原始尺寸放回。所有切片叠加后，应当重建出原来的 `frame.png` 视觉布局；这不是手动估算。

可选框架部件 bbox 换算规则（默认输出比例坐标）：
- 读取 `frame_parts/icons_manifest.json` 中每个切片的 `bbox:[l,t,r,b]` 和 `size:[frame_w,frame_h]`。
- 若 layout 使用 `units:"fraction"`：`x=l/frame_w`、`y=t/frame_h`、`w=(r-l)/frame_w`、`h=(b-t)/frame_h`。
- 同时保留 `source_bbox:[l/frame_w*ref_width, t/frame_h*ref_height, (r-l)/frame_w*ref_width, (b-t)/frame_h*ref_height]` 作为源图像素 QA 记录。
- 写入 `icons[]`：`{"file":"frame_parts/fp_001.png","role":"frame_part","x":...,"y":...,"w":...,"h":...,"source_bbox":[x,y,w,h]}`。
- 推荐直接运行脚本生成条目：`python3 scripts/frame_parts_to_icons.py "$RUN_ROOT/editable/01/frame_parts/icons_manifest.json" --ref-width <源图宽px> --ref-height <源图高px>`，再把输出的 `frame_parts_layout_icons.json` 内容并入 `layout.json` 的 `icons[]` 最前面。

> 📐 **必须记录每个图标在原图中的实际包围盒（核心要求，常被漏做）**：`slice_grid.py` 的 manifest **只记录素材表里每个图标的尺寸/宽高比，不含它在原幻灯片里的位置**。所以 B6 必须**看原图逐个量出每个图标在源图实际像素坐标系里的 `x, y, w, h` bbox，然后换算成比例写进 layout.json 的 `icons[]`**——放回任意 PPT 尺寸时大小/位置才能按比例一致。建议维护一张对照表：`图标文件 → 原图 x/y/w/h(px) → x/y/w/h(fraction)`（可顺手记进 manifest 旁的一个 `placements.json`）。**别只靠目测随手摆**，那会出现"图标偏大/偏小/错位"。

- 坐标默认用 **比例**：`units:"fraction"`。先量源图像素 bbox，再换算：`x=x_px/ref_width`、`y=y_px/ref_height`、`w=w_px/ref_width`、`h=h_px/ref_height`。`ref_width/ref_height` 仍写入 layout，供 QA、`source_bbox` 和旧字段换算使用。
- **坐标契约（合成前硬门禁）**：
  - `ref_width/ref_height` 必须等于当前页源图文件的实际像素尺寸，例如源图是 4096×2286，就写 `4096/2286`。
  - `source_bbox` 必须使用同一张源图的实际像素坐标，不能是 `view_image` 界面缩略图、预览 PNG、浏览器截图或人工缩放图上的坐标。`view_image` 常会把 4096×2286 显示成 2048×1143；此时量到的 `x/y/w/h/size_px` 必须全部乘以 2，不能只修 x 或只修 y。
  - 若为了方便在同宽高比缩略图上量测（例如 2048×1143），必须先按 `scale_x=源图宽/缩略图宽`、`scale_y=源图高/缩略图高` 分别换回源图坐标，或运行：
    `python3 scripts/layout_guard.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --fix-ref-to-source --fix-fractions --in-place`
    然后重新复查关键文本/图标位置。
  - 合成前必须运行：
    `python3 scripts/layout_guard.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --strict`
    任何 `ref_width/ref_height` 与源图尺寸不一致，或 `source_bbox` 与 `x/y/w/h` 不一致，都不得进入 B8。`layout_guard.py` 不用页面覆盖高度判错；有些真实页面本来只在上半页或局部区域有文字/图标。
  - `layout_guard.py` 只校验坐标契约，不能判断 bbox 是否圈住了正确对象。它通过以后，还必须打开 `qa-source-boxes/slide_01_source_boxes.png` 做视觉复核：每个框必须覆盖源图真实文本/图标，而不是覆盖到同一面板里的其它行、其它按钮或空白位置。
- **图标尺寸要对照原图逐个核准**（上一轮反馈"图标大小不合适"）：
  - 先在源图像素坐标里量宽高；若只量到宽度，用 manifest 的宽高比定 `h_px = w_px / aspect`（保持图标不变形）；再写 `w=w_px/ref_width`、`h=h_px/ref_height`。切勿随手给方形 w=h。
  - 小徽标图标（要点前的 badge）通常 `w≈40~90px`（以 2134px 宽源图计）；功能区图标 `w≈90~170px`；大艺术字/插画另量。
  - 摆放后必须跑 `placement_qa.py`，在源图和预览图上画框核对：图标不能比原图明显偏大/偏小、不能压住文字或溢出卡片。
- **首次预览后必须做图标回校**：
  - 把 `$RUN_ROOT/out/preview/slide_01.png` 与源图并排看，逐个记录 `source_bbox`、`preview_bbox`、`delta_center_x/y`、`scale_w/h` 和处理动作，写入 `$RUN_ROOT/editable/01/icons/placements.json` 或旁边的 `placement_fix_notes.json`。
  - 若图标整体偏小/偏大，按源图 bbox 中心点缩放，不要只改 `w/h`。计算方式：`cx = x + w/2`、`cy = y + h/2`，改尺寸后写回 `x = cx - new_w/2`、`y = cy - new_h/2`。
  - 若切片素材四周透明边距较大，预览视觉 bbox 会比 layout bbox 小；此时应放大 layout 的 `w/h` 或重切图标，不要接受“框对了但图标肉眼偏小”的结果。
  - 若同一张自动切片里混入多个小图标，导致无法单独贴原位，必须重切或重出图标表；不得把组合切片硬塞到页面上压住文字。
  - 图标与文字的相对位置以源图为准：源图没有重叠而预览重叠时，先修图标中心点和尺寸，再修文字框；不能通过删除图标、缩得过小或移动到无关空白处来规避。
- 默认框架走整张 `frame.png`；只有用户明确要求框架切分时，才走 `icons[] role:"frame_part"`。默认不使用原生 `shapes` 承载视觉内容。
- 顺序即图层：默认是背景 → frame → icons → texts；可选切分时是背景 → frame_parts(`icons[] role:"frame_part"`) → icons → texts。
- 写一个 `$RUN_ROOT/editable/01/icons/placements.json`：每个源图图标都要有记录，字段至少包括 `source_label`、`status`（`covered_by_frame` / `placed_icon` / `needs_regen`）、`file`（若已摆放）、`source_bbox`（源图像素）、`x/y/w/h`（比例坐标，若已摆放）。B9 用它检查缺失和重复。

### 框架锚点回校：贴框文本必须跟随最终 frame

`source_bbox` 和 fraction 坐标只说明文本在源图坐标系里数学一致；它不保证文本和最终 `frame.png` 视觉对齐。B3 的 `frame.png` 是 imagegen 提取式生成层，标题条、按钮、底栏、卡片容器可能相对源图有几个到几十个像素的漂移。凡是文本贴着这些框架元素摆放，都必须在首次合成后做 **frame-anchor calibration**：

- 适用对象：分区标题条、卡片/面板标题、按钮文字、底部总结条、页脚/横幅、步骤标签、贴在线条/箭头旁的短标签。
- 不适用对象：独立正文段落、图标旁说明、卡片内部自由排版内容。这些仍以源图文本 bbox 和文本自身基线为主。
- 方法：先按源图像素 bbox 写 `texts[]`，跑 `layout_guard --strict` 和 `placement_qa.py`；然后看最终预览中 `frame.png` 的实际标题条/按钮/底栏位置，量出该框架锚点的视觉中心线或内边距，与源图对应锚点的差值 `dx_px/dy_px`；把贴框文本整体平移同样的 `dx/dy`，保持 `w/h/size_ratio` 不变。
- 计算示例：按钮文本原 bbox 为 `[x,y,w,h]`，最终 frame 中按钮内容区中心比源图低 `dy=32px`，则写回 `source_bbox:[x,y+32,w,h]`，并同步 `y=(y+32)/ref_height`。不要只改 `y` fraction 而忘记更新 `source_bbox`。
- QA 记录：把每个调整写入 `$RUN_ROOT/editable/01/placement_fix_notes.json` 或 layout 旁边笔记，至少包含 `text`、`frame_anchor`、`old_source_bbox`、`new_source_bbox`、`dx_px/dy_px`、`reason`。
- 失败模式：`layout_guard` 通过但标题、按钮、底栏文字看起来偏上/偏下，通常不是坐标契约错，而是缺少这一步。不要反复用全局缩放修；按具体 frame 锚点逐项修。

---

## B7. GPT 视觉提取文字 → 写进 layout.json

**必须用 GPT 自身视觉能力**读原图，提取每段**普通字体文字**：内容(verbatim)、源图像素位置(x,y,w,h)、文字高度像素、颜色(hex)、粗细(bold)、对齐(align)、竖直对齐(valign)、字体(font)。写入 `texts[]` 时默认换成比例坐标和比例字号。艺术字不写入 `texts[]`，只在 B4/B6 作为图标/装饰元素摆放。

- 字号换算：推荐写 `size_ratio = 源图实际文字高度像素 / ref_height`，compose 时自动换算 `size_pt = size_ratio × (页高in×72)`。也可写 `size_pct = size_ratio*100`。旧字段 `size_px`/`size(pt)` 仍兼容，但 `size_px` 必须是**源图实际像素高度**；如果是在 2048×1143 预览上量到 20px，而源图是 4096×2286，写入前必须乘以 2 成 40px，否则 PPT 会得到约一半字号。
- 反推公式：`size_px = 目标pt × ref_height / (slide_height_in×72)`。例如页高 7.441in、`ref_height=2286` 时，`pt_per_source_px=7.441×72/2286=0.23436`，20px 只会生成 4.69pt；正常 9pt 应写约 38.4 源图 px。若用户明确要求常规 PowerPoint 号数，直接写 `size: 9` 这类绝对 pt 更稳。
- **字号要逐档还原**，别一刀切：主标题最大、重点数字更大、模块标题居中、子标签/正文最小；常见坑是从缩略图量字号导致所有正文小一倍。把每段单独估，宁可多设几档。
- **先定样式再定位**：`bold`、字号和 `line_spacing` 会改变字宽、换行和文本视觉高度。`bold` 默认 `false`；普通正文默认不要全加粗，只有各级标题、按钮标题、重点词按原图加粗；多行正文段落优先用约 `line_spacing:1.2`，单行标签/标题可更紧。样式定下来以后再做 bbox 和 frame-anchor 回校，避免后续改粗细/行距导致位置再次漂移。
- `w/h` 要给足，避免文字被框压窄而自动换行错位；长标题给宽框，重点数字给大框。
- `compose_pptx.py` 默认把 PowerPoint 文本框内边距清零；若某一段确实需要留白，可显式写 `margin_left/margin_right/margin_top/margin_bottom`（单位 pt）。不要依赖 PPT 默认内边距来“碰运气”修位置。
- **文字也要做预览回校**：首次预览后逐段检查文本块的左/中/右边界、首行基线、行距和换行位置。可编辑字体与原图手写字体宽度不同是常态，优先调整 `x/y/w/h` 比例、`size_ratio/size_pct`、`line_spacing`、`align`，确保文本块与周围图标/卡片的相对位置贴近源图。
- 若文本与图标在预览中互相压住，但源图没有压住，不能只删图标或把图标缩小；先按 B6 修正图标视觉 bbox，再按文本实际宽度微调文字框。
- 颜色/粗细照原图取；中文默认 `font:"Microsoft YaHei"`。
- 数字、单位、专有名词逐字照抄，**不要改写或编造**。
- 禁止先用 tesseract、EasyOCR、系统 OCR 等传统 OCR 引擎抽文字再贴入。若需要校验，只能把 GPT 视觉结果与原图复看比对，错误处由 GPT 视觉重新判读。

推荐让 GPT 视觉直接返回严格 JSON：

```json
{
  "texts": [
    {
      "text": "逐字原文",
      "x": 170,
      "y": 64,
      "w": 896,
      "h": 96,
      "size_ratio": 0.04,
      "color": "#111111",
      "bold": true,
      "align": "left",
      "valign": "top",
      "font": "Microsoft YaHei"
    }
  ],
  "notes": {
    "ref_width": 2134,
    "ref_height": 1200,
    "uncertain": "只记录不确定字符或需要复看的区域"
  }
}
```

提示词模板：

```text
请直接使用你的视觉能力读取这张 PPT 页面中的所有可见文字，并输出严格 JSON。
要求：
1. text 必须逐字照抄，不改写，不补写，不合并不同位置的文本。
2. 每个文本框先给源图实际像素 bbox，同时报告 ref_width/ref_height；再给换算后的 fraction bbox：x/ref_width、y/ref_height、w/ref_width、h/ref_height。若你看到的是缩略显示，先把 bbox 和文字高度按缩放倍数换回源图实际像素。
3. 估算源图实际文字高度像素，并给 size_ratio=文字高度像素/ref_height；如果你只能在缩略显示中量到高度，先乘以源图/缩略图缩放倍数再计算。正文 bold 默认 false，只给标题、按钮、重点词设置 true；同时给 color(hex)、align、valign、font。
4. 保持阅读顺序：标题、章节/标签、主体内容、脚注。
5. 遇到艺术字（渐变、书法、形变、描边、阴影、纹理、徽章式排版等普通字体无法直接写出的文字）不要放入 texts[]，改写入 notes.art_text_candidates，交给 B4 图标/装饰层。
6. 不要使用或引用外部 OCR 结果；不确定的字符写入 notes，不要猜造。
```

---

## B8. 合成 + 预览

```bash
python3 scripts/layout_guard.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --strict
python3 scripts/placement_qa.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --slide-index 1 --out-dir "$RUN_ROOT/editable/01/qa-source-boxes"
python3 scripts/compose_pptx.py "$RUN_ROOT/editable/01/layout.json" "$RUN_ROOT/out/<task-slug>.pptx" --preview-dir "$RUN_ROOT/out/preview"
python3 scripts/placement_qa.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/editable/01/layout.json" --slide-index 1 --preview "$RUN_ROOT/out/preview/slide_01.png" --out-dir "$RUN_ROOT/editable/01/qa-placement"
python3 scripts/visual_compare_qa.py "$RUN_ROOT/editable/01/slide-01.png" "$RUN_ROOT/out/preview/slide_01.png" --out-dir "$RUN_ROOT/editable/01/qa-visual"
```

- 生成可编辑 .pptx（文字是真文本框；背景/框架/图标/装饰是 imagegen 生成的可移动图片层）。
- `layout_guard.py` 先阻止坐标系混用：`ref_width/ref_height`、`source_bbox`、`x/y/w/h` 必须彼此一致，且与当前源图实际像素尺寸一致。它不做内容覆盖高度判断；最终位置是否正确必须看合成预览与源图的视觉对比。
- `layout_guard.py --strict` 同时检查文字样式：低于默认 6pt 的文本会被拦截（真实脚注/极小字需写 `small_text_ok:true`），`size_px` 与 `source_bbox` 行高相差过大时会提示半分辨率测量风险；6 个以上文本框中超过 85% 都是 bold 会被拦截（真实全粗体页需写 `allow_all_bold_text:true` 并在 QA 备注说明）。
- 第一遍 `placement_qa.py` 不传 `--preview`，只生成源图框。必须打开 `qa-source-boxes/slide_01_source_boxes.png` 复核每个框是否真实圈住源图对应对象；这一步专门抓“source_bbox 量错位置但数学一致”的错误。
- `--preview-dir` 用 Pillow 把各层拍平成 PNG，用于 B9 对比。
- `placement_qa.py` 会把 `icons[]` 和 `texts[]` 的 bbox 画回源图和预览图；先看标注框是否压准，再看整体视觉。
- `visual_compare_qa.py` 会把源图和最终预览统一尺寸后输出并排图、叠图、差异热图和诊断指标；最终验收必须看这些视觉对比产物，判断文字/图标是否和原始 PPT 图片对应。

多页：把每页 layout 合进一个 `deck.json` 的 `slides[]`，一次合成整本。

---

## B9. QA 反馈环

先看 `$RUN_ROOT/editable/01/qa-placement/slide_01_source_boxes.png` 和 `slide_01_preview_boxes.png`，再打开 `$RUN_ROOT/editable/01/qa-visual/side_by_side.png`、`blend.png`、`diff_heatmap.png` 对比源图与最终合成预览：

0. `imagegen-assets-manifest.json` 是否证明 B2/B3/B4 都来自真实 imagegen 调用，而不是程序绘图、旧图复用或裁原图？
1. 背景是否干净、配色是否一致？
2. 默认检查 `frame.png` 叠到背景后是否完整对位、线条/圆弧/填充是否干净；若用户要求框架切分，再检查 `frame_parts/icons_contact_sheet.png` 是否把框架按透明区域切成相互独立的部件。`icons_contact_sheet.png` 是否所有图标完整无缺边？有无齿轮、火箭、箭头、动物等被裁半截？
3. `placements.json` 是否覆盖源图全部图标/装饰/艺术字？每项状态是否为 `covered_by_frame` 或 `placed_icon`，没有 `needs_regen`？
4. 对比最终预览与源图：是否缺图标？是否有同一图标在 frame 和 icons 里重复叠影？图标位置、大小是否贴合，是否压住文字？重点看视觉 bbox，而不是只看 layout 标注框。
5. 框架结构是否对位？卡片位置、大小是否贴合？
6. 文字内容/字号/颜色/对齐是否还原？文本块的边界、换行、首行位置、行距和邻近图标距离是否贴近源图？
7. `layout_guard.py --strict` 是否通过？若失败，先修正坐标契约；不要在坐标系不一致的 layout 上继续肉眼微调。
8. `qa-source-boxes/slide_01_source_boxes.png` 是否逐项圈住源图真实对象？若框的位置本身就错了，先重测 `source_bbox`；不要继续调 fraction 或只看最终预览。
9. 有偏差 → 先改图标的源图像素 bbox 记录，再换算比例写回 `layout.json`；再改文字框比例、`size_ratio/size_pct`、行距和颜色；最后对分区标题、按钮文字、底栏总结等贴框文本做 frame-anchor 回校，按最终 `frame.png` 的标题条/按钮/底栏视觉中心线微调 `dx/dy_px` → 重跑 B8 和 placement QA → 再对比。
10. 满意后再处理下一页 / 输出整本。

**图标/文字 QA 验收阈值**：

- 普通图标的视觉中心点应尽量落在源图对应中心点附近；若肉眼可见漂移，必须改坐标。大图标/艺术字/说明气泡以容器边界和相邻文字为准。
- 图标视觉尺寸不得明显小于源图。若 `placement_qa.py` 的框对齐但预览图标仍偏小，说明切片透明边距或缩放比例有问题，必须放大 layout bbox、重切或重出图标表。
- 源图中没有遮挡文字的图标，最终预览也不得遮挡文字；源图中贴近文字的图标应保持相同间距，不得为了避免遮挡移到无关位置。
- 普通文本框不能因为框太窄产生额外换行；不能因为框太宽导致行长明显超过源图。每个主要文本块至少做一次源图/预览并排复看。
- 每页至少完成一轮“合成预览 → placement QA → 修改 layout → 再合成预览”。只有首次预览已经与源图高度贴合时，第二轮可只记录“无需调整”的 QA 说明。

最终答复必须包含：

- 最终 `.pptx` 的可点击绝对路径。
- 若复制了便捷副本，同时给出 RUN_ROOT 内原始输出路径和副本路径。
- 若仍有非阻断的还原差异，明确说明，不得只说“完成”。

---

## layout.json / deck.json 完整 schema

单页用 layout.json（可不含 `slides`，直接写 `background/frame/shapes/icons/texts`）；整本用 deck.json（含 `slides[]`）。

```json
{
  "slide_width_in": 13.333,
  "slide_height_in": 7.5,
  "units": "fraction",
  "ref_width": 2134,
  "ref_height": 1200,
  "assets_dir": "/abs/path/to/RUN_ROOT/editable/01",             
  "slides": [
    {
      "background": "background.png",
      "frame": "frame.png",
      "shapes": [],
      "icons": [
        {"file": "icons/ic1_r1c1.png",
         "x": 0.0703, "y": 0.4000, "w": 0.0703, "h": 0.1250,
         "source_bbox": [150, 480, 150, 150]}
      ],
      "texts": [
        {"text": "重点数字 88%", "x": 0.4499, "y": 0.1200, "w": 0.4592, "h": 0.1600,
         "source_bbox": [960, 144, 980, 192],
         "size_ratio": 0.0741, "color": "#1A1A1A", "bold": true,
         "align": "left", "valign": "middle", "font": "Microsoft YaHei",
         "line_spacing": 1.0}
      ]
    }
  ]
}
```

字段说明：
- `frame`：默认框架视觉层，指向整张透明 `frame.png`，全幅铺到背景之上、图标之下。只有用户明确要求框架切分/框架部件可移动时，才省略 `frame`，改用 `icons[]` 中 `role:"frame_part"` 的 `frame_parts/` 单件切片。
- `icons[]` 的 `x/y/w/h` 必须来自**对原图的像素实测后换算的比例**（见 B6），不是凭感觉给；`source_bbox` 保留源图像素测量值，`w/h` 保持图标原宽高比、尺寸贴合原图，放进去不偏大/偏小/压字。
- `units`：推荐 `"fraction"`。`ref_width/ref_height` 仍必须记录源图尺寸，用于 `source_bbox`、旧 `size_px` 换算和 QA。`"px"` 仅作旧 layout 兼容。
- `shapes[]`：默认必须为空。除非用户明确要求原生形状重建，否则不得使用 `shapes` 承载任何视觉内容。背景进入 `background.png`；容器、卡片、标题条、分隔线、时间轴、图表骨架、装饰色块都应进入整体 `frame.png`；图标/插画/车辆剪影进入普通 `icons[]`。只有用户明确要求框架切分时，才把 `frame.png` 按透明区域切成 `frame_parts/` 并作为 `icons[] role:"frame_part"` 放回。
- `texts[].size_ratio` 为源图实际文字高度占源图高度的比例，推荐字段；也可用 `size_pct`。旧字段 `size_px`+`ref_height` 或绝对 `size`(pt) 仍兼容，但 `size_px` 不能来自缩略图。`valign`：`top/middle/bottom`。真实极小脚注可写 `small_text_ok:true`，真实全粗体页可在 slide/deck 写 `allow_all_bold_text:true`。
- 文件路径相对 `assets_dir`（默认 = 该 json 所在目录），也可用绝对路径。为避免串文件，单页 layout 建议省略 `assets_dir`；如果保留，必须写 `RUN_ROOT` 内的绝对页目录，不要写 `"editable/01"`、`"."` 这类依赖当前工作目录的相对路径。
- 全幅图片型页（功能 A 成品）：slide 里只放 `background`，不放其它层。

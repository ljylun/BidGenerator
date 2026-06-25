# 运行时与模型差异适配

本 Skill 的**主目标运行时是 Codex 里的 GPT**，但也要能在 Cursor/Claude 等运行时跑。图片生成、抠图、看图(OCR/定位) 的具体调用方式因运行时而异。动手前先按本页解析后端。

---

## 1. 图片生成后端解析顺序

1. **用户当条消息点名了后端** → 用它。
2. **Codex（GPT）运行时** → 用内置 `imagegen` skill （**首选**，无需 API key）。
3. **其它原生图像工具**（如 Cursor 的 `GenerateImage`、Hermes `image_generate`）→ 用之。
4. 都没有 → 告诉用户并询问如何继续。

**绝不**用 SVG / HTML / Canvas / 代码绘图、PPT shapes、填充色块或裁原图局部冒充 raster 出图。**绝不**在已生成的位图上用代码补字/盖字。

---

## 2. 在 Codex（GPT）里 —— 主路径

### 出图（功能 A、功能 B 的背景/框架/图标）
- 调用内置 `imagegen` skill（`Skill` 工具，`skill: "imagegen"`）→ 默认走其内置 `imagegen` 工具。
- 一次调用出一张图；要多张就发多次调用（功能 A 批量、功能 B 多张图标图同理）。
- **比例**：内置 `imagegen` 的比例靠提示词表达——写明"16:9 横版，高分辨率（约 2048×1152）"。方形图标图写"正方形 1:1，高分辨率"。
- **保存位置**：内置工具默认存到 `$CODEX_HOME/generated_images/...`。**用完必须把选定图复制到本次唯一 `RUN_ROOT` 下**（如 `$RUN_ROOT/editable/01/background.png`、`frame_raw.png`、`icons_raw_1.png`），并保留默认目录原图，不要把成品只留在默认目录，也不要复制到工作区固定 `editable/01`。
- **功能 B 生成证据**：每页必须写 `imagegen-assets-manifest.json`，记录 `background`、`frame_raw`、`icons_raw_*` 的 `generated_source`、`copied_to`、`prompt_file`、`backend`、`key_color`。没有这份 manifest，不能交付可编辑 PPTX。
- **路径隔离**：`layout.json` 优先省略 `assets_dir`，或把它设为 `RUN_ROOT` 内的绝对页目录；manifest 的 `copied_to` 也必须指向同一个 `RUN_ROOT`。不要在同一工作目录里复用相对路径 `editable/01`、`out/`、`qa/`。
- **编辑本地图**（功能 B 擦除式背景）：先用内置 `view_image` 把原图载入上下文，再走内置 edit 流程；编辑时反复声明不变量（"只移除文字/图标/卡片，保留底色与渐变"）。

### 抠透明（功能 B：框架/图标去底）
- **首选本技能自带脚本 `scripts/chroma_key.py`（保色保线/保形，跨运行时一致）**：
  ```bash
  python3 scripts/chroma_key.py --input <框架绿底图> --out <透明框架.png> --preset frame-safe --scale 2 --force
  python3 scripts/chroma_key.py --input <图标绿底图> --out <透明图标.png> --preset icon-safe --scale 2 --force
  # 非绿底：--auto-key none --key-color "#ff00ff"
  ```
- 它**只对绿色主导像素去溢出**，对红/藏青/灰/白是 no-op → **绝不褪色**；默认不腐蚀边缘 → **不丢细线/辉光**。预设会提升半透明边缘 alpha，并用二值 gap repair 修补细线断点，不直接对灰度 alpha 做腐蚀/闭合，所以横线竖线更齐、圆弧不容易残缺。`--scale 2` 会先超采样再抠图，PPT 缩回目标尺寸后边缘更顺。
- 兜底：无该脚本时才用 Codex 的 `remove_chroma_key.py`，且**不要**叠 `--soft-matte --despill`（会把红色图标抠成灰白、吃掉框架线），用纯 `--auto-key border` 即可。
- 抠完务必把透明图合到灰底自检：颜色对不对、线/辉光在不在、有无残边（见 image-to-pptx.md B5「抠图保真铁律」）。

### 看图（文字提取/图标定位）
- 直接用 GPT 自身视觉读图，输出结构化 JSON（`texts[]` / `icons[]` 坐标）。不要使用外部 OCR 引擎；文字内容、bbox、字号、颜色、粗细、对齐都由 GPT 视觉一次性判读，再通过复看原图校正。
- 坐标优先输出**源图实际像素 bbox**，不要先输出 fraction。`view_image`/浏览器/预览图可能是缩略图；若在缩略图上量测，必须按 `源图宽/显示宽` 与 `源图高/显示高` 分别换回源图坐标，并同步缩放 `size_px`。layout 可使用 `units:"px"`（合成脚本自动换算到 PPT）或按源图 bbox 换算后的 `units:"fraction"`，但 `ref_width/ref_height` 必须等于源图真实尺寸。
- 字号优先写 `size_ratio = 源图实际文字高度像素 / ref_height`，或在需要标准 PowerPoint 号数时直接写 `size` 绝对 pt。不要把缩略图量到的文字高度写成全分辨率 `size_px`；`pt = size_px × (slide_height_in×72) / ref_height`，所以半分辨率 `size_px` 会直接生成半号字。
- 合成前必须跑 `scripts/layout_guard.py 源图 layout.json --strict`；它会拦截 ref/source_bbox/fraction 坐标契约不一致、疑似半分辨率字号、低于默认 6pt 的文本，以及 6 个以上文本框中超过 85% 都加粗的 all-bold 风险。它不用页面覆盖高度判错。
- 合成后必须跑 `scripts/placement_qa.py`，生成源图标注框和预览标注框；位置不准先修 bbox，再重合成。
- 合成后必须跑 `scripts/visual_compare_qa.py 源图 最终预览 --out-dir qa-visual`，并打开并排图、叠图和差异热图，用 GPT 视觉判断最终 PPTX 预览里的文字/图标是否与原始 PPT 图片对位。

### CLI 兜底（一般用不到）
- 仅当用户明确要 CLI/API，或要真·原生透明时，才用 imagegen 的 `scripts/image_gen.py`（需 `OPENAI_API_KEY`，`gpt-image-2`，`--size 2048x1152`）。切到该路径前先问用户。

---

## 3. 在 Cursor / Claude（本 Skill 的开发&测试环境）里

- 出图：用 `GenerateImage` 工具（提示词里写比例/分辨率）。生成的图在工作区，直接引用其路径。注意它**原生出 3:2（1536×1024）**——若目标就是 3:2 则正好直接用；要 16:9 再按 §5 裁切。
- 抠透明：用本技能自带 `scripts/chroma_key.py`（首选，保色保线）。
- 看图：用 Claude 自身视觉读图输出 JSON。
- 其余脚本（`probe_palette.py` / `slice_grid.py` / `compose_pptx.py`）与 Codex 完全一致。

---

## 4. GPT 与 Claude/Opus 的差异要点（写给最终在 Codex 跑的 GPT）

- **工具名不同**：Codex 用 imagegen skill；不要套用其它运行时的工具名。
- **图片落盘**：Codex 内置出图在 `$CODEX_HOME/generated_images/`，**务必复制到本次唯一 `RUN_ROOT` 并保留原图**——这是 Codex 特有的坑，别忘。不要复制到固定 `editable/01`，避免同目录多个转换任务互相干扰。
- **功能 B 图片层**：背景、框架、图标/装饰都必须由 imagegen 生成；不得用 PPT 色块、原生 shapes、代码绘图或裁切原始幻灯片局部替代。
- **逐字照排**：严格使用用户文字/数据，零编造（全局铁律）。生僻字在出图提示词里逐字拆开强调以提升渲染正确率。
- **GPT 视觉文本提取**：文字层必须来自 GPT 视觉对原图的结构化判读，不要跑 tesseract/EasyOCR/系统 OCR。对不确定字符用复看原图校验，不要猜造。
- **结构化输出**：`layout.json` / `deck.json` 要求严格合法 JSON（双引号、无尾逗号、hex 带 `#`）。
- **批量**：多资产用"多次单图调用"，不要用一次 `n` 张来替代不同内容的图。
- **确认策略**：功能 A 默认先确认风格/受众/页数/语言；用户说"直接生成/不用确认"才跳过，并在开跑前声明所用设定。
- **不要代码补字**：任何运行时都禁止在位图上用 ImageMagick/Pillow/SVG 盖字改字；错字就改提示词重出。

---

## 5. 比例与尺寸速查

**比例由用户决定**：默认 16:9；用户说 3:2（或后端原生 3:2 且用户接受）就直接用 3:2，**不必裁切**。功能 A 出图、功能 B 背景/框架/图标、`compose_pptx.py` 画布要**全程同一比例**。

| 用途 | 比例 | 建议尺寸 / 画布 |
|---|---|---|
| 幻灯片（功能 A / 功能 B 背景/框架） | 跟随用户：16:9 或 3:2 | 16:9→2048×1152；3:2→1536×1024 |
| `compose_pptx.py` 画布 | 16:9→13.333×7.5in；**3:2→13.333×8.889in**；4:3→10×7.5in | 配 `ref_width/ref_height` 用原图像素 |
| 图标提取网格图（功能 B） | 1:1 正方形 | 越大越好（如 2048×2048） |

- Cursor `GenerateImage` 原生出 **3:2（1536×1024）**：目标 3:2 时直接用最省事。
- Codex 内置 `imagegen`：用提示词表达比例；CLI 用 `--size`。

### 只要 16:9 但后端只出 3:2 时

1. 提示词按"16:9 构图、上下留安全边"生成（关键内容别贴最上/最下边）。
2. 居中裁切：3:2 的 1536×1024 → 1536×864：
   ```bash
   python3 -c "from PIL import Image;im=Image.open('in.png');w,h=im.size;th=int(w*9/16);t=(h-th)//2;im.crop((0,t,w,t+th)).save('out.png')"
   ```
3. 背景/框架/图标参考也同样裁，保持与幻灯片对齐后再 compose。

## 6. 排版参考图库 `参考图/`

技能自带 `参考图/`（高密度复杂排版范例，子集如 `red_grey_project / work_result / tech_prize / scholar_green / leader_love`，各含 ref1..N.png）。

- **用途**：功能 A 出图前，挑与本页结构最像的参考图，把其**布局骨架**写进提示词（见 image-prompt-guide.md §1.6）。
- **可作 reference 传入**：Codex `imagegen` 支持参考图；传入时务必在提示词写明"**只参考排版/构图，不要使用其配色与文字**"。
- 严禁照搬参考图的颜色、文字、品牌元素——配色一律用本页指定的【整体风格】色。

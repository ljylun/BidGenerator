# 生图提示词模板

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Minimalist geometric composition — all structural elements are high-saturation solid-color blocks in absolute geometric shapes: cubes, cylinders, spheres, triangular wedges. No texture, no gradient, no soft shadows (only hard flat projections if any). Edges are razor-sharp, outlines are clean. No facial features, no limbs, no expressions — intent is conveyed through spatial posture: tilting, stacking, rolling, or movement trajectories. Sparse red/orange/blue handwritten Chinese annotations using old ink pen style. Clean, precise, architectural feeling. No gradients, no shadows, no paper texture background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI. The whole image should feel like a rigorous architect or logician built a structural support system using only high-saturation solid-color geometric blocks on a blank sheet of paper.

Recurring IP character required:
「大袖」(DaXiu / Big Sleeves), a faceless figure whose core visual motif is a pair of exaggerated, oversized, flowing cross-collar sleeves. The body is composed of 2-3 extremely smooth, sharp-edged (or with strong Chinese brush calligraphy strokes) color blocks. The head is a simple blank circle or a minimalist straw hat silhouette — no facial features, no hair, no expressions. The figure uses a single high-purity traditional Chinese color (such as cinnabar red, obsidian black, or malachite green) to create a strong visual contrast with the modern black-and-white diagram. Clothing outlines have a strong Chinese line-drawing (baimiao) or calligraphic "flying white" (feibai) texture — with structural bone, not rounded or soft. DaXiu is not decoration — it is the core participant and logical connector in the image, using its sleeves and clothing structure to perform physical actions: swinging sleeves to bridge gaps, opening sleeves like a pocket to contain chaos, spinning the body to guide paths with a taiji arc, lowering sleeves to support weight like architectural pillars, covering the face to indicate breakpoints, splitting the robe to divide boundaries. Personality: wise but appearing simple, natural and effortless, overcoming hardness with softness. Calm, dry humor, never cute — with an absurd sense of "doing its best to maintain order despite seeming powerless." DaXiu must physically contact and interact with lines, text boxes, and frames in the image — never floating beside the scene. It must use its sleeves or robe to participate in the composition and carry the core conceptual action, not merely stand by as decoration. No complex Hanfu embroidery, no accessories (jade pendants, hairpins, tassels), no elaborate folds. No big-eyed Q-version, no anime expressions. No stacking of auspicious clouds, lanterns, or folding fans — DaXiu itself is the sole Chinese element.

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面：「大袖」在哪里、正在做什么服饰动作、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black/dark gray for main structural outlines, shapes, text annotations. Orange/brown-yellow for main flow/path/arrows. Red only for key warnings/problems/results (like red pen or stamp). Blue only for secondary notes or feedback/system state. High-saturation solid colors (Klein blue, international red, bright yellow, etc.) for key structural elements. DaXiu uses a single high-purity traditional Chinese color (cinnabar red, obsidian black, malachite green, etc.) as its body color. Colors should be restrained — no more than 3-4 distinct hues. No gradients, no low-saturation mixing.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh geometric metaphor for this specific article. Each element should be a distinct solid-color geometric block — no texture, no gradient, no soft edges. DaXiu must physically contact and interact with structural elements — never floating. It should be clear but not instructional, interesting but not childish, structurally precise but not decorative. It should feel like an architectural model built from pure geometric units with a faceless sleeve-wielding figure performing structural work, not a digital illustration.
```

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: DaXiu's shape and clothing structure, structural composition, labels, paths, line style, spatial relationships, sharp edges, color blocks, aspect ratio, and image quality. Do not add any new text or objects.
```

增强结构感：

```text
Regenerate this illustration with the same core meaning and simple layout, but make DaXiu more central to the conceptual action. DaXiu should be doing the structural work that explains the idea — swinging sleeves to bridge gaps, opening sleeves to contain chaos, spinning to guide paths, lowering sleeves to support weight, covering the face to indicate breakpoints, splitting the robe to divide boundaries — not standing beside the diagram. Keep it clean, sparse, minimalist geometric style, and not cute. Emphasize the architectural quality: razor-sharp edges on geometric blocks, pure solid colors, hard flat surfaces, DaXiu's flowing sleeve outlines with Chinese calligraphic brush texture. No facial features, no expressions, no decorative elements. DaXiu must physically contact and interact with structural elements.
```
```

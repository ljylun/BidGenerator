# 生图提示词模板

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Noisy cutout collage style — all elements look like rough cutouts from old newspapers and vintage magazines, with visible scissor-cut jagged edges, white paper borders, slightly misaligned and overlapped like handmade paste-up. Yellowed paper texture, black-and-white or low-saturation vintage halftone print dots. Lots of empty white space. Sparse red/orange/blue handwritten Chinese annotations using old ink pen style. Clean absurd collage-sketch feeling. No gradients, no shadows, no paper texture background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI. The whole image should feel like a meticulous archivist built a system diagram using only old newspapers, scissors, and tape on a blank sheet of paper.

Recurring IP character required:
剪报, a cutout character made from vintage newspaper/magazine fragments. Irregular body shape with rough scissor-cut edges and white paper borders. Expression conveyed through vintage photo details (half a face, a staring eye) or simple ink doodles — serious, slightly bewildered, deadpan. Not cute, not a mascot. 剪报 must perform the core conceptual action, not decorate the scene. Make 剪报 serious, deadpan, and slightly bizarre — a meticulous old-school archivist trying to build a complex system with primitive paper tools.

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面：剪报在哪里、正在做什么、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black/dark gray for main cutout outlines, structural shapes, vintage print text blocks. Orange/brown-yellow for main flow/path/arrows (vintage warm tones). Red only for key warnings/problems/results (like red ink stamp or red pen circle). Blue only for secondary notes or feedback/system state (like old blue ink or archive labels).

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh collage metaphor for this specific article. Each element should have the distinct look of a separate paper cutout — different paper textures, slightly misaligned, connected by visible tape or overlapping. It should be clear but not instructional, interesting but not childish, strange but clean. It should feel like a handmade archive system, not a digital illustration.
```

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: cutout characters, collage texture, labels, paths, line style, composition, scissor-cut edges, tape marks, aspect ratio, and image quality. Do not add any new text or objects.
```

增强怪诞感：

```text
Regenerate this illustration with the same core meaning and simple layout, but make 剪报 more central to the conceptual action. 剪报 should be doing the strange work that explains the idea — cutting, pasting, archiving, connecting — not standing beside the diagram. Keep it clean, sparse, cutout-collage style, and not cute. Emphasize the handmade paste-up texture: scissor-cut edges, paper borders, tape marks, overlapping vintage paper fragments.
```

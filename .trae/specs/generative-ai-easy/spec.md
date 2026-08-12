# Generative AI 轻松学 Spec

## Why
用户希望将《Generative AI in Action》这本专业书籍转化为"轻松学"风格的教学材料，降低学习门槛，让怕术语、怕代码的读者也能循序渐进地掌握生成式AI知识。

## What Changes
- 创建 `ebooks/GenerativeAI轻松学/` 目录
- 编写 `00-目录与体例.md` 定义全书结构与风格规范
- 编写 `01.md` 至 `13.md` 共13章正文
- 编写 `99-结语与附录.md` 包含练法、术语词典、速查表
- 每章严格遵循五段式结构：开篇除恐 → 白话化 → 直觉先行 → 例子贴身 → 收尾

## Impact
- 输出路径：`ebooks/GenerativeAI轻松学/`
- 参考素材：`ebooks/Manning.Generative.AI.in.Action.1633436942.pdf`
- 风格依据：x-made-easy-skill 规范

## ADDED Requirements
### Requirement: 轻松学教材生成系统
系统 SHALL 提供将技术书籍转化为轻松学风格教学材料的能力。

#### Scenario: 骨架确认
- **WHEN** 用户提供PDF素材并指定轻松学风格
- **THEN** 系统先输出 `00-目录与体例.md` 骨架，包含书名、四部式结构、每章除恐主旨、难度标注约定、贯穿例子
- **AND** 用户确认骨架风格与深浅度对路

#### Scenario: 逐章生成
- **WHEN** 用户确认骨架后
- **THEN** 系统按五段式为每章生成正文
- **AND** 每章包含至少2个贴身例子，标注难度（☼/☼☼/☼☼☼）
- **AND** 事实、案例忠实于原书，自编例子明确标注

#### Scenario: 结语附录
- **WHEN** 13章正文全部完成
- **THEN** 生成 `99-结语与附录.md`，包含练法/用法、术语小词典、一页纸速查、各章工具速查、出处与难度说明

## MODIFIED Requirements
### Requirement: 风格一致性
所有章节 SHALL 遵循统一的除恐-白话-直觉-例子-收尾五段式结构。
**Validation**: 每章开头有明确的除恐主旨，结尾有"**就这样。**"收尾句。

## REMOVED Requirements
（无）

---
name: 智能体需求文档生成skill
description: 用于生成和维护通用需求文档、功能设计文档、PRD/设计说明（Markdown 格式）。当用户提到"新建需求文档""新建PRD""按模板生成功能设计文档""更新设计说明""生成文档快照""批量生成文档""初始化文档模板""维护修订记录"时，应使用本 skill。基于源 Markdown 输出版本化 .md 快照，支持模板初始化、单文档/profile/manifest 三种生成方式，以及旧快照自动归档。
---

# 智能体需求文档生成 Skill

## 一句话定位

把"无版本号 Markdown 源文档"稳定产出为"版本化 `.md` 快照"，适用于需求文档、功能设计文档、PRD、设计说明等标准化文档场景。

## 适用触发语句

当用户出现以下意图时，优先使用本 skill：

- 新建需求文档 / 新建 PRD / 新建设计说明
- 按模板生成某功能设计文档
- 修改现有源文档并输出新版本快照
- 批量生成多个模块文档
- 为某项目建立通用 profile / manifest / 模板
- 将 Markdown 文档沉淀为可交付的 `.md` 版本快照

## 适用场景

- 新建某个功能、模块、页面的需求文档或功能设计文档
- 更新现有无版本号源文档，并生成新版本快照
- 将 Markdown 源文档转换为 `.md` 版本快照
- 批量生成多个文档快照
- 为不同项目复用统一的需求文档工作流

## 使用边界

- 本 skill 提供通用工作流、模板和脚本，不绑定任何特定项目、目录或文档清单
- 项目专属章节、角色、命名、组织边界、私有业务规则等，应写进项目自己的源文档、profile、模板或参考资料
- **通用合规基线**：`references/通用等保三级安全要求.md` 是 skill 内统一维护的跨项目通用安全基准，功能文档在涉及等保功能点时按需引用；若具体项目需要调整合规口径，直接修改该参考文件即可，不要把项目私有规则写死在通用 skill 主体中
- 若团队存在"生成前必须二次确认"等协作规则，应记录在项目记忆或项目文档中，而不是写死为 skill 强制规则
- 若需求是自由体报告、会议纪要、营销文案等非结构化文档，不必强行套用本 skill

## 推荐执行策略

| 当前任务 | 推荐入口 | 原因 |
| --- | --- | --- |
| 新建首版文档 | `gen_template.js` | 一次性生成源 Markdown + 首版快照 |
| 修改既有文档并重新出版 | `gen_from_md.js --source` | 最直接，适合单文档更新 |
| 同类项目重复建文档 | `gen_template.js --profile` | 常用字段可复用，减少重复输入 |
| 单文档标准化生成 | `gen_from_md.js --profile` | 适合固定目录、固定命名的项目 |
| 多文档批量出版 | `gen_from_md.js --manifest` | 统一执行多个文档任务 |
| 多文档且共享公共配置 | `gen_from_md.js --manifest --profile` | 用 profile 放公共字段，manifest 放单文档差异 |

## 标准工作流

1. 先确认文档名称、适用系统/项目、模块路径、角色、字段和交互范围
2. 新建文档时，优先参考 `references/通用需求文档模板.md`，再通过 `scripts/gen_template.js` 初始化源 Markdown
3. 若文档涉及身份鉴别、访问控制、日志留痕、敏感字段、导入导出或接口安全等内容，同时参考 `references/通用等保三级安全要求.md`，在源文档 `7.1` 中按章节引用并补充模块特有要求
4. 更新文档时，直接编辑无版本号源文件，并同步维护文档版本与修订记录
5. 生成快照前，确认输出目录、源文件路径和版本号是否正确
6. 使用 `scripts/gen_from_md.js` 生成 `.md` 快照；如目录下已有旧快照，脚本会自动归档到 `backup/`
7. 如需批量生成，使用 manifest 文件集中声明多个源文件；如有共享参数，再叠加 profile
8. 交付前确认源文件、Markdown 快照两者版本一致

## 资源说明

- `references/快速上手.md`：三分钟上手说明，适合首次导入后快速照着跑
- `references/通用需求文档模板.md`：通用十二章需求/功能设计模板
- `references/通用等保三级安全要求.md`：skill 内统一维护的通用安全基准文件；功能设计文档在 `7.1` 中按需引用适用章节，并补充模块特有要求
- `references/PROFILE_SCHEMA.md`：profile / manifest 字段说明、优先级与组合示例
- `assets/examples/feature-design.profile.json`：模板初始化示例 profile
- `assets/examples/single-generate.profile.json`：单文档生成示例 profile
- `assets/examples/batch-shared.profile.json`：批量生成时的共享参数示例 profile
- `assets/examples/feature-design.manifest.json`：批量生成示例 manifest
- `assets/examples/示例功能设计.md`：示例源文档

## 合规引用约定

- 通用等保要求统一维护在 `references/通用等保三级安全要求.md`
- 功能设计文档仅在涉及账号、权限、日志、敏感字段、导入导出、接口安全等功能点时，在 `7.1 合规与安全要求` 中按章节引用
- 功能文档应写"引用章节 + 本模块特有要求"，不要把通用规则原文整段复制到每份文档中
- 若某项目需要调整合规口径，直接修改上述参考文件即可，后续文档按更新后的内容引用

## 数据导出文件命名规范（通用约束）

生成功能设计文档时，如涉及「导出」功能描述，推荐遵循以下命名规范：

- **格式**: `{业务前缀}_{YYYYMMDD}_{HHMMSS}.xlsx`
- **示例**: `用户信息_20260405_103045.xlsx`
- **时间戳**: 使用当前系统时间，年月日(8位) + 时分秒(6位)
- **扩展名**: 固定为 `.xlsx`

**规范说明：**
1. 业务前缀应简洁明了，建议使用「模块名+信息」或「功能名+数据」格式
2. 时间戳确保文件名唯一性，避免覆盖
3. 导入模板文件名建议使用固定名称（不带时间戳），如：`批量导入模板.xlsx`

**示例对照表：**

| 模块 | 导出前缀示例 | 示例文件名 |
|------|-------------|-----------|
| 用户管理 | 用户信息 | 用户信息_20260405_103045.xlsx |
| 订单管理 | 订单数据 | 订单数据_20260405_103045.xlsx |
| 设备管理 | 设备信息 | 设备信息_20260405_103045.xlsx |

> **注意**：具体项目可根据实际业务调整前缀命名，但建议保持 `{前缀}_{时间戳}.xlsx` 的统一格式。

## 删除功能规范（推荐）

生成功能设计文档时，如涉及「删除」功能描述，推荐遵循以下规范：

**核心原则：根据业务需要决定是否提供批量删除功能**

| 模式 | 适用场景 | 实现方式 |
|-----|---------|---------|
| 单条删除 | 数据敏感、操作不可逆、需严格控制的场景 | 列表不展示复选框，仅在行内操作列提供删除按钮 |
| 批量删除 | 数据量大、操作频繁、需提升效率的场景 | 列表展示复选框，工具栏提供批量删除按钮 |

| 项目 | 规范要求 |
|-----|---------|
| 删除入口 | 单条删除在每行数据的操作列提供"删除"按钮；批量删除在工具栏提供"删除"按钮 |
| 删除约束 | 已绑定/已入网/已启用等状态的数据，删除按钮灰化不可用 |
| 确认机制 | 点击删除后弹出确认弹窗，确认后才执行删除 |

**建议：**
- 对于车辆、设备、用户等核心数据，建议仅提供单条删除，避免误操作
- 对于日志、临时数据等非核心数据，可考虑提供批量删除
- 具体项目应在文档中明确是否提供批量删除功能

## 导入功能逻辑规范（前置校验模式）

生成功能设计文档时，如涉及「导入」功能描述，推荐遵循以下逻辑规范：

**核心原则：前置全量校验，有错不导入，全部通过才入库**

| 阶段 | 处理逻辑 | 用户反馈 |
|-----|---------|---------|
| 文件上传 | 校验文件格式（.xlsx）和大小（≤10MB） | 格式错误时Toast提示阻断 |
| 数据校验 | 逐行校验所有数据（必填/格式/长度/唯一性/关联数据/字典值） | 错误列表直接展示在页面（行号+列名+原因） |
| 导入执行 | 仅当全部数据校验通过后才执行导入 | 成功后Toast提示导入条数 |

**校验类型清单：**

1. **文件级校验**：格式、大小
2. **必填项校验**：必填字段不能为空
3. **格式校验**：正则匹配（手机号、邮箱、编码等）
4. **长度校验**：字段值长度限制
5. **唯一性校验**：与现有数据对比，关键字段不重复
6. **关联数据校验**：外键/关联字段值在系统中存在
7. **字典值校验**：枚举/字典字段值在有效范围内

**错误提示格式：**
- 统一格式：`第X行，【字段名】：错误原因`
- 示例：`第3行，用户名：不能为空`、`第5行，手机号：格式不正确`

## 快速开始

1. 首次导入后，进入 `scripts/` 目录执行一次 `npm install`
2. 按场景选择入口：
   - 新建首版：`gen_template.js`
   - 单文档出版：`gen_from_md.js --source` 或 `--profile`
   - 批量出版：`gen_from_md.js --manifest`
3. 生成完成后，检查输出目录中的：
   - 无版本号源文件
   - `{baseName}_{version}.md`
   - `backup/` 中是否已归档旧快照

## 脚本入口

### 1）初始化源文档

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_template.js \
  --output-dir /path/to/doc \
  --basename 示例项目-用户管理功能设计 \
  --title 用户管理功能设计 \
  --system 示例管理平台 \
  --project 示例项目
```

或使用 profile：

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_template.js \
  --profile ~/.workbuddy/skills/智能体需求文档生成skill/assets/examples/feature-design.profile.json
```

### 2）生成单个文档快照

直接指定源文件：

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --source /path/to/doc/示例项目-用户管理功能设计.md \
  --output-dir /path/to/doc
```

或使用 profile：

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --profile ~/.workbuddy/skills/智能体需求文档生成skill/assets/examples/single-generate.profile.json
```

### 3）按 manifest 批量生成

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --manifest ~/.workbuddy/skills/智能体需求文档生成skill/assets/examples/feature-design.manifest.json
```

如多个文档共享同一输出目录、归档目录等参数，可叠加 profile：

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --manifest ~/.workbuddy/skills/智能体需求文档生成skill/assets/examples/feature-design.manifest.json \
  --profile ~/.workbuddy/skills/智能体需求文档生成skill/assets/examples/batch-shared.profile.json
```

## 配置优先级

- 单文档模式：CLI 参数 > profile > 脚本默认值
- 批量模式：manifest 单项字段 > profile 公共字段 > 脚本默认值
- 因此推荐把"公共项"放到 profile，把"单文档差异项"放到 manifest 每个 document 条目中

## 执行约定

- 首次导入后，先进入 `scripts/` 目录执行一次 `npm install`，安装本地依赖
- 源文件默认使用无版本号文件名，例如 `示例项目-用户管理功能设计.md`
- 快照文件统一命名为 `{baseName}_{version}.md`
- 版本号优先从源 Markdown 中读取，建议在"文档信息"表中使用 `| 文档版本 | v0.1 |`
- 若源文档缺少版本号，脚本默认按 `v0.1` 处理
- 旧快照会自动移入输出目录下的 `backup/`
- 源文件负责承载业务真实内容，快照只负责版本化归档与对外交付

## 生成前检查

- 源文档是否存在
- 输出目录是否正确
- 文档版本与修订记录是否一致
- 需要保留的项目专属规范是否已经写入源文档、项目模板、项目参考文件或 skill 的通用参考文件
- 当前输出目录里是否存在需要保留的历史快照

## 交付完成标准

- 已保留无版本号源 Markdown
- 已生成与源文档一致的新版本 `.md` 快照
- 旧版本快照已归档到 `backup/`
- 如文档涉及合规内容，`7.1` 已按需引用 `通用等保三级安全要求`
- 文档内版本号、修订记录、文件名版本号三者一致

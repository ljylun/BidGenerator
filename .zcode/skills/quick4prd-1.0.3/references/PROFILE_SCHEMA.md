# PROFILE / MANIFEST 配置说明

本 skill 通过两种配置方式支持不同项目：

- **profile**：适合单个文档任务，也适合作为批量任务的“公共配置层”
- **manifest**：适合批量生成多个文档快照，用来描述每个文档的差异项

## 一、推荐理解方式

可以把配置拆成两层：

1. **profile 放公共项**：例如输出目录、系统名、项目名、归档目录名、自定义模板
2. **manifest 或 CLI 放差异项**：例如某个源文件路径、某个 baseName、某个特定标题

推荐优先级如下：

- 单文档模式：**CLI 参数 > profile > 默认值**
- 批量模式：**manifest 单项字段 > profile 公共字段 > 默认值**

## 二、profile 字段

profile 为一个 JSON 对象，常用字段如下：

| 字段 | 是否必填 | 用途 | 示例 |
| --- | --- | --- | --- |
| `outputDir` | 是（模板初始化时） | 输出目录 | `/absolute/path/to/doc` |
| `source` | 是（单文档生成时） | 源 Markdown 路径 | `/absolute/path/to/doc/用户管理功能设计.md` |
| `baseName` / `basename` | 否 | 快照基础文件名 | `示例项目-用户管理功能设计` |
| `documentTitle` / `title` | 否 | 文档标题 | `用户管理功能设计` |
| `projectName` / `project` | 否 | 项目名称 | `示例项目` |
| `systemName` / `system` | 否 | 系统名称 | `示例管理平台` |
| `documentCode` | 否 | 文档编号 | `PRD-USER-2026-001` |
| `owner` | 否 | 编制人 | `张三` |
| `createdDate` | 否 | 编制日期 | `2026-04-01` |
| `docVersion` | 否 | 初始文档版本 | `v0.1` |
| `moduleName` | 否 | 所属模块 | `账号与权限` |
| `menuPath` | 否 | 模块路径 | `系统管理 → 用户管理 → 用户列表` |
| `template` | 否 | 自定义模板路径 | `/absolute/path/to/template.md` |
| `backupDirName` | 否 | 旧快照归档目录名 | `backup` |

## 三、常见 profile 模板

### 1. 模板初始化 profile

适用于“我要先起一份首版源文档”。

```json
{
  "outputDir": "/absolute/path/to/project/doc",
  "baseName": "示例项目-用户管理功能设计",
  "documentTitle": "用户管理功能设计",
  "projectName": "示例项目",
  "systemName": "示例管理平台",
  "documentCode": "PRD-USER-2026-001",
  "owner": "张三",
  "createdDate": "2026-04-01",
  "docVersion": "v0.1",
  "moduleName": "账号与权限",
  "menuPath": "系统管理 → 用户管理 → 用户列表"
}
```

### 2. 单文档生成 profile

适用于“源文件已经写好了，我只想稳定出快照”。

```json
{
  "source": "/absolute/path/to/project/doc/示例项目-用户管理功能设计.md",
  "outputDir": "/absolute/path/to/project/doc",
  "baseName": "示例项目-用户管理功能设计",
  "backupDirName": "backup"
}
```

### 3. 批量任务公共配置 profile

适用于“多个文档共用同一个输出目录、归档目录或项目上下文”。

```json
{
  "outputDir": "/absolute/path/to/project/doc",
  "backupDirName": "backup"
}
```

## 四、manifest 格式

manifest 支持两种写法：

### 写法 A：直接使用数组

```json
[
  {
    "source": "/absolute/path/to/doc/示例项目-用户管理功能设计.md",
    "outputDir": "/absolute/path/to/doc",
    "baseName": "示例项目-用户管理功能设计"
  },
  {
    "source": "/absolute/path/to/doc/示例项目-角色管理功能设计.md",
    "outputDir": "/absolute/path/to/doc",
    "baseName": "示例项目-角色管理功能设计"
  }
]
```

### 写法 B：使用 `documents` 包装

```json
{
  "documents": [
    {
      "source": "/absolute/path/to/doc/示例项目-用户管理功能设计.md",
      "outputDir": "/absolute/path/to/doc",
      "baseName": "示例项目-用户管理功能设计"
    }
  ]
}
```

## 五、manifest + profile 组合建议

当多个文档共享相同输出目录、归档目录时，推荐：

- `profile` 里只放公共字段
- `manifest` 里只放每个文档的 `source`、`baseName` 等差异项

示例：

### profile

```json
{
  "outputDir": "/absolute/path/to/project/doc",
  "backupDirName": "backup"
}
```

### manifest

```json
{
  "documents": [
    {
      "source": "/absolute/path/to/project/doc/示例项目-用户管理功能设计.md",
      "baseName": "示例项目-用户管理功能设计"
    },
    {
      "source": "/absolute/path/to/project/doc/示例项目-角色管理功能设计.md",
      "baseName": "示例项目-角色管理功能设计"
    }
  ]
}
```

## 六、脚本使用建议

在首次使用前，请先进入 skill 的 `scripts/` 目录执行一次 `npm install`，安装本地依赖。

### 1. 初始化模板

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_template.js \
  --output-dir /absolute/path/to/doc \
  --basename 示例项目-用户管理功能设计 \
  --title 用户管理功能设计 \
  --system 示例管理平台 \
  --project 示例项目
```

### 2. 用 profile 初始化模板

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_template.js \
  --profile /absolute/path/to/feature-design.profile.json
```

### 3. 生成单个文档快照

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --source /absolute/path/to/doc/示例项目-用户管理功能设计.md \
  --output-dir /absolute/path/to/doc
```

### 4. 用 profile 生成单个文档快照

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --profile /absolute/path/to/single-generate.profile.json
```

### 5. 用 manifest 批量生成

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --manifest /absolute/path/to/feature-design.manifest.json
```

### 6. 用 manifest + profile 批量生成

```bash
/usr/local/bin/node ~/.workbuddy/skills/智能体需求文档生成skill/scripts/gen_from_md.js \
  --manifest /absolute/path/to/feature-design.manifest.json \
  --profile /absolute/path/to/batch-shared.profile.json
```

## 七、版本与归档规则

- 脚本优先从源 Markdown 中读取版本号，推荐在文档信息表中使用 `| 文档版本 | v0.1 |`
- 若未读取到版本号，脚本默认按 `v0.1` 处理
- 每次生成前，输出目录下同名旧快照会被移入 `backup/`（或自定义目录）
- 源文件本身不带版本后缀，版本号只用于快照文件

## 八、通用化约束

- skill 主体不维护任何项目专属 key 对照表
- 项目专属命名规则、角色、术语、章节细化要求，应写入项目自己的 profile、模板或源文档
- 如果团队对文档章节有进一步要求，优先新建自定义模板文件，再通过 `--template` 指定
- 如果团队已有更严格的修订、审批、发布规则，应在项目侧补充，不要写死在通用 skill 中

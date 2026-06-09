# BidGenerator - AI智能标书生成系统

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)

[English](ReadMe.md) | **中文**

---

## 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [核心功能](#核心功能)
- [环境要求](#环境要求)
- [安装与部署](#安装与部署)
- [项目结构](#项目结构)
- [使用说明](#使用说明)
- [开发规范](#开发规范)
- [参与贡献](#参与贡献)
- [常见问题](#常见问题)
- [许可证](#许可证)

---

## 项目概述

**BidGenerator** 是一款专为我国政府采购招投标流程设计的智能标书生成系统。系统采用AI技术，能够自动生成完整的投标文件，包括商务标、技术标、报价标三大模块，覆盖货物采购、服务项目、工程施工三大行业领域。

### 核心能力

- **智能生成**：基于招标文件自动生成完整标书
- **风险管控**：32项废标红线自查
- **多行业支持**：货物、服务、工程三大类模板
- **格式规范**：符合政府采购标准格式
- **智能校验**：报价一致性检查、格式规范性验证

---

## 技术栈

### 后端技术

| 技术 | 版本 | 作用 |
|------|------|------|
| **Python** | 3.8+ | 核心编程语言，承载所有业务逻辑 |
| **Markdown** | 3.4.4+ | 标书内容存储与处理的文档格式 |
| **python-docx** | 0.8.11+ | Word文档生成与操作 |
| **Pillow** | 9.5.0+ | 图片处理，支持文档图片嵌入 |
| **lxml** | 4.9.3+ | XML/HTML解析，处理文档结构 |
| **regex** | 2023.6.3+ | 高级文本模式匹配与处理 |
| **tqdm** | 4.65.0+ | 长时间操作的进度追踪 |
| **colorlog** | 6.7.0+ | 彩色日志输出 |

### 前端技术

本项目以后端为主，提供以下交互方式：

| 技术 | 作用 |
|------|------|
| **命令行界面 (CLI)** | 主要用户交互方式 |
| **Markdown编辑器** | 查看和编辑标书模板 |

### 基础设施与工具

| 类别 | 技术 | 作用 |
|------|------|------|
| **运行环境** | Python 3.8+ | 应用运行环境 |
| **包管理器** | pip | 依赖管理 |
| **版本控制** | Git | 源代码版本控制 |
| **许可证** | GPL v3.0 | 开源许可证 |
| **文档格式** | Markdown | 项目文档格式 |

### 外部依赖

| 依赖 | 作用 |
|------|------|
| **Microsoft Word** | 查看生成的.docx文件（可选） |
| **win32com.client** | Windows平台高级Word操作（仅Windows） |

---

## 核心功能

### 1. 完整标书生成

- ✅ **商务标**：投标函、授权委托书、资质证明文件
- ✅ **技术标**：技术方案、实施计划、团队配置
- ✅ **报价标**：报价表、偏离表、分项明细

### 2. 智能质量保障

- 🔍 **32项风险自查**：自动检测废标风险点
- 💰 **报价校验**：大小写金额一致性检查
- 📋 **格式合规**：符合政府采购标准
- ⚠️ **偏离标注**：自动标记负偏离项

### 3. 多行业模板

- 📦 **货物采购**：设备、材料、供应合同
- 🔧 **服务项目**：维护、咨询、专业服务
- 🏗️ **工程施工**：基础设施、建筑工程

### 4. 文档转换

- 🔄 **Markdown转Word**：高保真转换，保留格式
- 📄 **目录自动生成**：层级清晰的目录结构
- 🖼️ **图片嵌入**：支持本地图片资源
- 📊 **表格格式化**：专业表格布局与样式

---

## 环境要求

### 系统要求

- **操作系统**：Windows 10/11、macOS 10.15+、Linux (Ubuntu 18.04+)
- **Python版本**：3.8 或更高版本
- **内存**：最低4GB（推荐8GB）
- **磁盘空间**：500MB可用空间
- **其他软件**：
  - Git（版本控制）
  - Microsoft Word（可选，用于查看生成的文档）

### Python依赖

```txt
python-docx>=0.8.11
markdown>=3.4.4
Pillow>=9.5.0
lxml>=4.9.3
regex>=2023.6.3
tqdm>=4.65.0
colorlog>=6.7.0
pywin32>=306  # 仅Windows，用于高级Word操作
```

---

## 安装与部署

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/BidGenerator.git
cd BidGenerator
```

### 2. 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r md_to_word_converter/requirements.txt
```

Windows用户如需高级Word集成功能：
```bash
pip install pywin32>=306
```

### 4. 验证安装

```bash
python md_to_word_converter/md_to_word_converter.py --help
```

---

## 项目结构

```
BidGenerator/
├── doc/                                    # 文档模板与输出目录
│   ├── 招标正文.doc                         # 招标文件（输入）
│   ├── doc_content.txt                     # 提取的招标内容
│   ├── 商务标.md                           # 商务标模板
│   ├── 技术标.md                           # 技术标模板
│   ├── 报价标.md                           # 报价标模板
│   ├── 标书校验报告.md                      # 标书校验报告
│   └── 技术标/                             # 技术标分章节
│       ├── README.md                       # 技术标索引
│       ├── merge.py                        # 章节合并脚本
│       ├── 合并技术标.ps1                   # PowerShell合并脚本
│       ├── 技术标_完整版.md                 # 完整技术标
│       ├── 技术标_完整版.docx               # 完整技术标（Word版）
│       ├── 00_总目录.md                     # 总目录
│       ├── 01_需求理解.md                   # 需求理解
│       ├── 02_总体技术方案.md                # 总体技术方案
│       ├── 03_硬件维护方案.md                # 硬件维护方案
│       ├── 04_软件运维方案.md                # 软件运维方案
│       ├── 05_故障处理流程.md                # 故障处理流程
│       ├── 06_服务保障.md                    # 服务保障
│       ├── 07_技术团队与资源配置.md          # 技术团队与资源配置
│       ├── 08_技术保障与应急预案.md          # 技术保障与应急预案
│       ├── 09_同类项目案例.md                # 同类项目案例
│       ├── 10_技术参数响应表.md              # 技术参数响应表
│       └── 11_技术评分项响应索引.md          # 技术评分项响应索引
│
├── md_to_word_converter/                    # Markdown转Word转换模块
│   ├── README.md                           # 模块文档
│   ├── config.py                           # 配置文件
│   ├── md_to_word_converter.py             # 主转换器类
│   ├── requirements.txt                    # Python依赖
│   └── test_conversion.py                  # 单元测试
│
├── .trae/                                  # Trae AI助手配置
│   ├── skills/                             # 自定义技能
│   │   └── bid-tender/                     # 标书生成技能
│   │       ├── SKILL.md                    # 技能定义
│   │       ├── _meta.json                  # 技能元数据
│   │       └── references/                 # 参考文档
│   └── specs/                              # 规格说明
│       ├── bid-generation/                 # 标书生成规格
│       │   ├── spec.md                     # 规格文档
│       │   ├── checklist.md                # 实现清单
│       │   └── tasks.md                    # 任务分解
│       ├── tech-bid-500k/                  # 技术标规格（50万）
│       ├── tech-bid-enhancement/            # 技术标增强规格
│       ├── tech-bid-expansion/             # 技术标扩展规格
│       └── markdown-to-word-converter/     # 转换器规格
│
├── check_progress.py                       # 进度检查工具
├── file_length.txt                         # 文件大小信息
├── file_lines.txt                           # 行数统计信息
├── LICENSE                                 # GPL v3.0许可证
├── .gitignore                              # Git忽略规则
└── ReadMe-ZhCn.md                          # 本文件
```

---

## 使用说明

### 基础使用

1. **准备招标文件**：将招标文件（招标正文.doc）放入 `doc/` 目录

2. **提取内容**：运行内容提取脚本（仅Windows）：
   ```bash
   python doc/read_doc.py
   ```

3. **生成标书**：使用AI助手生成标书内容：
   ```bash
   # 示例：生成完整标书
   "请帮我生成一份服务项目标书。项目名称：XX园区物业管理服务，预算金额：120万元/年，投标单位：XX物业管理有限公司，服务期限：1年"
   ```

4. **转换为Word**：将生成的Markdown转换为Word格式：
   ```bash
   python md_to_word_converter/md_to_word_converter.py -i doc/技术标/技术标_完整版.md -o doc/技术标/技术标_完整版.docx
   ```

### 高级用法

**自定义输入/输出路径：**
```bash
python md_to_word_converter/md_to_word_converter.py \
  --input "path/to/input.md" \
  --output "path/to/output.docx" \
  --log "conversion.log" \
  --report "validation_report.txt"
```

**合并技术标章节：**
```bash
python doc/技术标/merge.py
```

**检查进度：**
```bash
python check_progress.py
```

---

## 开发规范

### 代码风格

- **语言**：Python 3.8+
- **风格指南**：遵循PEP 8规范
- **类型提示**：所有函数签名使用类型注解
- **文档字符串**：所有模块和类使用Google风格文档字符串
- **命名规范**：
  - 变量/函数：`snake_case`
  - 类：`PascalCase`
  - 常量：`UPPER_CASE`

### 项目约定

1. **文件编码**：UTF-8（Windows兼容可使用BOM）
2. **换行符**：首选LF（Unix风格），Windows可接受CRLF
3. **中文支持**：所有源文件必须支持中文字符
4. **错误处理**：使用try-except块，捕获特定异常类型
5. **日志记录**：使用`logging`模块，设置适当的日志级别

### 测试

```bash
# 运行单元测试
python -m pytest md_to_word_converter/test_conversion.py

# 详细输出模式
python -m pytest -v md_to_word_converter/test_conversion.py
```

### Pull Request流程

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

---

## 参与贡献

欢迎贡献！欢迎提交问题、功能请求或拉取请求。

### 如何贡献

1. **报告Bug**：创建Issue，附上详细的复现步骤
2. **建议功能**：创建Issue，描述您的功能需求
3. **提交代码**：Fork、修改并提交Pull Request
4. **完善文档**：帮助改进本文档和其他文档

### 行为准则

- 尊重与包容
- 聚焦建设性反馈
- 尊重知识产权

---

## 常见问题

### 常见问题

#### 1. 导入错误

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```bash
pip install -r md_to_word_converter/requirements.txt
```

#### 2. 编码错误

**问题**：读取中文文件时出现 `UnicodeDecodeError`

**解决方案**：确保文件以UTF-8编码保存。转换器自动检测多种编码（UTF-8、GBK、GB2312、GB18030）。

#### 3. 图片未找到警告

**问题**：Markdown中引用的图片缺失

**解决方案**：
- 检查Markdown中的图片路径是否正确
- 确保图片存在于预期位置
- 系统会为缺失的图片添加占位符

#### 4. Word应用程序错误（Windows）

**问题**：使用win32com时出现 `pywintypes.com_error`

**解决方案**：
- 确保已安装Microsoft Word
- 运行 `python -c "import win32com.client; print('OK')"` 测试COM连接
- 尝试以管理员身份运行

#### 5. 大文件内存问题

**问题**：处理大型标书时内存不足

**解决方案**：
- 系统分块处理大文件（默认1MB）
- 增加系统虚拟内存/交换空间
- 关闭其他内存密集型应用

### 性能优化建议

- 使用SSD存储提升文件I/O速度
- 为Python进程分配至少4GB内存
- 超过100页的文档建议分章节处理

---

## 许可证

本项目采用 **GNU通用公共许可证 v3.0** - 详见 [LICENSE](LICENSE) 文件。

### 关键条款

- ✅ 允许商业使用
- ✅ 允许修改
- ✅ 允许分发
- ✅ 允许私人使用
- ⚠️ 必须包含许可证和版权声明
- ⚠️ 修改内容必须文档化
- ⚠️ 分发时必须提供源代码

---

## 支持

- **问题反馈**：[GitHub Issues](https://github.com/yourusername/BidGenerator/issues)
- **文档**：本文档和代码内联文档
- **邮箱**：[your-email@example.com](mailto:your-email@example.com)

---

**用 ❤️ 为中国政府采购社区打造**

*最后更新：2026年6月*
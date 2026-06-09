# Markdown to Word Document Converter

Markdown转Word文档转换器 - 将Markdown文件转换为符合公文规范的Word文档。

## 功能特性

### 1. 完整内容转换
- ✅ 多级标题层级（h1-h6）
- ✅ 正文段落和换行
- ✅ 有序列表和无序列表（支持嵌套）
- ✅ 代码块（带语法高亮标记）
- ✅ 表格（支持合并单元格）
- ✅ 图片引用（本地相对路径）
- ✅ 引用块（blockquote）
- ✅ 文本格式：加粗、斜体、下划线、删除线
- ✅ 数学公式（LaTeX格式）
- ✅ 流程图（Mermaid/PlantUML）
- ✅ 脚注和链接

### 2. 公文规范样式
- ✅ **页边距**：上下2.54cm、左右3.17cm
- ✅ **正文字体**：宋体（SimSun），小四（12pt）
- ✅ **标题字体**：黑体（SimHei），按层级设置大小
  - 一级标题（h1）：二号（22pt）
  - 二级标题（h2）：三号（16pt）
  - 三级标题（h3）：四号（14pt）
  - 四级标题（h4）：小四（12pt）加粗
  - 五级标题（h5）：小四（12pt）
  - 六级标题（h6）：小四（12pt）斜体
- ✅ **行间距**：固定值22磅
- ✅ **段落间距**：段前0行，段后0行
- ✅ **目录**：自动生成包含所有标题层级的目录索引

### 3. 本地资源处理
- ✅ 检测Markdown中引用的图片路径
- ✅ 将图片嵌入到Word文档对应位置
- ✅ 对于缺失的图片，在对应位置添加占位符并记录日志
- ✅ 保持资源在文档中的相对位置关系

### 4. 兼容性
- ✅ Microsoft Office 2019及以上版本
- ✅ WPS Office 2021及以上版本
- ✅ 输出格式：.docx（Office Open XML格式）

### 5. 异常处理
- ✅ 源文件不存在：输出清晰错误日志，程序优雅退出
- ✅ 资源加载失败：记录失败资源路径，继续转换其他内容
- ✅ 格式转换错误：记录错误位置和原因，跳过错误部分继续
- ✅ 内存不足：对于大文件采用流式处理，避免一次性加载
- ✅ 权限问题：检测输出目录写权限，无权限时提示用户

### 6. 全量校验
- ✅ 内容完整性校验：对比源文件和Word文档的段落数、字数
- ✅ 格式规范性校验：检查标题层级、列表结构、表格数量
- ✅ 资源可用性校验：确认所有引用的资源已正确嵌入
- ✅ 生成校验报告：输出详细的校验结果报告

## 使用方法

### 安装依赖

```bash
cd md_to_word_converter
pip install -r requirements.txt
```

### 基本使用

```bash
# 使用默认配置（转换技术标_完整版.md）
python md_to_word_converter.py

# 指定输入和输出文件
python md_to_word_converter.py -i input.md -o output.docx

# 指定日志和报告文件
python md_to_word_converter.py --log conversion.log --report report.txt
```

### 命令行参数

- `-i, --input`: 输入Markdown文件路径
- `-o, --output`: 输出Word文件路径
- `--log`: 日志文件路径
- `--report`: 校验报告路径

## 项目结构

```
md_to_word_converter/
├── requirements.txt          # 依赖包列表
├── config.py                 # 配置文件（样式、路径等）
├── md_to_word_converter.py   # 主程序
├── test_conversion.py        # 测试脚本
└── README.md                 # 说明文档
```

## 输出文件

转换完成后会生成以下文件：

1. **Word文档**：`doc\技术标\技术标_完整版.docx`
2. **校验报告**：`doc\技术标\conversion_report.txt`
3. **日志文件**：`doc\技术标\conversion.log`

## 转换统计

最近一次转换结果：

- **源文件大小**：1.01 MB
- **总行数**：16,173 行
- **总字符数**：498,477 字符
- **标题数**：899 个
  - H1: 11 个
  - H2: 110 个
  - H3: 424 个
  - H4: 354 个
- **段落数**：1,823 个
- **表格数**：658 个
- **代码块数**：43 个
- **列表数**：618 个
- **引用块数**：17 个
- **错误数**：0
- **警告数**：0

## 校验结果

```
总体结果: 通过

详细结果:
  - 内容完整性: 通过
  - 格式规范性: 通过
  - 资源可用性: 通过
```

## 技术栈

- **Python 3.13**
- **python-docx**: Word文档生成
- **Markdown**: Markdown解析
- **Pillow**: 图片处理
- **lxml**: XML处理
- **tqdm**: 进度显示
- **colorlog**: 彩色日志

## 许可证

MIT License

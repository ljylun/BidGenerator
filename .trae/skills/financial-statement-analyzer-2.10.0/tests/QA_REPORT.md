# QA 验证报告 — 财务报表分析专家 (Financial Statement Analyzer)

> **执行人**: Edward (QA Engineer)  
> **日期**: 2026-06-17  
> **版本**: v1.1.0  
> **测试范围**: 多格式解析增强（新增4源文件 + 修改5源文件 + 新增2测试文件）

---

## 📊 总览

| 维度 | 状态 | 评分 |
|------|------|------|
| 代码质量 (pylint + pyflakes) | ⚠️ 通过（有建议） | 8.9/10 |
| 接口一致性 | ✅ 通过 | 10/10 |
| 向后兼容 | ✅ 通过 | 10/10 |
| 路由正确性 | ⚠️ 通过（.tif 未路由） | 9/10 |
| 降级处理 | ✅ 通过 | 10/10 |
| 测试覆盖 | ✅ 通过 | 10/10 |

> **综合评分**: **9.4 / 10** 🟢 优秀

---

## 1. 代码质量

### pylint 评分: **8.91 / 10**

### pyflakes — 源码问题（反馈给 Engineer）

| # | 文件 | 行号 | 问题 | 严重度 |
|---|------|------|------|--------|
| SRC-001 | `scripts/parse_router.py` | 21 | `re` imported but unused | 🟡 低 |
| SRC-002 | `scripts/parse_docx.py` | 58 | `copy` imported but unused | 🟡 低 |
| SRC-003 | `scripts/parse_excel.py` | 13 | `Tuple` imported but unused | 🟡 低 |
| SRC-004 | `scripts/parse_router.py` | 427-429 | `KNOWN_IMAGE_EXTENSIONS` 包含 `.tif` 但 `_detect_by_extension()` 未处理 | 🟠 中 |
| SRC-005 | `parse_audit_report.py` ↔ `parse_docx.py` | — | 循环导入（惰性导入，运行时安全但设计不佳） | 🟡 低 |

### pyflakes — `__init__.py` (false positives, re-export pattern)

`scripts/__init__.py` 中的所有 "imported but unused" 警告均为 re-export 模式的误报，无需处理。

### pyflakes — QA 测试代码（已自行修复）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| QA-001 | `tests/test_parse_router.py:12` | `io` imported but unused | ✅ 已修复 |
| QA-002 | `tests/test_parse_image.py:108` | `bright_pixels` assigned but never used | ✅ 已修复（增加断言） |
| QA-003 | `tests/test_parse_image.py:300` | `ImageFont` imported but unused | ✅ 已修复 |

---

## 2. 接口一致性验证

### 统一输出格式检查

所有解析器均返回 `{balance_sheet, income_statement, cash_flow, metadata}` 核心字典：

| 解析器 | balance_sheet | income_statement | cash_flow | metadata | 额外顶层键 |
|--------|:---:|:---:|:---:|:---:|------|
| `parse_excel()` | ✅ | ✅ | ✅ | ✅ | — |
| `parse_pdf()` | ✅ | ✅ | ✅ | ✅ | `tables`, `text` (向后兼容) |
| `parse_paste()` | ✅ | ✅ | ✅ | ✅ | — |
| `parse_image()` | ✅ | ✅ | ✅ | ✅ | — |
| `parse_docx()` | ✅ | ✅ | ✅ | ✅ | — |
| `parse_audit_report_from_pdf()` | ✅ | ✅ | ✅ | ✅ | `tables`, `text` (继承自 pdf) |
| `parse_audit_report_from_docx()` | ✅ | ✅ | ✅ | ✅ | — |
| `parse_financial_document()` | ✅ | ✅ | ✅ | ✅ | — |
| `parse_pasted_text_as_document()` | ✅ | ✅ | ✅ | ✅ | — |

### metadata 必需字段检查

所有解析器的 metadata 均包含必需字段：
- `source` / `source_format` / `extraction_method` / `extraction_confidence` / `warnings` / `audit_report_detected`

✅ **接口一致性通过**

---

## 3. 向后兼容验证

| 旧版 API | 签名变化 | 输出变化 | 结论 |
|----------|---------|---------|:--:|
| `parse_excel(filepath, sheet_names, header_row)` | 无变化 | 无变化 | ✅ |
| `parse_pdf(filepath, **kwargs)` | 无变化 | 新增 `tables`/`text` 顶层键 + `audit_report_detected` | ✅ |
| `parse_pasted_text(text)` | 无变化 | 无变化 | ✅ |

> `parse_pdf` 新增的 `tables`/`text` 为加法性变更，不影响旧版代码访问 `balance_sheet` 等字段。

✅ **向后兼容通过**

---

## 4. 路由正确性

### 扩展名路由覆盖矩阵

| 承诺格式 | `_detect_by_extension()` | `detect_file_type()` | 状态 |
|----------|:---:|:---:|:--:|
| `.xlsx` | `excel` | `excel` | ✅ |
| `.xls` | `excel` | `excel` | ✅ |
| `.csv` | `excel` | `excel` | ✅ |
| `.pdf` | `pdf` | `pdf` | ✅ |
| `.png` | `image` | `image` | ✅ |
| `.jpg` | `image` | `image` | ✅ |
| `.jpeg` | `image` | `image` | ✅ |
| `.tiff` | `image` | `image` | ✅ |
| `.bmp` | `image` | `image` | ✅ |
| `.webp` | `image` | `image` | ✅ |
| `.docx` | `docx` | `docx` | ✅ |
| **`.tif`** | **`None` ❌** | `unknown` | ⚠️ **缺失** |
| `.xyz` | `None` | `unknown` | ✅ (预期) |

### 魔数检测验证

| 场景 | 扩展名 | 文件头魔数 | 结果 | 状态 |
|------|--------|-----------|------|:--:|
| PDF 伪造为 .xyz | `.xyz` | `%PDF-1.4` | `pdf` | ✅ |
| PNG 伪造为 .xyz | `.xyz` | `\x89PNG...` | `image` | ✅ |
| JPEG 伪造为 .txt | `.txt` | `\xff\xd8\xff` | `image` | ✅ |
| PNG 伪造为 .txt | `.txt` | `\x89PNG...` | `image` | ✅ |

> 魔数检测正确优先于扩展名，防伪造机制有效。

⚠️ **路由正确性：9/10** — `.tif` 扩展名在 `KNOWN_IMAGE_EXTENSIONS` 中声明但 `_detect_by_extension()` 未处理。

---

## 5. 降级处理验证

| 场景 | 解析器 | 行为 | 状态 |
|------|--------|------|:--:|
| 文件不存在 | `parse_router` | 返回空数据 + `"文件不存在"` warning | ✅ |
| 未知格式 (.xyz) | `parse_router` | 返回空数据 + 格式不支持 warning | ✅ |
| 无扩展名 | `parse_router` | 返回 `unknown` | ✅ |
| pytesseract 未安装 | `parse_image` | `RuntimeError` → 捕获返回 warning | ✅ |
| Tesseract OCR 不可用 | `parse_image` | `RuntimeError` → 捕获返回 warning | ✅ |
| python-docx 未安装 | `parse_docx` | 返回空数据 + 安装提示 warning | ✅ |
| python-docx 未安装 | `parse_router` (docx路由) | 返回空数据 + 安装提示 warning | ✅ |
| pdfplumber 未安装 | `parse_audit_report_from_pdf` | 返回空数据 + 安装提示 warning | ✅ |
| PDF 无表格（扫描图片） | `parse_pdf` | 返回文本 + warning 建议 OCR | ✅ |
| DOCX 无表格 | `parse_docx` | 返回空数据 + 无表格 warning | ✅ |
| OCR 置信度低 (<30%) | `parse_image` | 返回数据 + 低置信度 warning | ✅ |
| 粘贴空文本 | `parse_pasted_text_as_document` | `PasteParseError` 被捕获降级 | ✅ |
| ParseError 异常 | `parse_router` | 全局 try/except 兜底 | ✅ |

✅ **降级处理通过** — 所有错误场景均优雅降级，不抛未捕获异常。

---

## 6. 测试覆盖

### 测试通过率: **120 / 120 = 100%** ✅

| 测试文件 | 测试数 | 通过 | 说明 |
|----------|:---:|:---:|------|
| `tests/test_parse_router.py` | 27 | 27 | 🆕 路由器测试 |
| `tests/test_parse_image.py` | 27 | 27 | 🆕 图片OCR测试 |
| `tests/test_ratios.py` | 10 | 10 | 现有 |
| `tests/test_mscore.py` | 9 | 9 | 现有 |
| `tests/test_redflags.py` | 7 | 7 | 现有 |
| `tests/test_integration.py` | 40 | 40 | 现有 |
| **合计** | **120** | **120** | |

### 新增测试覆盖矩阵 (v1.1.0)

| 测试类 | 数量 | 覆盖内容 |
|--------|:---:|------|
| `TestDetectFileType` | 13 | 所有承诺格式的扩展名检测 + unknown + 无扩展名 |
| `TestMagicDetection` | 4 | PDF/PNG/JPEG 魔数检测 + 伪造扩展名防御 |
| `TestRouterDispatch` | 4 | 未知格式降级、文件不存在、metadata 完整性、Excel路由 |
| `TestKnownExtensions` | 4 | KNOWN_*_EXTENSIONS 常量完整性 |
| `TestPastedTextRouting` | 2 | 粘贴文本路由 + 空文本降级 |
| `TestImagePreprocessing` | 4 | 有效图片、不存在文件、小尺寸图片、暗图二值化 |
| `TestKeywordDetection` | 5 | BS/IS/CF 关键词分类 + 无关键词 + 单关键词不足 |
| `TestTableDetection` | 3 | 简单表格、纯文本、两列表格 |
| `TestConfidence` | 3 | 高置信度、低置信度、范围检查 |
| `TestParseImageMain` | 3 | 不存在文件降级、返回结构、默认语言 |
| `TestSectionExtraction` | 2 | 段落提取 + 不存在的表类型 |
| `TestNumericDetection` | 7 | 纯数字、逗号、负数、百分比、非数值、货币符号、中文单位 |
| **合计新增** | **54** | |

---

## 7. SKILL.md 验证

| 检查项 | 状态 |
|--------|:--:|
| 版本号更新至 v1.1.0 | ✅ |
| 触发格式包含全部10种扩展名 | ✅ |
| 输入规范表格包含 OCR/DOCX/审计报告/路由 | ✅ |
| 统一输出格式文档完整 | ✅ |
| 依赖列表包含 `pytesseract>=0.3.10` | ✅ |
| 依赖列表包含 `python-docx>=1.1.0` | ✅ |
| 依赖列表包含 `Pillow>=10.0.0` | ✅ |
| 系统依赖 `tesseract-ocr` + `tesseract-ocr-chi-sim` | ✅ |
| 版本历史记录 v1.1.0 变更 | ✅ |

---

## 8. 路由决策

### 源码 Bug（→ 反馈给 Engineer）

| Bug ID | 文件 | 描述 | 严重度 | 建议修复 |
|--------|------|------|:--:|------|
| **BUG-001** | `scripts/parse_router.py:79` | `KNOWN_IMAGE_EXTENSIONS` 包含 `.tif` 但 `_detect_by_extension()` 的 `image_exts` 集合中缺少 `.tif`，导致 `.tif` 文件被路由为 `unknown` | 🟠 中 | 在 `image_exts` 集合中添加 `.tif` |
| SRC-001~003 | 多个文件 | 未使用的 import | 🟡 低 | 清理即可 |
| SRC-005 | parse_audit_report ↔ parse_docx | 循环导入（惰性导入，运行时安全） | 🟡 低 | 提取共享接口到独立模块 |

### QA 测试代码修复（已自行完成）

| Fix ID | 修复内容 | 状态 |
|--------|---------|:--:|
| QA-FIX-001 | `tests/test_parse_router.py`: 移除未使用的 `import io` | ✅ |
| QA-FIX-002 | `tests/test_parse_image.py:108`: `bright_pixels` 增加断言 | ✅ |
| QA-FIX-003 | `tests/test_parse_image.py:300`: 移除未使用的 `ImageFont` | ✅ |

### 最终路由

> **Send To: Engineer** — BUG-001（.tif 路由缺失）需修复，其余为低优先级代码整洁问题。

---

## 9. 总结

### 质量亮点
- ✅ 全量 120 测试通过，回归零失败
- ✅ 统一路由引擎设计优秀：扩展名+魔数双重检测，防伪造
- ✅ 降级处理完善：OCR/DOCX/PDF 不可用时优雅返回 + 安装指引
- ✅ 接口一致性严格：所有9个解析入口遵循统一 `{balance_sheet, income_statement, cash_flow, metadata}` 契约
- ✅ 向后兼容：旧版 `parse_excel/parse_pdf/parse_pasted_text` API 完全不变
- ✅ SKILL.md 文档完整，依赖声明齐全
- ✅ 图片预处理管道完整：灰度→二值化→去噪→锐化

### 待改进
1. ⚠️ **BUG-001**: `.tif` 扩展名路由缺失（1行修复）
2. 🟡 清理3处未使用 import
3. 🟡 审计报告解析器与 DOCX 解析器的循环导入可优化
4. 💡 建议增加 `parse_docx`、`parse_audit_report` 的独立单元测试（当前仅通过路由器间接测试）

---

> **QA 签署**: Edward | **结论**: 🟢 **通过** — 修复 BUG-001 后建议发布 v1.1.0

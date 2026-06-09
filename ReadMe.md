# BidGenerator - AI-Powered Bid Document Generation System

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)

**English** | [中文](ReadMe-ZhCn.md)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Development Guidelines](#development-guidelines)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Project Overview

**BidGenerator** is an intelligent bid document generation system designed for Chinese government procurement and bidding processes. It leverages AI technology to automatically generate complete bid documents including commercial proposals, technical proposals, and pricing proposals across three major industries: goods procurement, service projects, and engineering construction.

### Key Capabilities

- **Automated Generation**: Complete bid document generation from tender requirements
- **Risk Assessment**: 32-point bid rejection risk self-inspection
- **Multi-Industry Support**: Templates for goods, services, and engineering sectors
- **Format Compliance**: Standardized formatting meeting government procurement standards
- **Intelligent Validation**: Automatic price consistency checks and format validation

---

## Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core programming language for all business logic |
| **Markdown** | 3.4.4+ | Document format for bid content storage and processing |
| **python-docx** | 0.8.11+ | Word document generation and manipulation |
| **Pillow** | 9.5.0+ | Image processing for document embedding |
| **lxml** | 4.9.3+ | XML/HTML parsing for document structure |
| **regex** | 2023.6.3+ | Advanced text pattern matching and processing |
| **tqdm** | 4.65.0+ | Progress tracking for long-running operations |
| **colorlog** | 6.7.0+ | Enhanced logging with color-coded output |

### Frontend Technologies

This project is primarily a backend-focused system with the following interface components:

| Technology | Purpose |
|------------|---------|
| **Command Line Interface (CLI)** | Primary user interaction method |
| **Markdown Editors** | For viewing and editing bid templates |

### Infrastructure & Tools

| Category | Technology | Purpose |
|----------|------------|---------|
| **Runtime** | Python 3.8+ | Application runtime environment |
| **Package Manager** | pip | Dependency management |
| **Version Control** | Git | Source code version control |
| **License** | GPL v3.0 | Open-source license |
| **Documentation** | Markdown | Project documentation format |

### External Dependencies

| Dependency | Purpose |
|------------|---------|
| **Microsoft Word** | For viewing generated .docx files (optional) |
| **win32com.client** | For advanced Word document operations (Windows only) |

---

## Features

### 1. Complete Bid Document Generation

- ✅ **Commercial Section**: Bid letters, authorization letters, qualification documents
- ✅ **Technical Section**: Technical solutions, implementation plans, team configurations
- ✅ **Pricing Section**: Price schedules, deviation tables, cost breakdowns

### 2. Intelligent Quality Assurance

- 🔍 **32-Point Risk Inspection**: Automatic detection of bid rejection risks
- 💰 **Price Validation**: Consistency checks between Chinese and Arabic numerals
- 📋 **Format Compliance**: Adherence to government procurement standards
- ⚠️ **Deviation Highlighting**: Automatic marking of negative deviations

### 3. Multi-Industry Templates

- 📦 **Goods Procurement**: Equipment, materials, and supply contracts
- 🔧 **Service Projects**: Maintenance, consulting, and professional services
- 🏗️ **Engineering Construction**: Infrastructure and construction projects

### 4. Document Conversion

- 🔄 **Markdown to Word**: High-fidelity conversion preserving formatting
- 📄 **Table of Contents**: Automatic generation with proper hierarchy
- 🖼️ **Image Embedding**: Support for local image resources
- 📊 **Table Formatting**: Professional table layouts with styling

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python Version**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 500MB free space
- **Additional Software**: 
  - Git (for version control)
  - Microsoft Word (optional, for viewing generated documents)

### Python Dependencies

```txt
python-docx>=0.8.11
markdown>=3.4.4
Pillow>=9.5.0
lxml>=4.9.3
regex>=2023.6.3
tqdm>=4.65.0
colorlog>=6.7.0
pywin32>=306  # Windows only, for advanced Word operations
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/BidGenerator.git
cd BidGenerator
```

### 2. Create Virtual Environment (Recommended)

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

### 3. Install Dependencies

```bash
pip install -r md_to_word_converter/requirements.txt
```

For Windows users requiring advanced Word integration:
```bash
pip install pywin32>=306
```

### 4. Verify Installation

```bash
python md_to_word_converter/md_to_word_converter.py --help
```

---

## Project Structure

```
BidGenerator/
├── doc/                                    # Document templates and outputs
│   ├── 招标正文.doc                         # Tender document (input)
│   ├── doc_content.txt                     # Extracted tender content
│   ├── 商务标.md                           # Commercial bid template
│   ├── 技术标.md                           # Technical bid template
│   ├── 报价标.md                           # Pricing bid template
│   ├── 标书校验报告.md                      # Bid validation report
│   └── 技术标/                             # Technical bid sections
│       ├── README.md                       # Technical section index
│       ├── merge.py                        # Section merge script
│       ├── 合并技术标.ps1                   # PowerShell merge script
│       ├── 技术标_完整版.md                 # Complete technical bid
│       ├── 技术标_完整版.docx               # Complete technical bid (Word)
│       ├── 00_总目录.md                     # Master table of contents
│       ├── 01_需求理解.md                   # Requirements understanding
│       ├── 02_总体技术方案.md                # Overall technical solution
│       ├── 03_硬件维护方案.md                # Hardware maintenance plan
│       ├── 04_软件运维方案.md                # Software maintenance plan
│       ├── 05_故障处理流程.md                # Fault handling process
│       ├── 06_服务保障.md                    # Service assurance
│       ├── 07_技术团队与资源配置.md          # Team & resource allocation
│       ├── 08_技术保障与应急预案.md          # Technical support & emergency plan
│       ├── 09_同类项目案例.md                # Similar project cases
│       ├── 10_技术参数响应表.md              # Technical parameter response table
│       └── 11_技术评分项响应索引.md          # Technical scoring criteria index
│
├── md_to_word_converter/                    # Markdown to Word conversion module
│   ├── README.md                           # Module documentation
│   ├── config.py                           # Configuration settings
│   ├── md_to_word_converter.py             # Main converter class
│   ├── requirements.txt                    # Python dependencies
│   └── test_conversion.py                  # Unit tests
│
├── .trae/                                  # Trae AI assistant configuration
│   ├── skills/                             # Custom skills
│   │   └── bid-tender/                     # Bid generation skill
│   │       ├── SKILL.md                    # Skill definition
│   │       ├── _meta.json                  # Skill metadata
│   │       └── references/                 # Reference documents
│   └── specs/                              # Specifications
│       ├── bid-generation/                 # Bid generation spec
│       │   ├── spec.md                     # Specification document
│       │   ├── checklist.md                # Implementation checklist
│       │   └── tasks.md                    # Task breakdown
│       ├── tech-bid-500k/                  # Technical bid spec (500k)
│       ├── tech-bid-enhancement/            # Technical bid enhancement spec
│       ├── tech-bid-expansion/             # Technical bid expansion spec
│       └── markdown-to-word-converter/     # Converter spec
│
├── check_progress.py                       # Progress checking utility
├── file_length.txt                         # File size information
├── file_lines.txt                           # Line count information
├── LICENSE                                 # GPL v3.0 License
├── .gitignore                              # Git ignore rules
└── ReadMe.md                               # This file
```

---

## Usage

### Basic Usage

1. **Prepare Tender Document**: Place your tender document (招标正文.doc) in the `doc/` directory

2. **Extract Content**: Run the content extraction script (Windows only):
   ```bash
   python doc/read_doc.py
   ```

3. **Generate Bid Document**: Use the AI assistant to generate bid content:
   ```bash
   # Example: Generate a complete bid document
   "请帮我生成一份服务项目标书。项目名称：XX园区物业管理服务，预算金额：120万元/年，投标单位：XX物业管理有限公司，服务期限：1年"
   ```

4. **Convert to Word**: Convert the generated Markdown to Word format:
   ```bash
   python md_to_word_converter/md_to_word_converter.py -i doc/技术标/技术标_完整版.md -o doc/技术标/技术标_完整版.docx
   ```

### Advanced Usage

**Custom Input/Output Paths:**
```bash
python md_to_word_converter/md_to_word_converter.py \
  --input "path/to/input.md" \
  --output "path/to/output.docx" \
  --log "conversion.log" \
  --report "validation_report.txt"
```

**Merge Technical Sections:**
```bash
python doc/技术标/merge.py
```

**Check Progress:**
```bash
python check_progress.py
```

---

## Development Guidelines

### Code Style

- **Language**: Python 3.8+
- **Style Guide**: PEP 8 compliance
- **Type Hints**: Use type annotations for all function signatures
- **Docstrings**: Google-style docstrings for all modules and classes
- **Naming**: 
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Project Conventions

1. **File Encoding**: UTF-8 (with BOM for Windows compatibility)
2. **Line Endings**: LF (Unix-style) preferred, CRLF acceptable for Windows
3. **Chinese Support**: All source files must support Chinese characters
4. **Error Handling**: Use try-except blocks with specific exception types
5. **Logging**: Use the `logging` module with appropriate log levels

### Testing

```bash
# Run unit tests
python -m pytest md_to_word_converter/test_conversion.py

# Run with verbose output
python -m pytest -v md_to_word_converter/test_conversion.py
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### How to Contribute

1. **Report Bugs**: Open an issue with detailed reproduction steps
2. **Suggest Features**: Open an issue describing your feature request
3. **Submit Code**: Fork, modify, and submit a pull request
4. **Improve Documentation**: Help us improve this README and other docs

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Respect intellectual property rights

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
```bash
pip install -r md_to_word_converter/requirements.txt
```

#### 2. Encoding Errors

**Problem**: `UnicodeDecodeError` when reading Chinese files

**Solution**: Ensure files are saved with UTF-8 encoding. The converter automatically detects multiple encodings (UTF-8, GBK, GB2312, GB18030).

#### 3. Image Not Found Warnings

**Problem**: Images referenced in Markdown are missing

**Solution**: 
- Check that image paths in Markdown are correct
- Ensure images exist in the expected locations
- The system will add placeholders for missing images

#### 4. Word Application Errors (Windows)

**Problem**: `pywintypes.com_error` when using win32com

**Solution**:
- Ensure Microsoft Word is installed
- Run `python -c "import win32com.client; print('OK')"` to test COM connection
- Try running as administrator

#### 5. Memory Issues with Large Files

**Problem**: System runs out of memory with large bid documents

**Solution**:
- The system processes large files in chunks (1MB default)
- Increase system virtual memory/swap space
- Close other memory-intensive applications

### Performance Tips

- Use SSD storage for faster file I/O
- Allocate at least 4GB RAM for the Python process
- For documents >100 pages, consider splitting into sections

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### Key Points

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Must include license and copyright notice
- ⚠️ Changes must be documented
- ⚠️ Source code must be made available when distributing

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/BidGenerator/issues)
- **Documentation**: This README and inline code documentation
- **Email**: [your-email@example.com](mailto:your-email@example.com)

---

**Made with ❤️ for the Chinese government procurement community**

*Last Updated: June 2026*
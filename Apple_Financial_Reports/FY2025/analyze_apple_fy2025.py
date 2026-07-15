#!/usr/bin/env python3
"""Apple FY2025 Financial Statements Analyzer
Parses 4 quarterly PDF reports and runs full financial analysis pipeline."""

import sys
import os
import json
import logging
import importlib

# Add skill scripts to path
SKILL_DIR = r"h:\DEV\MyProjects\BidGenerator\.trae\skills\financial-statement-analyzer-2.10.0\scripts"
sys.path.insert(0, SKILL_DIR)

# Fix relative imports in the skill scripts
# We need to import the package properly
import types
skill_package = types.ModuleType('financial_skill')
skill_package.__path__ = [SKILL_DIR]
sys.modules['financial_skill'] = skill_package

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# File paths
REPORT_DIR = r"h:\DEV\MyProjects\BidGenerator\Apple_Financial_Reports\FY2025\Financial_Statements"
OUTPUT_DIR = r"h:\DEV\MyProjects\BidGenerator\Apple_Financial_Reports\FY2025\Analysis_Reports"

PDF_FILES = [
    "FY2025_Q1_Financial_Statements.pdf",
    "FY2025_Q2_Financial_Statements.pdf",
    "FY25_Q3_Consolidated_Financial_Statements.pdf",
    "FY25_Q4_Consolidated_Financial_Statements.pdf",
]

QUARTERS = ["Q1 FY2025", "Q2 FY2025", "Q3 FY2025", "Q4 FY2025"]


def safe_import(module_name, alias=None):
    """Safely import a module from skill scripts directory."""
    try:
        spec = importlib.util.spec_from_file_location(
            module_name, 
            os.path.join(SKILL_DIR, f"{module_name}.py")
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Failed to import {module_name}: {e}")
        return None


def parse_all_pdfs():
    """Parse all PDF files and return raw results."""
    # Import parse_router with proper setup
    parse_router = safe_import('parse_router')
    if parse_router is None:
        logger.error("Cannot load parse_router module")
        return {}
    
    results = {}
    for i, filename in enumerate(PDF_FILES):
        filepath = os.path.join(REPORT_DIR, filename)
        logger.info(f"Parsing {filename}...")
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            continue
            
        try:
            result = parse_router.parse_financial_document(filepath)
            results[QUARTERS[i]] = result
            
            # Log extraction quality
            meta = result.get("metadata", {})
            logger.info(f"  Confidence: {meta.get('extraction_confidence', 'N/A')}")
            logger.info(f"  Warnings: {len(meta.get('warnings', []))}")
            
            if result.get("balance_sheet") is not None:
                logger.info(f"  Balance sheet: detected")
            if result.get("income_statement") is not None:
                logger.info(f"  Income statement: detected")
            if result.get("cash_flow") is not None:
                logger.info(f"  Cash flow: detected")
                
        except Exception as e:
            logger.error(f"  Failed to parse: {e}")
            import traceback
            traceback.print_exc()
    
    return results


def extract_data_from_pdf_direct(pdf_path):
    """Directly extract tabular data from PDF using pdfplumber."""
    try:
        import pdfplumber
        import pandas as pd
    except ImportError:
        logger.error("Required packages not installed: pdfplumber, pandas")
        return {}, {}, {}
    
    bs_data = {}
    is_data = {}
    cf_data = {}
    
    bs_keywords = ['assets', 'liabilities', 'stockholders', 'equity', 'cash and cash', 
                   'receivable', 'inventory', 'total current', 'total assets', 'total liabilities']
    is_keywords = ['net sales', 'revenue', 'cost of', 'gross margin', 'operating', 
                   'income', 'earnings per share', 'net income']
    cf_keywords = ['operating activities', 'investing activities', 'financing activities',
                   'cash generated', 'cash used', 'cash and cash equivalents']
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"  PDF has {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Analyze table content
                    table_text = str(table).lower()
                    
                    # Determine table type
                    bs_score = sum(1 for kw in bs_keywords if kw in table_text)
                    is_score = sum(1 for kw in is_keywords if kw in table_text)
                    cf_score = sum(1 for kw in cf_keywords if kw in table_text)
                    
                    # Extract data from rows
                    data_dict = {}
                    for row in table:
                        if not row or len(row) < 2:
                            continue
                        
                        key = str(row[0]).strip() if row[0] else ""
                        if not key or key.lower() in ['nan', 'none', '', ' ']:
                            continue
                        
                        # Try to get the numeric value
                        for val in reversed(row[1:]):
                            if val and str(val).strip():
                                try:
                                    clean = str(val).replace(',', '').replace('(', '-').replace(')', '').strip()
                                    # Remove any text annotations
                                    for suffix in ['million', 'billion', 'thousand']:
                                        if suffix in clean.lower():
                                            clean = clean.lower().replace(suffix, '').strip()
                                    num_val = float(clean)
                                    data_dict[key] = num_val
                                    break
                                except (ValueError, TypeError):
                                    continue
                    
                    # Assign to appropriate statement
                    if bs_score >= 3 and bs_score >= is_score and bs_score >= cf_score:
                        bs_data.update(data_dict)
                        logger.info(f"    Page {page_num+1}: Found balance sheet ({len(data_dict)} items)")
                    elif is_score >= 3 and is_score >= cf_score:
                        is_data.update(data_dict)
                        logger.info(f"    Page {page_num+1}: Found income statement ({len(data_dict)} items)")
                    elif cf_score >= 2:
                        cf_data.update(data_dict)
                        logger.info(f"    Page {page_num+1}: Found cash flow ({len(data_dict)} items)")
                        
    except Exception as e:
        logger.error(f"  PDF extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    return bs_data, is_data, cf_data


def parse_all_pdfs_direct():
    """Parse all PDF files using direct extraction."""
    results = {}
    
    for i, filename in enumerate(PDF_FILES):
        filepath = os.path.join(REPORT_DIR, filename)
        logger.info(f"Parsing {filename}...")
        
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            continue
        
        bs, inc, cf = extract_data_from_pdf_direct(filepath)
        
        results[QUARTERS[i]] = {
            "balance_sheet": bs,
            "income_statement": inc,
            "cash_flow": cf,
            "metadata": {
                "source": filepath,
                "source_format": "pdf",
                "extraction_method": "direct_pdfplumber",
                "bs_items": len(bs),
                "is_items": len(inc),
                "cf_items": len(cf),
            }
        }
        
        logger.info(f"  Total items - BS: {len(bs)}, IS: {len(inc)}, CF: {len(cf)}")
    
    return results


def map_apple_accounts(data):
    """Map Apple's US GAAP account names to standardized format."""
    
    # Apple (US GAAP) to standard mapping
    bs_mapping = {
        # Assets
        'Cash and cash equivalents': '货币资金',
        'Marketable securities': '交易性金融资产',
        'Accounts receivable, net': '应收账款',
        'Inventories': '存货',
        'Vendor non-trade receivables': '其他应收款',
        'Other current assets': '其他流动资产',
        'Total current assets': '流动资产合计',
        'Property, plant and equipment, net': '固定资产',
        'Goodwill': '商誉',
        'Intangible assets, net': '无形资产',
        'Other non-current assets': '其他非流动资产',
        'Total non-current assets': '非流动资产合计',
        'Total assets': '资产总计',
        
        # Liabilities
        'Accounts payable': '应付账款',
        'Other current liabilities': '其他流动负债',
        'Deferred revenue': '预收款项',
        'Commercial paper': '短期借款',
        'Term debt, current portion': '一年内到期的非流动负债',
        'Total current liabilities': '流动负债合计',
        'Term debt, noncurrent': '长期借款',
        'Other non-current liabilities': '其他非流动负债',
        'Total non-current liabilities': '非流动负债合计',
        'Total liabilities': '负债合计',
        
        # Equity
        'Common stock and additional paid-in capital': '实收资本',
        'Retained earnings': '未分配利润',
        'Accumulated other comprehensive income/(loss)': '其他综合收益',
        'Total shareholders\' equity': '所有者权益合计',
        'Total liabilities and shareholders\' equity': '负债和所有者权益总计',
    }
    
    is_mapping = {
        'Net sales': '营业收入',
        'Total net sales': '营业收入',
        'Cost of sales': '营业成本',
        'Total cost of sales': '营业成本',
        'Gross margin': '毛利润',
        'Total operating expenses': '营业费用',
        'Research and development': '研发费用',
        'Selling, general and administrative': '管理费用',
        'Operating income': '营业利润',
        'Other income/(expense), net': '其他收益',
        'Income before provision for income taxes': '利润总额',
        'Provision for income taxes': '所得税费用',
        'Net income': '净利润',
    }
    
    cf_mapping = {
        'Cash and cash equivalents, beginning of period': '期初现金',
        'Cash and cash equivalents, end of period': '期末现金',
        'Cash generated by operating activities': '经营活动现金流入',
        'Cash used in operating activities': '经营活动现金流出',
        'Cash generated by investing activities': '投资活动现金流入',
        'Cash used in investing activities': '投资活动现金流出',
        'Cash generated by financing activities': '筹资活动现金流入',
        'Cash used in financing activities': '筹资活动现金流出',
    }
    
    def apply_mapping(original_dict, mapping):
        mapped = {}
        for k, v in original_dict.items():
            mapped_key = mapping.get(k, k)
            mapped[mapped_key] = v
        return mapped
    
    for period in data.get("periods", []):
        if period in data.get("bs", {}):
            data["bs"][period] = apply_mapping(data["bs"][period], bs_mapping)
        if period in data.get("is", {}):
            data["is"][period] = apply_mapping(data["is"][period], is_mapping)
        if period in data.get("cf", {}):
            data["cf"][period] = apply_mapping(data["cf"][period], cf_mapping)
    
    return data


def prepare_pipeline_data(parsed_results):
    """Convert parsed results to pipeline format."""
    periods = []
    bs_data = {}
    is_data = {}
    cf_data = {}
    
    for quarter in QUARTERS:
        if quarter not in parsed_results:
            continue
        
        result = parsed_results[quarter]
        periods.append(quarter)
        
        bs_data[quarter] = result.get("balance_sheet", {})
        is_data[quarter] = result.get("income_statement", {})
        cf_data[quarter] = result.get("cash_flow", {})
    
    return {
        "periods": periods,
        "bs": bs_data,
        "is": is_data,
        "cf": cf_data,
    }


def run_analysis(data):
    """Run the financial analysis pipeline."""
    run_pipeline = safe_import('run_pipeline')
    if run_pipeline is None:
        logger.error("Cannot run pipeline - module not available")
        return []
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Apple industry benchmark (Technology/Consumer Electronics)
    industry = {
        "label": "科技/消费电子",
        "profit_margin_avg": 25.0,
        "net_margin_avg": 20.0,
        "roe_avg": 25.0,
        "current_ratio_avg": 1.5,
        "debt_ratio_avg": 55.0,
        "turnover_avg": 0.80,
    }
    
    paths = run_pipeline.run_full_pipeline(
        data=data,
        company_name="Apple Inc. (苹果公司)",
        company_short="Apple",
        year="FY2025",
        output_dir=OUTPUT_DIR,
        industry=industry,
    )
    
    return paths


def main():
    logger.info("=" * 60)
    logger.info("Apple Inc. FY2025 Financial Statement Analysis")
    logger.info("=" * 60)
    
    # Step 1: Parse all PDFs using direct extraction
    logger.info("\n--- Step 1: Parsing PDF Reports ---")
    parsed = parse_all_pdfs_direct()
    
    # Save parsed data for inspection
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parsed_output = os.path.join(OUTPUT_DIR, "parsed_data.json")
    with open(parsed_output, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Parsed data saved to: {parsed_output}")
    
    # Step 2: Prepare pipeline data
    logger.info("\n--- Step 2: Preparing Data ---")
    data = prepare_pipeline_data(parsed)
    logger.info(f"Periods: {data['periods']}")
    
    # Step 3: Map accounts to standard format
    logger.info("\n--- Step 3: Mapping Accounts ---")
    data = map_apple_accounts(data)
    
    # Save mapped data
    mapped_output = os.path.join(OUTPUT_DIR, "mapped_data.json")
    with open(mapped_output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Mapped data saved to: {mapped_output}")
    
    # Step 4: Run analysis pipeline
    logger.info("\n--- Step 4: Running Analysis Pipeline ---")
    try:
        paths = run_analysis(data)
        logger.info(f"\n--- Analysis Complete ---")
        logger.info(f"Reports generated:")
        for p in paths:
            logger.info(f"  -> {p}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract complete financial data from Apple 10-Q PDFs."""

import pdfplumber
import os
import json
import re

PDF_DIR = r"h:\DEV\MyProjects\BidGenerator\Apple_Financial_Reports\FY2026\10-Q"

def extract_all_tables(filepath):
    """Extract all tables from PDF."""
    all_data = {
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
        "metadata": {}
    }
    
    with pdfplumber.open(filepath) as pdf:
        all_tables = []
        all_text = []
        
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                all_text.append((page_num, text))
            
            tables = page.extract_tables()
            for tbl in tables:
                if tbl and len(tbl) >= 2 and max(len(r) for r in tbl) >= 2:
                    all_tables.append((page_num, tbl))
        
        all_data["metadata"]["total_pages"] = len(pdf.pages)
        all_data["metadata"]["total_tables"] = len(all_tables)
        
        # Print full text for pages 4-8 (financial statements)
        for page_num, text in all_text:
            if 4 <= page_num <= 10:
                all_data[f"page_{page_num}_text"] = text
        
        # Print all tables with content
        for page_num, tbl in all_tables:
            if 4 <= page_num <= 10:
                all_data[f"page_{page_num}_table"] = {
                    "rows": len(tbl),
                    "cols": max(len(r) for r in tbl),
                    "first_5_rows": tbl[:5]
                }
    
    return all_data

# Extract both files
for fname in ["FY2026_10-Q_Q1.pdf", "FY2026_10-Q_Q2.pdf"]:
    fpath = os.path.join(PDF_DIR, fname)
    print(f"\n{'='*80}")
    print(f"FILE: {fname}")
    print(f"{'='*80}")
    
    data = extract_all_tables(fpath)
    
    # Print pages 4-8 text
    for key in sorted(data.keys()):
        if key.startswith("page_") and key.endswith("_text"):
            print(f"\n--- {key} ---")
            print(data[key])
    
    # Print table summaries
    for key in sorted(data.keys()):
        if key.startswith("page_") and key.endswith("_table"):
            print(f"\n--- {key} ---")
            t = data[key]
            print(f"  Rows: {t['rows']}, Cols: {t['cols']}")
            for row in t['first_5_rows']:
                print(f"  {row}")

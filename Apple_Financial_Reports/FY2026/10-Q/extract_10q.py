#!/usr/bin/env python3
"""Extract text from Apple 10-Q PDFs for inspection."""

import pdfplumber
import os
import json

PDF_DIR = r"h:\DEV\MyProjects\BidGenerator\Apple_Financial_Reports\FY2026\10-Q"

def inspect_pdf(filepath, max_pages=5):
    """Extract text from first few pages of a PDF."""
    print(f"\n{'='*80}")
    print(f"FILE: {os.path.basename(filepath)}")
    print(f"{'='*80}")
    
    with pdfplumber.open(filepath) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        for i, page in enumerate(pdf.pages[:max_pages]):
            text = page.extract_text()
            if text:
                print(f"\n--- Page {i+1} ---")
                print(text[:3000])  # First 3000 chars per page
            
            tables = page.extract_tables()
            if tables:
                print(f"\n  [Page {i+1}] Tables found: {len(tables)}")
                for j, tbl in enumerate(tables):
                    print(f"  Table {j}: {len(tbl)} rows x {max(len(r) for r in tbl)} cols")
                    # Print first 3 rows
                    for row in tbl[:3]:
                        print(f"    {row}")

# Inspect both files
for fname in ["FY2026_10-Q_Q1.pdf", "FY2026_10-Q_Q2.pdf"]:
    fpath = os.path.join(PDF_DIR, fname)
    if os.path.exists(fpath):
        inspect_pdf(fpath, max_pages=8)
    else:
        print(f"NOT FOUND: {fpath}")

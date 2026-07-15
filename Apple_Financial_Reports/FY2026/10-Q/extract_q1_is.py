#!/usr/bin/env python3
"""Extract Q1 income statement fully."""

import pdfplumber

with pdfplumber.open(r"h:\DEV\MyProjects\BidGenerator\Apple_Financial_Reports\FY2026\10-Q\FY2026_10-Q_Q1.pdf") as pdf:
    # Page 4 (index 3) has income statement
    page = pdf.pages[3]
    text = page.extract_text()
    print("=== Q1 PAGE 4 (Income Statement) ===")
    print(text)
    
    # Also check page 3 (index 2) - might have partial IS
    page3 = pdf.pages[2]
    text3 = page3.extract_text()
    print("\n=== Q1 PAGE 3 ===")
    print(text3)

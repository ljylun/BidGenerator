#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Inc. Financial Reports PDF Downloader
Downloads PDF financial reports from Apple's investor relations website
for FY2022, FY2023, FY2024, FY2025, and FY2026.
"""

import os
import time
import requests
from pathlib import Path
from typing import List, Dict, Tuple

# Configuration
BASE_DIR = Path("h:/DEV/MyProjects/BidGenerator/Apple_Financial_Reports")
CIK = "0000320193"

# Request headers
HEADERS = {
    "User-Agent": "AppleFinancialReportsDownloader/1.0 (research@example.com)",
}

# Apple PDF URLs based on pattern from investor.apple.com
# Pattern: https://www.apple.com/newsroom/pdfs/FY[YY][QQ]_Consolidated_Financial_Statements.pdf
# Pattern: https://s2.q4cdn.com/470004039/files/doc_earnings/[YYYY]/[qq]/filing/[TYPE]-[QQ]-[YYYY]-as-filed.pdf

REPORTS_TO_DOWNLOAD: List[Dict] = [
    # FY2022
    {"fiscal_year": "FY2022", "quarter": "Q4", "report_type": "10-K", "filename": "FY2022_10-K.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2022/q4/filing/_10-K-Q4-2022-As-Filed.pdf"},
    {"fiscal_year": "FY2022", "quarter": "Q1", "report_type": "10-Q", "filename": "FY2022_10-Q_Q1.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2022/q1/filing/_10-Q-Q1-2022-As-Filed.pdf"},
    {"fiscal_year": "FY2022", "quarter": "Q2", "report_type": "10-Q", "filename": "FY2022_10-Q_Q2.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2022/q2/filing/_10-Q-Q2-2022-As-Filed.pdf"},
    {"fiscal_year": "FY2022", "quarter": "Q3", "report_type": "10-Q", "filename": "FY2022_10-Q_Q3.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2022/q3/filing/_10-Q-Q3-2022-As-Filed.pdf"},
    
    # FY2023
    {"fiscal_year": "FY2023", "quarter": "Q4", "report_type": "10-K", "filename": "FY2023_10-K.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2023/q4/filing/_10-K-Q4-2023-As-Filed.pdf"},
    {"fiscal_year": "FY2023", "quarter": "Q1", "report_type": "10-Q", "filename": "FY2023_10-Q_Q1.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2023/q1/filing/_10-Q-Q1-2023-As-Filed.pdf"},
    {"fiscal_year": "FY2023", "quarter": "Q2", "report_type": "10-Q", "filename": "FY2023_10-Q_Q2.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2023/q2/filing/_10-Q-Q2-2023-As-Filed.pdf"},
    {"fiscal_year": "FY2023", "quarter": "Q3", "report_type": "10-Q", "filename": "FY2023_10-Q_Q3.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2023/q3/filing/_10-Q-Q3-2023-As-Filed.pdf"},
    
    # FY2024
    {"fiscal_year": "FY2024", "quarter": "Q4", "report_type": "10-K", "filename": "FY2024_10-K.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2024/q4/filing/10-Q4-2024-As-Filed.pdf"},
    {"fiscal_year": "FY2024", "quarter": "Q1", "report_type": "10-Q", "filename": "FY2024_10-Q_Q1.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2024/q1/filing/_10-Q-Q1-2024-As-Filed.pdf"},
    {"fiscal_year": "FY2024", "quarter": "Q2", "report_type": "10-Q", "filename": "FY2024_10-Q_Q2.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_financials/2024/q2/_10-Q-Q2-2024-As-Filed.pdf"},
    {"fiscal_year": "FY2024", "quarter": "Q3", "report_type": "10-Q", "filename": "FY2024_10-Q_Q3.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2024/q3/filing/_10-Q-Q3-2024-As-Filed.pdf"},
    
    # FY2025
    {"fiscal_year": "FY2025", "quarter": "Q4", "report_type": "10-K", "filename": "FY2025_10-K.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2025/q4/filing/10K-Q4-2025-as-filed.pdf"},
    {"fiscal_year": "FY2025", "quarter": "Q1", "report_type": "10-Q", "filename": "FY2025_10-Q_Q1.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2025/q1/filing/10Q-Q1-2025-as-filed.pdf"},
    {"fiscal_year": "FY2025", "quarter": "Q2", "report_type": "10-Q", "filename": "FY2025_10-Q_Q2.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2025/q2/filing/10Q-Q2-2025-as-filed.pdf"},
    {"fiscal_year": "FY2025", "quarter": "Q3", "report_type": "10-Q", "filename": "FY2025_10-Q_Q3.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2025/q3/filing/10Q-Q3-2025-as-filed.pdf"},
    
    # FY2026 (Q1 and Q2 available)
    {"fiscal_year": "FY2026", "quarter": "Q1", "report_type": "10-Q", "filename": "FY2026_10-Q_Q1.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2026/q1/filing/10Q-Q1-2026-as-filed.pdf"},
    {"fiscal_year": "FY2026", "quarter": "Q2", "report_type": "10-Q", "filename": "FY2026_10-Q_Q2.pdf", "url": "https://s2.q4cdn.com/470004039/files/doc_earnings/2026/q2/filing/10Q-Q2-2026-as-filed.pdf"},
]

# Financial Statements PDFs (consolidated financial statements)
FINANCIAL_STATEMENTS: List[Dict] = [
    # FY2022
    {"fiscal_year": "FY2022", "quarter": "Q1", "filename": "FY2022_Q1_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2022-q1/FY22_Q1_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2022", "quarter": "Q2", "filename": "FY2022_Q2_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2022-q2/FY22_Q2_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2022", "quarter": "Q3", "filename": "FY2022_Q3_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2022-q3/FY22_Q3_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2022", "quarter": "Q4", "filename": "FY2022_Q4_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2022-q4/FY22_Q4_Consolidated_Financial_Statements.pdf"},
    
    # FY2023
    {"fiscal_year": "FY2023", "quarter": "Q1", "filename": "FY2023_Q1_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2023-q1/FY23_Q1_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2023", "quarter": "Q2", "filename": "FY2023_Q2_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2023-q2/FY23_Q2_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2023", "quarter": "Q3", "filename": "FY2023_Q3_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2023-q3/FY23_Q3_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2023", "quarter": "Q4", "filename": "FY2023_Q4_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2023-q4/FY23_Q4_Consolidated_Financial_Statements.pdf"},
    
    # FY2024
    {"fiscal_year": "FY2024", "quarter": "Q1", "filename": "FY2024_Q1_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2024-q1/FY24_Q1_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2024", "quarter": "Q2", "filename": "FY2024_Q2_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2024-q2/FY24_Q2_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2024", "quarter": "Q3", "filename": "FY2024_Q3_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2024-q3/FY24_Q3_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2024", "quarter": "Q4", "filename": "FY2024_Q4_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf"},
    
    # FY2025
    {"fiscal_year": "FY2025", "quarter": "Q1", "filename": "FY2025_Q1_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2025-q1/FY25_Q1_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2025", "quarter": "Q2", "filename": "FY2025_Q2_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2025-q2/FY25_Q2_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2025", "quarter": "Q3", "filename": "FY2025_Q3_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2025-q3/FY25_Q3_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2025", "quarter": "Q4", "filename": "FY2025_Q4_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2025-q4/FY25_Q4_Consolidated_Financial_Statements.pdf"},
    
    # FY2026 (Q1 and Q2 available)
    {"fiscal_year": "FY2026", "quarter": "Q1", "filename": "FY2026_Q1_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2026-q1/FY26_Q1_Consolidated_Financial_Statements.pdf"},
    {"fiscal_year": "FY2026", "quarter": "Q2", "filename": "FY2026_Q2_Financial_Statements.pdf", "url": "https://www.apple.com/newsroom/pdfs/fy2026q2/FY26_Q2_Consolidated_Financial_Statements.pdf"},
]


def download_file(url: str, save_path: Path, max_retries: int = 3) -> bool:
    """Download a file from URL with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=120, stream=True)
            response.raise_for_status()
            
            # Check if we got a PDF (not an error page)
            content_type = response.headers.get('content-type', '')
            if 'html' in content_type.lower() and 'pdf' not in content_type.lower():
                print(f"  Warning: Response appears to be HTML, not PDF. URL may be invalid.")
                print(f"  Content-Type: {content_type}")
                return False
            
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file is a PDF
            with open(save_path, "rb") as f:
                header = f.read(5)
                if header != b"%PDF-":
                    print(f"  Warning: Downloaded file is not a valid PDF. Header: {header}")
                    save_path.unlink()  # Delete invalid file
                    return False
            
            return True
        except requests.RequestException as e:
            print(f"  Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return False


def main():
    print("=" * 60)
    print("Apple Inc. Financial Reports PDF Downloader")
    print("=" * 60)
    print()
    
    # Combine all reports to download
    all_reports = REPORTS_TO_DOWNLOAD + FINANCIAL_STATEMENTS
    
    stats = {
        "total": len(all_reports),
        "success": 0,
        "failed": 0,
        "skipped": 0,
    }
    
    failed_downloads = []
    
    for i, report in enumerate(all_reports, 1):
        fiscal_year = report["fiscal_year"]
        filename = report["filename"]
        url = report["url"]
        
        # Determine save path based on report type
        if "10-K" in filename or "10-Q" in filename:
            report_type_dir = "10-K" if "10-K" in filename else "10-Q"
        elif "Financial_Statements" in filename:
            report_type_dir = "Financial_Statements"
        else:
            report_type_dir = "Other"
        
        save_dir = BASE_DIR / fiscal_year / report_type_dir
        save_path = save_dir / filename
        
        print(f"[{i}/{len(all_reports)}] Downloading {fiscal_year} - {filename}")
        print(f"  URL: {url}")
        print(f"  Save to: {save_path}")
        
        # Check if file already exists
        if save_path.exists():
            file_size = save_path.stat().st_size
            if file_size > 0:
                print(f"  Skipped: File already exists ({file_size} bytes)")
                stats["skipped"] += 1
                continue
        
        if download_file(url, save_path):
            file_size = save_path.stat().st_size
            print(f"  Success! ({file_size} bytes)")
            stats["success"] += 1
        else:
            print(f"  Failed to download!")
            stats["failed"] += 1
            failed_downloads.append(report)
        
        # Rate limiting
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"Total: {stats['total']}")
    print(f"Success: {stats['success']}")
    print(f"Skipped (already exists): {stats['skipped']}")
    print(f"Failed: {stats['failed']}")
    print("=" * 60)
    
    if failed_downloads:
        print("\nFailed downloads:")
        for report in failed_downloads:
            print(f"  - {report['fiscal_year']} {report['filename']}: {report['url']}")
    
    # Print files by fiscal year
    print("\nFiles by Fiscal Year:")
    for year in ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]:
        year_dir = BASE_DIR / year
        if year_dir.exists():
            file_count = sum(1 for _ in year_dir.rglob("*.pdf") if _.is_file())
            if file_count > 0:
                print(f"  {year}: {file_count} PDF files")


if __name__ == "__main__":
    main()

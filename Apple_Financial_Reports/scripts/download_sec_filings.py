#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Inc. SEC Filings Downloader
Downloads Apple Inc. financial reports from SEC EDGAR database
"""

import os
import sys
import json
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
CIK = "0000320193"  # Apple Inc. CIK number
COMPANY_NAME = "Apple Inc."
BASE_URL = "https://www.sec.gov"
DATA_URL = "https://data.sec.gov"
BASE_DIR = Path("h:/DEV/MyProjects/BidGenerator/Apple_Financial_Reports")

# Fiscal years to download
FISCAL_YEARS = ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]

# File types to download
FILE_TYPES = {
    "10-K": "10-K",
    "10-Q": "10-Q",
    "8-K": "8-K",
    "DEF 14A": "DEF 14A",
    "S-1": "S-1",
    "S-3": "S-3",
}

# Request headers (SEC requires a User-Agent with contact information)
HEADERS = {
    "User-Agent": "AppleFinancialReportsDownloader/1.0 (research@example.com)",
}

def get_company_filings() -> Optional[Dict]:
    """Get all filings for Apple Inc. from SEC EDGAR API"""
    url = f"{DATA_URL}/submissions/CIK{CIK}.json"
    print(f"Fetching company filings from: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully retrieved filings for {data.get('name', COMPANY_NAME)}")
        print(f"Total recent filings: {len(data.get('filings', {}).get('recent', {}).get('form', []))}")
        return data
    except requests.RequestException as e:
        print(f"Error fetching company filings: {e}")
        return None

def determine_fiscal_year(filing_date: str) -> Optional[str]:
    """Determine fiscal year based on filing date"""
    try:
        date = datetime.strptime(filing_date, "%Y-%m-%d")
        year = date.year
        month = date.month
        
        # Apple's fiscal year ends in September
        # If filing is in October-December, it belongs to the current calendar year's fiscal year
        # If filing is in January-September, it belongs to the previous calendar year's fiscal year
        if month >= 10:  # October, November, December
            fiscal_year = year
        else:  # January-September
            fiscal_year = year - 1
        
        # Check if it's within our target range
        if fiscal_year >= 2022 and fiscal_year <= 2026:
            return f"FY{fiscal_year}"
    except ValueError:
        pass
    return None

def get_filing_url(accession_number: str, primary_document: str) -> str:
    """Generate the download URL for a filing"""
    # Remove dashes from accession number for URL
    accession_clean = accession_number.replace("-", "")
    return f"{BASE_URL}/Archives/edgar/data/{CIK}/{accession_clean}/{primary_document}"

def download_file(url: str, save_path: Path, max_retries: int = 3) -> bool:
    """Download a file from URL with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=120, stream=True)
            response.raise_for_status()
            
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except requests.RequestException as e:
            print(f"  Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return False

def calculate_md5(file_path: Path) -> str:
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    print("=" * 60)
    print(f"Apple Inc. SEC Filings Downloader")
    print(f"CIK: {CIK}")
    print(f"Target Fiscal Years: {', '.join(FISCAL_YEARS)}")
    print("=" * 60)
    print()
    
    # Get company filings data
    data = get_company_filings()
    if not data:
        print("Failed to retrieve company filings. Exiting.")
        return
    
    # Parse recent filings
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    documents = recent.get("primaryDocument", [])
    
    print(f"\nProcessing {len(forms)} filings...")
    
    # Track downloads
    download_log = []
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
    }
    
    for i in range(len(forms)):
        form_type = forms[i]
        filing_date = dates[i]
        accession_number = accessions[i]
        primary_document = documents[i]
        
        stats["total"] += 1
        
        # Determine fiscal year
        fiscal_year = determine_fiscal_year(filing_date)
        if not fiscal_year or fiscal_year not in FISCAL_YEARS:
            stats["skipped"] += 1
            continue
        
        # Check if we want this file type
        # For 8-K, only download financial-related ones
        if form_type == "8-K":
            # Download all 8-K files as they may contain financial info
            target_dir = BASE_DIR / fiscal_year / "8-K"
        elif form_type in ["10-K", "10-Q"]:
            target_dir = BASE_DIR / fiscal_year / form_type
        elif form_type == "DEF 14A":
            target_dir = BASE_DIR / fiscal_year / "DEF-14A"
        else:
            target_dir = BASE_DIR / fiscal_year / "Other"
        
        # Generate filename with date for better organization
        date_str = filing_date.replace("-", "")
        if primary_document.endswith(".htm"):
            filename = f"{date_str}_{primary_document}"
        else:
            filename = f"{date_str}_{primary_document}"
        
        save_path = target_dir / filename
        
        # Check if file already exists
        if save_path.exists():
            print(f"  [{fiscal_year}] {form_type}: {filename} (already exists, skipping)")
            stats["skipped"] += 1
            continue
        
        # Download file
        url = get_filing_url(accession_number, primary_document)
        print(f"  Downloading [{fiscal_year}] {form_type}: {filename}")
        print(f"    URL: {url}")
        
        if download_file(url, save_path):
            print(f"    Success! Saved to: {save_path}")
            stats["success"] += 1
            
            # Log download
            download_log.append({
                "filename": filename,
                "form_type": form_type,
                "fiscal_year": fiscal_year,
                "filing_date": filing_date,
                "accession_number": accession_number,
                "url": url,
                "save_path": str(save_path.relative_to(BASE_DIR)),
                "size": save_path.stat().st_size,
            })
        else:
            print(f"    Failed to download after retries")
            stats["failed"] += 1
        
        # Rate limiting - SEC allows up to 10 requests per second
        time.sleep(0.15)
    
    # Print summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"Total filings processed: {stats['total']}")
    print(f"Successfully downloaded: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped (out of range/exists): {stats['skipped']}")
    print("=" * 60)
    
    # Save download log
    log_path = BASE_DIR / "scripts" / "download_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(download_log, f, indent=2, ensure_ascii=False)
    print(f"\nDownload log saved to: {log_path}")
    
    # Print files by fiscal year
    print("\nFiles by Fiscal Year:")
    for year in FISCAL_YEARS:
        year_dir = BASE_DIR / year
        if year_dir.exists():
            file_count = sum(1 for _ in year_dir.rglob("*") if _.is_file())
            print(f"  {year}: {file_count} files")

if __name__ == "__main__":
    main()

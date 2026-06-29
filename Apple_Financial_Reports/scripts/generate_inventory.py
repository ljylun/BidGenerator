#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Inc. SEC Filings Inventory Generator
Generates a comprehensive CSV inventory of all downloaded SEC filings
with file metadata, checksums, and source URLs.
"""

import os
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
BASE_DIR = Path("h:/DEV/MyProjects/BidGenerator/Apple_Financial_Reports")
OUTPUT_FILE = BASE_DIR / "file_inventory.csv"
DOWNLOAD_LOG = BASE_DIR / "scripts" / "download_log.json"

# Fiscal years to include
FISCAL_YEARS = ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]

# File type classification
FILE_TYPE_DIRS = {
    "10-K": "10-K",
    "10-Q": "10-Q",
    "8-K": "8-K",
    "DEF-14A": "DEF-14A",
    "Other": "Other",
}


def calculate_md5(file_path: Path) -> str:
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def extract_date_from_filename(filename: str) -> Optional[str]:
    """Extract date from filename in format YYYYMMDD"""
    import re
    match = re.match(r"(\d{8})_", filename)
    if match:
        date_str = match.group(1)
        try:
            date = datetime.strptime(date_str, "%Y%m%d")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def determine_file_type(filename: str, directory: str) -> str:
    """Determine the file type based on filename and directory"""
    # First check directory
    if directory in FILE_TYPE_DIRS:
        return FILE_TYPE_DIRS[directory]
    
    # Then check filename patterns
    fname_upper = filename.upper()
    if "10-K" in fname_upper:
        return "10-K"
    elif "10-Q" in fname_upper:
        return "10-Q"
    elif "8-K" in fname_upper:
        return "8-K"
    elif "DEF" in fname_upper and "14A" in fname_upper:
        return "DEF-14A"
    
    return "Other"


def get_download_url(filename: str, fiscal_year: str) -> str:
    """Try to reconstruct the download URL from the filename"""
    # This is an approximation - actual URLs require accession numbers
    date_str = extract_date_from_filename(filename)
    if date_str:
        date_formatted = date_str.replace("-", "")
        return f"https://www.sec.gov/Archives/edgar/data/320193/{date_formatted}/{filename}"
    return "N/A"


def load_download_log() -> Dict[str, Dict]:
    """Load the download log to get original URLs"""
    url_map = {}
    if DOWNLOAD_LOG.exists():
        try:
            with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
                log_data = json.load(f)
                for entry in log_data:
                    key = entry.get("filename", "")
                    url_map[key] = entry
        except Exception as e:
            print(f"Warning: Could not load download log: {e}")
    return url_map


def generate_inventory():
    """Generate the complete file inventory"""
    print("=" * 60)
    print("Apple Inc. SEC Filings Inventory Generator")
    print("=" * 60)
    
    # Load download log for URL mapping
    url_map = load_download_log()
    
    # Prepare CSV data
    inventory = []
    
    # Scan all fiscal year directories
    for fiscal_year in FISCAL_YEARS:
        year_dir = BASE_DIR / fiscal_year
        if not year_dir.exists():
            print(f"Directory not found: {fiscal_year}, skipping...")
            continue
        
        print(f"\nScanning {fiscal_year}...")
        
        # Scan subdirectories
        for subdir in FILE_TYPE_DIRS.keys():
            subdir_path = year_dir / subdir
            if not subdir_path.exists():
                continue
            
            # Process all files in subdirectory
            for item in subdir_path.iterdir():
                if item.is_file():
                    filename = item.name
                    file_path = item
                    
                    # Get file metadata
                    file_size = file_path.stat().st_size
                    file_extension = file_path.suffix.lower()
                    
                    # Extract date from filename
                    filing_date = extract_date_from_filename(filename)
                    
                    # Determine file type
                    file_type = determine_file_type(filename, subdir)
                    
                    # Get download URL from log or reconstruct
                    log_entry = url_map.get(filename, {})
                    download_url = log_entry.get("url", get_download_url(filename, fiscal_year))
                    
                    # Calculate checksums
                    print(f"  Calculating checksums for: {filename}...")
                    md5_hash = calculate_md5(file_path)
                    sha256_hash = calculate_sha256(file_path)
                    
                    # Build inventory entry
                    entry = {
                        "filename": filename,
                        "file_type": file_type,
                        "fiscal_year": fiscal_year,
                        "filing_date": filing_date or "N/A",
                        "file_size": file_size,
                        "file_size_human": format_file_size(file_size),
                        "file_extension": file_extension,
                        "download_url": download_url,
                        "local_path": str(file_path.relative_to(BASE_DIR)),
                        "md5_hash": md5_hash,
                        "sha256_hash": sha256_hash,
                        "last_modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    
                    inventory.append(entry)
    
    # Sort inventory by fiscal year, then file type, then date
    type_order = {"10-K": 0, "10-Q": 1, "8-K": 2, "DEF-14A": 3, "Other": 4}
    inventory.sort(key=lambda x: (
        FISCAL_YEARS.index(x["fiscal_year"]) if x["fiscal_year"] in FISCAL_YEARS else 99,
        type_order.get(x["file_type"], 99),
        x["filing_date"] or "",
    ))
    
    # Write CSV
    print(f"\nWriting inventory to: {OUTPUT_FILE}")
    
    fieldnames = [
        "filename",
        "file_type",
        "fiscal_year",
        "filing_date",
        "file_size",
        "file_size_human",
        "file_extension",
        "download_url",
        "local_path",
        "md5_hash",
        "sha256_hash",
        "last_modified",
    ]
    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)
    
    # Print summary
    print("\n" + "=" * 60)
    print("INVENTORY SUMMARY")
    print("=" * 60)
    print(f"Total files: {len(inventory)}")
    
    # Count by fiscal year
    print("\nFiles by fiscal year:")
    for year in FISCAL_YEARS:
        count = sum(1 for item in inventory if item["fiscal_year"] == year)
        if count > 0:
            print(f"  {year}: {count} files")
    
    # Count by file type
    print("\nFiles by type:")
    for file_type in ["10-K", "10-Q", "8-K", "DEF-14A", "Other"]:
        count = sum(1 for item in inventory if item["file_type"] == file_type)
        if count > 0:
            print(f"  {file_type}: {count} files")
    
    # Total size
    total_size = sum(item["file_size"] for item in inventory)
    print(f"\nTotal size: {format_file_size(total_size)}")
    print(f"\nInventory saved to: {OUTPUT_FILE}")
    print("=" * 60)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


if __name__ == "__main__":
    generate_inventory()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Inc. SEC Filings Organizer
Organizes downloaded SEC filings into a standardized directory structure
with consistent naming conventions.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Configuration
BASE_DIR = Path("h:/DEV/MyProjects/BidGenerator/Apple_Financial_Reports")
FISCAL_YEARS = ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]

# File type mappings
FILE_TYPE_DIRS = {
    "10-K": "10-K",
    "10-Q": "10-Q",
    "8-K": "8-K",
    "DEF 14A": "DEF-14A",
    "DEF-14A": "DEF-14A",
}


def extract_date_from_filename(filename: str) -> Optional[str]:
    """Extract date from filename in format YYYYMMDD"""
    match = re.match(r"(\d{8})_", filename)
    if match:
        date_str = match.group(1)
        try:
            date = datetime.strptime(date_str, "%Y%m%d")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def determine_fiscal_year(filing_date_str: str) -> Optional[str]:
    """Determine fiscal year from filing date"""
    try:
        if isinstance(filing_date_str, str):
            date = datetime.strptime(filing_date_str, "%Y-%m-%d")
        else:
            return None
        
        year = date.year
        month = date.month
        
        # Apple's fiscal year ends in September
        if month >= 10:  # October, November, December
            fiscal_year = year
        else:  # January-September
            fiscal_year = year - 1
        
        if fiscal_year >= 2022 and fiscal_year <= 2026:
            return f"FY{fiscal_year}"
    except (ValueError, AttributeError):
        pass
    return None


def classify_file(filename: str, form_type: str = None) -> Tuple[str, str]:
    """
    Classify file and return (new_filename, target_directory)
    Returns: (new_filename, target_dir_relative_to_fiscal_year)
    """
    date_str = extract_date_from_filename(filename)
    file_date = date_str if date_str else "unknown-date"
    
    # Get file extension
    ext = Path(filename).suffix
    
    # Handle subdirectory files (like xslF345X03/)
    if "/" in filename:
        # These are supporting files, keep them in Other
        return filename, "Other"
    
    # Classify by form type or filename pattern
    if form_type == "10-K" or "10-K" in filename.upper():
        new_name = f"{file_date}_10-K{ext}" if date_str else filename
        return new_name, "10-K"
    
    elif form_type == "10-Q" or "10-Q" in filename.upper():
        # Try to determine quarter from date
        quarter = determine_quarter_from_date(date_str)
        new_name = f"{file_date}_10-Q_Q{quarter}{ext}" if quarter and date_str else f"{file_date}_10-Q{ext}" if date_str else filename
        return new_name, "10-Q"
    
    elif form_type == "8-K":
        # Check for special 8-K types
        if "ef200" in filename.lower():
            # These are exhibit filings
            return filename, "8-K"
        new_name = f"{file_date}_8-K{ext}" if date_str else filename
        return new_name, "8-K"
    
    elif form_type and "DEF 14A" in form_type.upper():
        new_name = f"{file_date}_DEF-14A{ext}" if date_str else filename
        return new_name, "DEF-14A"
    
    elif "def14a" in filename.lower() or "defa14a" in filename.lower():
        new_name = f"{file_date}_DEF-14A{ext}" if date_str else filename
        return new_name, "DEF-14A"
    
    elif filename.endswith((".htm", ".xml", ".txt", ".pdf")):
        # For other file types, classify by extension
        if filename.startswith("20") and len(filename) > 8:
            # Already has date prefix, keep it
            return filename, "Other"
    
    return filename, "Other"


def determine_quarter_from_date(date_str: str) -> Optional[int]:
    """Determine fiscal quarter from date (Apple's fiscal year starts in October)"""
    if not date_str:
        return None
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        month = date.month
        
        # Apple's fiscal quarters:
        # Q1: Oct-Dec (10-12)
        # Q2: Jan-Mar (1-3)
        # Q3: Apr-Jun (4-6)
        # Q4: Jul-Sep (7-9)
        if month >= 10:
            return 1
        elif month <= 3:
            return 2
        elif month <= 6:
            return 3
        else:
            return 4
    except ValueError:
        return None


def clean_filename(filename: str) -> str:
    """Remove or replace characters that might cause issues"""
    # Keep the date prefix and meaningful part
    return filename.replace("/", "_").replace("\\", "_")


def organize_files():
    """Organize all files in the Apple_Financial_Reports directory"""
    print("=" * 60)
    print("Apple Inc. SEC Filings Organizer")
    print("=" * 60)
    
    if not BASE_DIR.exists():
        print(f"Error: Directory {BASE_DIR} does not exist")
        return
    
    # Track operations
    stats = {
        "files_moved": 0,
        "files_skipped": 0,
        "errors": 0,
        "by_type": {},
    }
    
    # Ensure fiscal year directories exist
    for year in FISCAL_YEARS:
        year_dir = BASE_DIR / year
        if not year_dir.exists():
            year_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure subdirectories exist
        for subdir in ["10-K", "10-Q", "8-K", "DEF-14A", "Other"]:
            subdir_path = year_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True, exist_ok=True)
    
    # Walk through all files
    for year in FISCAL_YEARS:
        year_dir = BASE_DIR / year
        if not year_dir.exists():
            continue
        
        print(f"\nProcessing {year}...")
        
        # Process files in subdirectories
        for subdir in ["10-K", "10-Q", "8-K", "DEF-14A", "Other"]:
            subdir_path = year_dir / subdir
            if not subdir_path.exists():
                continue
            
            for item in subdir_path.iterdir():
                if item.is_file():
                    filename = item.name
                    
                    # Classify the file
                    form_type = get_form_type_from_dirname(subdir)
                    new_name, target_type = classify_file(filename, form_type)
                    
                    # Determine target path
                    target_dir = year_dir / target_type
                    target_path = target_dir / clean_filename(new_name)
                    
                    # Check if file is already in correct location
                    if item.parent == target_dir and filename == new_name:
                        stats["files_skipped"] += 1
                        continue
                    
                    # Handle filename collisions
                    if target_path.exists():
                        # Add a suffix to avoid overwriting
                        base = target_path.stem
                        suffix = target_path.suffix
                        counter = 1
                        while target_path.exists():
                            target_path = target_dir / f"{base}_{counter}{suffix}"
                            counter += 1
                    
                    try:
                        # Move or rename the file
                        shutil.move(str(item), str(target_path))
                        stats["files_moved"] += 1
                        
                        # Track by type
                        stats["by_type"][target_type] = stats["by_type"].get(target_type, 0) + 1
                        
                        print(f"  Moved: {filename} -> {target_type}/{target_path.name}")
                    except Exception as e:
                        stats["errors"] += 1
                        print(f"  Error moving {filename}: {e}")
                
                elif item.is_dir():
                    # Handle nested directories (like xslF345X03/)
                    # Move contents to Other directory
                    other_dir = year_dir / "Other"
                    for sub_item in item.iterdir():
                        if sub_item.is_file():
                            target_path = other_dir / clean_filename(sub_item.name)
                            
                            if target_path.exists():
                                # Add suffix for collision
                                base = target_path.stem
                                suffix = target_path.suffix
                                counter = 1
                                while target_path.exists():
                                    target_path = other_dir / f"{base}_{counter}{suffix}"
                                    counter += 1
                            
                            try:
                                shutil.move(str(sub_item), str(target_path))
                                stats["files_moved"] += 1
                            except Exception as e:
                                stats["errors"] += 1
                                print(f"  Error moving sub_item: {e}")
                    
                    # Remove empty directory
                    try:
                        if not list(item.iterdir()):
                            item.rmdir()
                    except Exception:
                        pass
    
    # Print summary
    print("\n" + "=" * 60)
    print("ORGANIZATION SUMMARY")
    print("=" * 60)
    print(f"Files moved: {stats['files_moved']}")
    print(f"Files skipped (already organized): {stats['files_skipped']}")
    print(f"Errors: {stats['errors']}")
    print("\nFiles by type:")
    for file_type, count in sorted(stats["by_type"].items()):
        print(f"  {file_type}: {count}")
    print("=" * 60)


def get_form_type_from_dirname(dirname: str) -> Optional[str]:
    """Map directory name to SEC form type"""
    mapping = {
        "10-K": "10-K",
        "10-Q": "10-Q",
        "8-K": "8-K",
        "DEF-14A": "DEF 14A",
    }
    return mapping.get(dirname)


if __name__ == "__main__":
    organize_files()

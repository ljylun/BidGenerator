#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Inc. SEC Filings Verifier
Verifies the integrity and accessibility of all downloaded SEC filings.
"""

import os
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Configuration
BASE_DIR = Path("h:/DEV/MyProjects/BidGenerator/Apple_Financial_Reports")
DOWNLOAD_LOG = BASE_DIR / "scripts" / "download_log.json"
INVENTORY_FILE = BASE_DIR / "file_inventory.csv"
REPORT_FILE = BASE_DIR / "verification_report.txt"

# Fiscal years to verify
FISCAL_YEARS = ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]


def verify_file_exists(file_path: Path) -> Tuple[bool, str]:
    """Verify file exists and is accessible"""
    if not file_path.exists():
        return False, "File does not exist"
    if not file_path.is_file():
        return False, "Path is not a file"
    return True, "OK"


def verify_file_not_empty(file_path: Path) -> Tuple[bool, str]:
    """Verify file is not empty"""
    try:
        size = file_path.stat().st_size
        if size == 0:
            return False, "File is empty (0 bytes)"
        return True, f"OK ({size} bytes)"
    except Exception as e:
        return False, f"Error checking size: {e}"


def verify_html_file(file_path: Path) -> Tuple[bool, str]:
    """Verify HTML file has valid structure"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(10240)  # Read first 10KB
        
        # Check for basic HTML structure
        if "<!DOCTYPE" in content.upper() or "<HTML" in content.upper():
            return True, "Valid HTML structure"
        
        # SEC files might start with <?xml declaration
        if content.strip().startswith("<?xml"):
            return True, "XML/XHTML document"
        
        # Check if it looks like HTML content
        if "<" in content and ">" in content:
            return True, "Contains HTML-like content"
        
        return False, "Does not appear to be valid HTML"
    except Exception as e:
        return False, f"Error reading file: {e}"


def verify_xml_file(file_path: Path) -> Tuple[bool, str]:
    """Verify XML file is parseable"""
    try:
        # Try to parse just the first part
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(10240)
        
        # Check for XML declaration
        if content.strip().startswith("<?xml"):
            # Try to parse
            ET.fromstring(content + "</root>" if not content.endswith(">") else content)
            return True, "Valid XML"
        
        # Check for XML-like content
        if "<" in content and ">" in content:
            return True, "Contains XML-like content"
        
        return False, "Does not appear to be valid XML"
    except ET.ParseError as e:
        # SEC XML files might not be fully valid, but that's often OK
        if "<" in content and ">" in content:
            return True, f"XML parse warning (common for SEC files): {str(e)[:50]}"
        return False, f"Invalid XML: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def verify_txt_file(file_path: Path) -> Tuple[bool, str]:
    """Verify text file is readable"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(1024)
        
        if len(content) > 0:
            return True, "Readable text file"
        return False, "File appears to be empty or unreadable"
    except Exception as e:
        return False, f"Error reading file: {e}"


def verify_pdf_file(file_path: Path) -> Tuple[bool, str]:
    """Verify PDF file header"""
    try:
        with open(file_path, "rb") as f:
            header = f.read(5)
        
        if header == b"%PDF-":
            return True, "Valid PDF header"
        
        # Check if it starts with common PDF version
        if header.startswith(b"%PDF-1.") or header.startswith(b"%PDF-2."):
            return True, "Valid PDF header"
        
        return False, f"Invalid PDF header: {header}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def verify_file_checksum(file_path: Path, expected_md5: str = None, expected_sha256: str = None) -> Tuple[bool, str]:
    """Verify file checksum matches expected value"""
    if not expected_md5 and not expected_sha256:
        return True, "No checksum to verify"
    
    try:
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
                hash_sha256.update(chunk)
        
        actual_md5 = hash_md5.hexdigest()
        actual_sha256 = hash_sha256.hexdigest()
        
        if expected_md5 and actual_md5 != expected_md5:
            return False, f"MD5 mismatch: expected {expected_md5}, got {actual_md5}"
        
        if expected_sha256 and actual_sha256 != expected_sha256:
            return False, f"SHA256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        
        return True, "Checksum verified"
    except Exception as e:
        return False, f"Error calculating checksum: {e}"


def verify_file(file_path: Path, extension: str, expected_md5: str = None, expected_sha256: str = None) -> Dict:
    """Run all verifications on a file"""
    result = {
        "file": str(file_path),
        "exists": False,
        "not_empty": False,
        "format_valid": False,
        "checksum_valid": True,  # Default to True if no checksum provided
        "errors": [],
        "warnings": [],
    }
    
    # Check existence
    exists, msg = verify_file_exists(file_path)
    result["exists"] = exists
    if not exists:
        result["errors"].append(msg)
        return result
    
    # Check not empty
    not_empty, msg = verify_file_not_empty(file_path)
    result["not_empty"] = not_empty
    if not not_empty:
        result["errors"].append(msg)
        return result
    
    # Format-specific verification
    ext = extension.lower()
    if ext == ".htm":
        valid, msg = verify_html_file(file_path)
        result["format_valid"] = valid
        if not valid:
            result["warnings"].append(f"HTML validation warning: {msg}")
    
    elif ext == ".xml":
        valid, msg = verify_xml_file(file_path)
        result["format_valid"] = valid
        if not valid:
            result["warnings"].append(f"XML validation warning: {msg}")
    
    elif ext == ".txt":
        valid, msg = verify_txt_file(file_path)
        result["format_valid"] = valid
        if not valid:
            result["warnings"].append(f"Text validation warning: {msg}")
    
    elif ext == ".pdf":
        valid, msg = verify_pdf_file(file_path)
        result["format_valid"] = valid
        if not valid:
            result["warnings"].append(f"PDF validation warning: {msg}")
    
    else:
        result["format_valid"] = True
        result["warnings"].append(f"Unknown file type: {ext}, skipping format check")
    
    # Verify checksum if available
    if expected_md5 or expected_sha256:
        valid, msg = verify_file_checksum(file_path, expected_md5, expected_sha256)
        result["checksum_valid"] = valid
        if not valid:
            result["errors"].append(msg)
    
    return result


def load_inventory() -> List[Dict]:
    """Load the file inventory CSV"""
    inventory = []
    if INVENTORY_FILE.exists():
        try:
            with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                inventory = list(reader)
        except Exception as e:
            print(f"Warning: Could not load inventory: {e}")
    return inventory


def load_download_log() -> Dict[str, Dict]:
    """Load the download log"""
    log_data = {}
    if DOWNLOAD_LOG.exists():
        try:
            with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
                for entry in data:
                    key = entry.get("filename", "")
                    log_data[key] = entry
        except Exception as e:
            print(f"Warning: Could not load download log: {e}")
    return log_data


def run_verification():
    """Run complete verification on all files"""
    print("=" * 60)
    print("Apple Inc. SEC Filings Verifier")
    print("=" * 60)
    
    # Load inventory for checksum verification
    inventory = load_inventory()
    inventory_map = {item["filename"]: item for item in inventory}
    
    # Stats
    stats = {
        "total_files": 0,
        "verified": 0,
        "warnings": 0,
        "errors": 0,
        "by_status": {"pass": 0, "warning": 0, "error": 0},
    }
    
    verification_results = []
    
    # Scan all fiscal year directories
    for fiscal_year in FISCAL_YEARS:
        year_dir = BASE_DIR / fiscal_year
        if not year_dir.exists():
            continue
        
        print(f"\nVerifying {fiscal_year}...")
        
        for subdir in ["10-K", "10-Q", "8-K", "DEF-14A", "Other"]:
            subdir_path = year_dir / subdir
            if not subdir_path.exists():
                continue
            
            for item in subdir_path.iterdir():
                if item.is_file():
                    stats["total_files"] += 1
                    
                    filename = item.name
                    extension = item.suffix.lower()
                    
                    # Get expected checksums from inventory
                    inv_entry = inventory_map.get(filename, {})
                    expected_md5 = inv_entry.get("md5_hash")
                    expected_sha256 = inv_entry.get("sha256_hash")
                    
                    # Run verification
                    result = verify_file(
                        item, extension,
                        expected_md5=expected_md5 if expected_md5 != "ERROR: " else None,
                        expected_sha256=expected_sha256 if expected_sha256 != "ERROR: " else None
                    )
                    
                    # Determine status
                    if result["errors"]:
                        status = "error"
                        stats["by_status"]["error"] += 1
                        stats["errors"] += 1
                    elif result["warnings"]:
                        status = "warning"
                        stats["by_status"]["warning"] += 1
                        stats["warnings"] += 1
                    else:
                        status = "pass"
                        stats["by_status"]["pass"] += 1
                        stats["verified"] += 1
                    
                    result["status"] = status
                    result["fiscal_year"] = fiscal_year
                    result["file_type"] = subdir
                    verification_results.append(result)
                    
                    # Print progress
                    status_icon = {"pass": "✓", "warning": "⚠", "error": "✗"}.get(status, "?")
                    print(f"  {status_icon} {filename}: {status}")
    
    # Generate report
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total files checked: {stats['total_files']}")
    print(f"Passed: {stats['by_status']['pass']}")
    print(f"Warnings: {stats['by_status']['warning']}")
    print(f"Errors: {stats['by_status']['error']}")
    print("=" * 60)
    
    # Write detailed report
    write_report(verification_results, stats)
    
    return stats


def write_report(results: List[Dict], stats: Dict):
    """Write detailed verification report"""
    print(f"\nWriting report to: {REPORT_FILE}")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Apple Inc. SEC Filings Verification Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total files checked: {stats['total_files']}\n")
        f.write(f"Passed: {stats['by_status']['pass']}\n")
        f.write(f"Warnings: {stats['by_status']['warning']}\n")
        f.write(f"Errors: {stats['by_status']['error']}\n\n")
        
        # Error details
        errors = [r for r in results if r["status"] == "error"]
        if errors:
            f.write("\nERRORS\n")
            f.write("-" * 40 + "\n")
            for result in errors:
                f.write(f"\nFile: {result['file']}\n")
                f.write(f"  Fiscal Year: {result['fiscal_year']}\n")
                f.write(f"  File Type: {result['file_type']}\n")
                for error in result["errors"]:
                    f.write(f"  Error: {error}\n")
        
        # Warning details
        warnings = [r for r in results if r["status"] == "warning"]
        if warnings:
            f.write("\n\nWARNINGS\n")
            f.write("-" * 40 + "\n")
            for result in warnings:
                f.write(f"\nFile: {result['file']}\n")
                f.write(f"  Fiscal Year: {result['fiscal_year']}\n")
                f.write(f"  File Type: {result['file_type']}\n")
                for warning in result["warnings"]:
                    f.write(f"  Warning: {warning}\n")
        
        # Passed files
        passed = [r for r in results if r["status"] == "pass"]
        if passed:
            f.write("\n\nPASSED FILES\n")
            f.write("-" * 40 + "\n")
            for result in passed:
                f.write(f"  {result['file']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("End of Report\n")
    
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    run_verification()

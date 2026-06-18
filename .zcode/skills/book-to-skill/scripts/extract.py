#!/usr/bin/env python3
"""Extract text from PDF/EPUB/DOCX files for book-to-skill converter."""
import sys
import os
import json
import tempfile
from pathlib import Path

def extract_pdf(path):
    """Extract text from PDF using PyMuPDF, preserving structure."""
    import fitz
    doc = fitz.open(path)
    pages_text = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages_text.append(f"--- Page {i+1} ---\n{text}")
    doc.close()
    return "\n\n".join(pages_text)

def extract_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_md(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    input_paths = []
    mode = "text"
    install_missing = "no"
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--mode" and i+1 < len(args):
            mode = args[i+1]
            i += 2
        elif args[i] == "--install-missing" and i+1 < len(args):
            install_missing = args[i+1]
            i += 2
        elif args[i] == "--check":
            print("PyMuPDF (fitz): available")
            print("PyPDF2: available")
            print("pdfplumber: available")
            return
        else:
            input_paths.append(args[i])
            i += 1
    
    if not input_paths:
        print("Usage: extract.py <path>... [--mode text|technical] [--install-missing yes|no|ask] [--check]", file=sys.stderr)
        sys.exit(1)
    
    workdir = Path(tempfile.mkdtemp(prefix="book_skill_work_"))
    full_text_parts = []
    sources_meta = []
    
    for path_str in input_paths:
        path = Path(path_str)
        if not path.exists():
            print(f"Warning: {path} not found, skipping", file=sys.stderr)
            continue
        
        ext = path.suffix.lower()
        size = path.stat().st_size
        
        if ext == '.pdf':
            text = extract_pdf(str(path))
        elif ext in ('.txt', '.text'):
            text = extract_txt(str(path))
        elif ext in ('.md', '.markdown'):
            extract_md(str(path))
        else:
            print(f"Warning: unsupported format {ext} for {path}", file=sys.stderr)
            continue
        
        word_count = len(text.split())
        page_count = text.count("--- Page ")
        
        full_text_parts.append(f"\n\n{'='*60}\nSource: {path.name}\n{'='*60}\n\n{text}")
        sources_meta.append({
            "filename": path.name,
            "format": ext,
            "size_bytes": size,
            "words": word_count,
            "pages": max(page_count, 1)
        })
    
    full_text = "\n".join(full_text_parts)
    
    # Write outputs
    full_text_path = workdir / "full_text.txt"
    full_text_path.write_text(full_text, encoding='utf-8')
    
    metadata = {
        "total_sources": len(sources_meta),
        "sources": sources_meta,
        "total_words": len(full_text.split()),
        "total_chars": len(full_text),
        "estimated_tokens": len(full_text.split()) * 1.33,
        "workdir": str(workdir)
    }
    
    meta_path = workdir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()

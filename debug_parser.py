#!/usr/bin/env python3
"""Debug the PDF parser to see what's happening."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import io
import re
import pdfplumber

RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"

def test_parser():
    pdf_path = RAW_DIR / "bns.pdf"
    print(f"📌 Testing parser on: {pdf_path}")
    print(f"   File exists: {pdf_path.exists()}")
    print(f"   File size: {pdf_path.stat().st_size / (1024*1024):.1f} MB")
    
    pdf_bytes = pdf_path.read_bytes()
    print(f"✓ Read {len(pdf_bytes) / (1024*1024):.1f} MB from disk")
    
    print("\n📖 Opening PDF with pdfplumber...")
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        print(f"✓ PDF has {len(pdf.pages)} pages")
        
        # Extract text from first 10 pages to debug
        print("\n📝 Extracting text from pages 1-10...")
        for page_idx in range(min(10, len(pdf.pages))):
            page = pdf.pages[page_idx]
            text = page.extract_text()
            if text:
                print(f"  Page {page_idx+1}: {len(text)} chars")
                # Show first 200 chars
                preview = text[:200].replace("\n", " ")
                print(f"    Preview: {preview}...")
            else:
                print(f"  Page {page_idx+1}: NO TEXT extracted")
        
        # Full extraction
        print("\n⏳ Extracting ALL pages (this may take time)...")
        full_text = ""
        for i, page in enumerate(pdf.pages):
            if i % 100 == 0:
                print(f"  ...processing page {i}/{len(pdf.pages)}")
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        print(f"✓ Total extracted text: {len(full_text)} chars")
        
        # Try regex on full text
        print("\n🔍 Running regex pattern...")
        section_pattern = re.compile(
            r"(?:^|\n)(\d{1,3}[A-Z]?)\.\s+([A-Z\u0900-\u097F][^\n]{3,120})\n",
            re.MULTILINE,
        )
        matches = list(section_pattern.finditer(full_text))
        print(f"✓ Found {len(matches)} section headings (strict pattern)")
        
        if not matches:
            print("\n🔄 Trying loose fallback pattern...")
            alt_pattern = re.compile(r"(?:^|\n)(\d{1,3}[A-Z]?)\.\s+([^\n]{1,120})\n", re.MULTILINE)
            matches = list(alt_pattern.finditer(full_text))
            print(f"✓ Found {len(matches)} section headings (loose pattern)")
        
        # Show first few matches
        if matches:
            print(f"\n✓ First 5 matches:")
            for i, match in enumerate(matches[:5]):
                sec_num = match.group(1)
                sec_title = match.group(2)
                print(f"  {i+1}. Section {sec_num}: {sec_title[:80]}")

if __name__ == "__main__":
    test_parser()

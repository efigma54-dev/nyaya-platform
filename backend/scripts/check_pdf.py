
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
pdf_path = BASE_DIR / "data" / "raw" / "bns" / "bns.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"PDF has {len(pdf.pages)} pages")
    print("\n--- Page 149 (150th page):")
    print(pdf.pages[149].extract_text())
    print("\n--- Page 150:")
    print(pdf.pages[150].extract_text())
    print("\n--- Page 151:")
    print(pdf.pages[151].extract_text())

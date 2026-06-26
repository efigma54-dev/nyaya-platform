
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

pdf_files = [
    ("BNS", BASE_DIR / "data" / "raw" / "bns" / "bns.pdf"),
    ("BNSS", BASE_DIR / "data" / "raw" / "bnss" / "bnss.pdf"),
    ("BSA", BASE_DIR / "data" / "raw" / "bsa" / "bsa.pdf"),
]

for name, pdf_path in pdf_files:
    print(f"\n--- {name} ---")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"  Pages: {len(pdf.pages)}")
        text = ""
        for i in range(min(5, len(pdf.pages))):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                text += page_text[:500] + "\n"
        print(text[:2000])


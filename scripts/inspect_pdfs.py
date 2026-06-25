from pathlib import Path
import re
from PyPDF2 import PdfReader

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PDF_FILES = ["bns.pdf", "bnss.pdf", "bsa.pdf"]

for name in PDF_FILES:
    path = RAW_DIR / name
    print("FILE:", name)
    if not path.exists():
        print("  MISSING")
        continue
    reader = PdfReader(path)
    print("  pages", len(reader.pages))
    for idx in range(min(3, len(reader.pages))):
        page = reader.pages[idx]
        text = page.extract_text() or ""
        print(f"  --- page {idx+1} sample ---")
        print(text[:1200].replace("\n", "\\n"))
        if idx == 0:
            print("  ### heading regex sample ###")
            for m in re.finditer(r'([0-9]{1,3}[A-Z]?\\.)\\s*([A-Z][^\\n]{0,120})', text):
                print("   H:", m.group(1), m.group(2)[:80])
                if m.start() > 400:
                    break
    print()

import pdfplumber
from pathlib import Path

pdf_path = Path("data") / "raw" / "bns" / "bns.pdf"
print("PDF path:", pdf_path)
print("Exists:", pdf_path.exists())
print("Size:", pdf_path.stat().st_size, "bytes")

print("Trying to open PDF...")
pdf = pdfplumber.open(pdf_path)
print("Opened! Pages:", len(pdf.pages))
pdf.close()
print("Done!")


import pdfplumber
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedSection:
    section_number: str
    section_title: Optional[str]
    bare_text: str
    plain_language: Optional[str] = None
    is_bailable: Optional[bool] = None
    is_cognizable: Optional[bool] = None
    is_compoundable: Optional[bool] = None
    punishment_summary: Optional[str] = None
    min_punishment: Optional[str] = None
    max_punishment: Optional[str] = None
    fine_amount: Optional[str] = None
    relevant_court: Optional[str] = None
    limitation_period: Optional[str] = None
    effective_date: Optional[str] = None
    language: str = "en"
    state: Optional[str] = None
    hash: Optional[str] = None


@dataclass
class ParsedAct:
    short_title: str
    full_title: str
    year: Optional[int]
    act_type: str
    category: str
    sections: List[ParsedSection]
    source_url: Optional[str] = None
    effective_date: Optional[str] = None
    language: str = "en"
    state: Optional[str] = None


class PDFLegalParser:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.text = ""
        self.pages = []

    def extract_text(self, start_page=0, end_page=None) -> str:
        """Extract raw text from PDF using pdfplumber with OCR fallback."""
        print(f"  Opening PDF file: {self.pdf_path}")
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                end_page_idx = end_page if end_page is not None else total_pages
                print(f"  PDF has {total_pages} pages, processing {start_page+1}-{end_page_idx}")
                self.pages = []
                for i in range(start_page, min(end_page_idx, total_pages)):
                    page = pdf.pages[i]
                    if (i + 1) % 50 == 0 or i == start_page:
                        print(f"    Processing page {i+1}/{total_pages}...")
                    page_text = page.extract_text() or ""
                    self.pages.append(page_text)
                self.text = "\n".join(self.pages)
                print(f"  Extracted {len(self.text)} characters total")
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
        return self.text

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()

    def _compute_section_hash(self, act_short_title: str, section_number: str, text: str) -> str:
        cleaned = re.sub(r'\s+', '', text.lower())
        content = f"{act_short_title}:{section_number}:{cleaned}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _extract_metadata_from_text(self, text: str) -> Dict[str, Any]:
        metadata = {
            "is_bailable": None,
            "is_cognizable": None,
            "is_compoundable": None,
            "punishment_summary": None,
            "min_punishment": None,
            "max_punishment": None,
            "fine_amount": None
        }
        
        text_lower = text.lower()
        
        if "bailable" in text_lower:
            if "non-bailable" in text_lower or "not bailable" in text_lower:
                metadata["is_bailable"] = False
            else:
                metadata["is_bailable"] = True
                
        if "cognizable" in text_lower:
            if "non-cognizable" in text_lower or "not cognizable" in text_lower:
                metadata["is_cognizable"] = False
            else:
                metadata["is_cognizable"] = True
                
        if "compoundable" in text_lower:
            if "non-compoundable" in text_lower or "not compoundable" in text_lower:
                metadata["is_compoundable"] = False
            else:
                metadata["is_compoundable"] = True
                
        punishment_patterns = [
            r'(?:punishment|imprisonment|sentence)\s*(?:is|shall be|for)\s*([^\.]{20,200})',
            r'with\s+(?:imprisonment|imprisonment for|fine)\s+([^\.]{20,200})',
        ]
        
        for pattern in punishment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["punishment_summary"] = match.group(1).strip()
                break
                
        fine_match = re.search(r'fine\s*(?:of|up to|not exceeding|not less than)?\s*[₹$]?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees|rs\.?)?', text, re.IGNORECASE)
        if fine_match:
            metadata["fine_amount"] = fine_match.group(1)
            
        return metadata

    def _extract_sections_improved(self, act_short_title: str) -> List[ParsedSection]:
        sections = []
        cleaned_text = self._clean_text(self.text)
        
        patterns = [
            re.compile(r'(?:^|\n)(\d{1,3}[A-Za-z]?)\.\s+([A-Z][^\n]{3,150})\n', re.MULTILINE),
            re.compile(r'(?:^|\n)Section\s+(\d{1,3}[A-Za-z]?)\.?\s+([^\n]{3,150})\n', re.MULTILINE | re.IGNORECASE),
            re.compile(r'(?:^|\n)(\d{1,3}[A-Za-z]?)\.\s+([^\n]{1,150})\n', re.MULTILINE),
        ]
        
        matches = []
        for pattern in patterns:
            matches = list(pattern.finditer(cleaned_text))
            if matches:
                print(f"✓ Found {len(matches)} sections using pattern {patterns.index(pattern)+1}")
                break
                
        if not matches:
            print("⚠️  No clear section matches found, trying fallback extraction...")
            return []
            
        for i, match in enumerate(matches):
            section_num = match.group(1).strip()
            section_title = match.group(2).strip()
            
            start_pos = match.end()
            if i < len(matches) - 1:
                end_pos = matches[i+1].start()
            else:
                end_pos = len(cleaned_text)
                
            content = cleaned_text[start_pos:end_pos].strip()
            
            metadata = self._extract_metadata_from_text(content)
            section_hash = self._compute_section_hash(act_short_title, section_num, content)
            
            sections.append(ParsedSection(
                section_number=section_num,
                section_title=section_title,
                bare_text=content,
                is_bailable=metadata["is_bailable"],
                is_cognizable=metadata["is_cognizable"],
                is_compoundable=metadata["is_compoundable"],
                punishment_summary=metadata["punishment_summary"],
                min_punishment=metadata["min_punishment"],
                max_punishment=metadata["max_punishment"],
                fine_amount=metadata["fine_amount"],
                hash=section_hash
            ))
            
        return sections

    def parse_bns(self) -> ParsedAct:
        print(f"📖 Parsing BNS from {self.pdf_path.name}...")
        self.extract_text(start_page=0, end_page=150)
        sections = self._extract_sections_improved("Bharatiya Nyaya Sanhita 2023")
        print(f"✓ Extracted {len(sections)} sections from BNS")
        
        return ParsedAct(
            short_title="Bharatiya Nyaya Sanhita 2023",
            full_title="The Bharatiya Nyaya Sanhita, 2023",
            year=2023,
            act_type="CENTRAL",
            category="CRIMINAL",
            sections=sections,
            effective_date="2024-07-01"
        )

    def parse_bnss(self) -> ParsedAct:
        print(f"📖 Parsing BNSS from {self.pdf_path.name}...")
        self.extract_text()
        sections = self._extract_sections_improved("Bharatiya Nagarik Suraksha Sanhita 2023")
        print(f"✓ Extracted {len(sections)} sections from BNSS")
        
        return ParsedAct(
            short_title="Bharatiya Nagarik Suraksha Sanhita 2023",
            full_title="The Bharatiya Nagarik Suraksha Sanhita, 2023",
            year=2023,
            act_type="CENTRAL",
            category="CRIMINAL",
            sections=sections,
            effective_date="2024-07-01"
        )

    def parse_bsa(self) -> ParsedAct:
        print(f"📖 Parsing BSA from {self.pdf_path.name}...")
        self.extract_text()
        sections = self._extract_sections_improved("Bharatiya Sakshya Adhiniyam 2023")
        print(f"✓ Extracted {len(sections)} sections from BSA")
        
        return ParsedAct(
            short_title="Bharatiya Sakshya Adhiniyam 2023",
            full_title="The Bharatiya Sakshya Adhiniyam, 2023",
            year=2023,
            act_type="CENTRAL",
            category="CRIMINAL",
            sections=sections,
            effective_date="2024-07-01"
        )


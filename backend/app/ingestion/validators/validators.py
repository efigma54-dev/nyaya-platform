
from typing import List, Dict, Any
from ..parsers.parsers import ParsedAct, ParsedSection


class LegalCorpusValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_act(self, parsed_act: ParsedAct) -> Dict[str, Any]:
        self.errors = []
        self.warnings = []
        section_numbers = set()

        if not parsed_act.short_title:
            self.errors.append("Act short title is missing")
        if not parsed_act.full_title:
            self.errors.append("Act full title is missing")
        if not parsed_act.act_type:
            self.errors.append("Act type is missing")
        if not parsed_act.category:
            self.errors.append("Act category is missing")
        
        if not parsed_act.sections:
            self.warnings.append("No sections found in act")
        
        valid_sections = []
        for i, section in enumerate(parsed_act.sections):
            is_valid = self._validate_section(section, i)
            if is_valid:
                if section.section_number in section_numbers:
                    self.warnings.append(f"Duplicate section number {section.section_number} at index {i}")
                else:
                    section_numbers.add(section.section_number)
                    valid_sections.append(section)
        
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_sections": len(parsed_act.sections),
            "valid_sections": len(valid_sections),
            "section_count": len(valid_sections)
        }

    def _validate_section(self, section: ParsedSection, index: int) -> bool:
        is_valid = True
        prefix = f"Section {section.section_number} (index {index})"
        
        if not section.section_number:
            self.errors.append(f"{prefix}: Section number is missing")
            is_valid = False
            
        if not section.bare_text or len(section.bare_text.strip()) < 20:
            self.warnings.append(f"{prefix}: Bare text is very short or missing")
            
        if not section.section_title:
            self.warnings.append(f"{prefix}: Section title is missing")
            
        if not section.hash:
            self.warnings.append(f"{prefix}: Section hash is missing")
            
        return is_valid


from typing import List, Set, Dict, Any
import hashlib
from ..parsers.parsers import ParsedSection


class Deduplicator:
    def __init__(self):
        self.seen_hashes: Set[str] = set()

    def _compute_section_hash(self, act_short_title: str, section_number: str, text: str) -> str:
        cleaned = ''.join(text.lower().split())
        content = f"{act_short_title}:{section_number}:{cleaned}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_duplicate(self, act_short_title: str, section_number: str, text: str) -> bool:
        section_hash = self._compute_section_hash(act_short_title, section_number, text)
        if section_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(section_hash)
        return False

    def deduplicate_sections(self, sections: List[ParsedSection], act_short_title: str) -> List[ParsedSection]:
        unique_sections = []
        self.seen_hashes.clear()
        
        for section in sections:
            if not self.is_duplicate(act_short_title, section.section_number, section.bare_text):
                unique_sections.append(section)
        
        removed = len(sections) - len(unique_sections)
        if removed > 0:
            print(f"⚠️  Removed {removed} duplicate sections from {act_short_title}")
            
        return unique_sections

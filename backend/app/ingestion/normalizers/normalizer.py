
from typing import Dict, Any, List
from pathlib import Path
import json
from ..parsers.parsers import ParsedAct, ParsedSection
from ..metadata.metadata_extractor import MetadataExtractor
from ..checksum.checksum import compute_content_sha256


class LegalNormalizer:
    @staticmethod
    def normalize_section(section: ParsedSection, act_short_title: str, chapter: str = None) -> Dict[str, Any]:
        extractor = MetadataExtractor()
        
        return {
            "act": act_short_title,
            "chapter": chapter,
            "section": section.section_number,
            "title": section.section_title,
            "body": section.bare_text,
            "explanations": extractor.extract_explanations(section.bare_text),
            "illustrations": extractor.extract_illustrations(section.bare_text),
            "exceptions": extractor.extract_exceptions(section.bare_text),
            "provisos": extractor.extract_provisos(section.bare_text),
            "keywords": extractor.extract_keywords(section.bare_text),
            "metadata": {
                "is_bailable": section.is_bailable,
                "is_cognizable": section.is_cognizable,
                "is_compoundable": section.is_compoundable,
                "punishment_summary": section.punishment_summary,
                "fine_amount": section.fine_amount,
                "effective_date": section.effective_date
            },
            "sha256": compute_content_sha256(section.bare_text)
        }
    
    @staticmethod
    def normalize_act(parsed_act: ParsedAct, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        normalized_sections = [
            LegalNormalizer.normalize_section(section, parsed_act.short_title)
            for section in parsed_act.sections
        ]
        
        return {
            "short_title": parsed_act.short_title,
            "full_title": parsed_act.full_title,
            "year": parsed_act.year,
            "act_type": parsed_act.act_type,
            "category": parsed_act.category,
            "source_metadata": source_metadata,
            "sections": normalized_sections,
            "sha256": compute_content_sha256(json.dumps(normalized_sections, sort_keys=True))
        }
    
    @staticmethod
    def save_normalized(data: Dict[str, Any], output_dir: Path, filename: str = None) -> Path:
        output_dir.mkdir(exist_ok=True, parents=True)
        if not filename:
            filename = f"{data['short_title'].lower().replace(' ', '_')}.json"
        file_path = output_dir / filename
        
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path

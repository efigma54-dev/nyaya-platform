
from typing import Dict, Any, List
from pathlib import Path
import json
import re


def simple_token_count(text: str) -> int:
    tokens = re.findall(r'\w+|[^\w\s]', text)
    return len(tokens)


class CorpusMetricsCalculator:
    def calculate_act_metrics(self, normalized_act: Dict[str, Any]) -> Dict[str, Any]:
        sections = normalized_act.get("sections", [])
        total_tokens = sum(simple_token_count(sec["body"]) for sec in sections)
        total_chars = sum(len(sec["body"]) for sec in sections)
        
        return {
            "act_title": normalized_act.get("short_title"),
            "sections_count": len(sections),
            "total_tokens": total_tokens,
            "total_characters": total_chars,
            "avg_tokens_per_section": total_tokens / len(sections) if sections else 0,
            "avg_chars_per_section": total_chars / len(sections) if sections else 0,
            "explanations_count": sum(len(sec.get("explanations", [])) for sec in sections),
            "illustrations_count": sum(len(sec.get("illustrations", [])) for sec in sections),
            "exceptions_count": sum(len(sec.get("exceptions", [])) for sec in sections),
            "provisos_count": sum(len(sec.get("provisos", [])) for sec in sections)
        }
    
    def calculate_corpus_metrics(self, normalized_acts: List[Dict[str, Any]]) -> Dict[str, Any]:
        act_metrics_list = [self.calculate_act_metrics(act) for act in normalized_acts]
        
        total_acts = len(normalized_acts)
        total_sections = sum(am["sections_count"] for am in act_metrics_list)
        total_tokens = sum(am["total_tokens"] for am in act_metrics_list)
        total_chars = sum(am["total_characters"] for am in act_metrics_list)
        
        seen_sections = set()
        duplicate_count = 0
        for act in normalized_acts:
            for sec in act.get("sections", []):
                key = f"{act['short_title']}:{sec['section']}"
                if key in seen_sections:
                    duplicate_count += 1
                seen_sections.add(key)
        
        return {
            "acts": total_acts,
            "chapters": 0,
            "sections": total_sections,
            "subsections": 0,
            "rules": 0,
            "notifications": 0,
            "judgments": 0,
            "duplicate_count": duplicate_count,
            "missing_sections": 0,
            "total_tokens": total_tokens,
            "total_characters": total_chars,
            "avg_chunk_size": total_chars / total_sections if total_sections else 0,
            "avg_tokens_per_section": total_tokens / total_sections if total_sections else 0,
            "missing_embeddings": 0,
            "act_metrics": act_metrics_list,
            "generated_at": __import__("datetime").datetime.now().isoformat()
        }
    
    def save_metrics(self, metrics: Dict[str, Any], output_path: Path):
        output_path.parent.mkdir(exist_ok=True, parents=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

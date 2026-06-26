
from typing import List, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class TextChunk:
    text: str
    metadata: Dict[str, Any]
    chunk_number: int
    chunk_type: str = "section"


class LegalTextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_section_legal_aware(self, section_text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        chunks: List[TextChunk] = []
        
        split_patterns = [
            r'(?:^|\n)(Explanation\s*\d*\.?)',
            r'(?:^|\n)(Illustration\s*\d*\.?)',
            r'(?:^|\n)(Exception\s*\d*\.?)',
            r'(?:^|\n)(Proviso\s*\d*\.?)',
            r'(?:^|\n)\(\d+\)\s*',
        ]
        
        split_points = []
        for pattern in split_patterns:
            for match in re.finditer(pattern, section_text, re.IGNORECASE):
                split_points.append(match.start())
                
        split_points = sorted(list(set(split_points)))
        
        if split_points:
            split_points = [0] + split_points + [len(section_text)]
            
            for i in range(len(split_points) - 1):
                start = split_points[i]
                end = split_points[i + 1]
                chunk_text = section_text[start:end].strip()
                
                if len(chunk_text) > 50:
                    chunk_type = "section"
                    chunk_text_lower = chunk_text.lower()
                    if "explanation" in chunk_text_lower:
                        chunk_type = "explanation"
                    elif "illustration" in chunk_text_lower:
                        chunk_type = "illustration"
                    elif "exception" in chunk_text_lower:
                        chunk_type = "exception"
                    elif "proviso" in chunk_text_lower:
                        chunk_type = "proviso"
                        
                    chunks.append(TextChunk(
                        text=chunk_text,
                        metadata={**metadata, "chunk_type": chunk_type},
                        chunk_number=len(chunks),
                        chunk_type=chunk_type
                    ))
                    
        if not chunks or any(len(c.text) > self.chunk_size for c in chunks):
            chunks = self._chunk_by_words(section_text, metadata)
            
        return chunks

    def _chunk_by_words(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        chunk_number = 0
        
        for word in words:
            word_length = len(word) + 1
            if current_length + word_length > self.chunk_size and current_chunk:
                chunks.append(TextChunk(
                    text=" ".join(current_chunk),
                    metadata={**metadata, "chunk_number": chunk_number, "chunk_type": "section"},
                    chunk_number=chunk_number,
                    chunk_type="section"
                ))
                chunk_number += 1
                overlap_words = current_chunk[-int(self.chunk_overlap / 5):]
                current_chunk = overlap_words
                current_length = sum(len(w) + 1 for w in overlap_words)
                
            current_chunk.append(word)
            current_length += word_length
            
        if current_chunk:
            chunks.append(TextChunk(
                text=" ".join(current_chunk),
                metadata={**metadata, "chunk_number": chunk_number, "chunk_type": "section"},
                chunk_number=chunk_number,
                chunk_type="section"
            ))
            
        return chunks

    def chunk_section(self, section_text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        return self.chunk_section_legal_aware(section_text, metadata)

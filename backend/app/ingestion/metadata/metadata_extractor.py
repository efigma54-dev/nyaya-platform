
from typing import List, Dict, Any
import re
from datetime import datetime


class MetadataExtractor:
    @staticmethod
    def extract_explanations(text: str) -> List[str]:
        explanations = []
        pattern = re.compile(r'(?:^|\n)(Explanation\s*\d*\.?\s*)([^\n]*(?:\n(?!Explanation|Illustration|Exception|Proviso|Section|\d+\.)[^\n]*)*)', re.IGNORECASE | re.MULTILINE)
        for match in pattern.finditer(text):
            explanations.append(match.group(2).strip())
        return explanations
    
    @staticmethod
    def extract_illustrations(text: str) -> List[str]:
        illustrations = []
        pattern = re.compile(r'(?:^|\n)(Illustration\s*\d*\.?\s*)([^\n]*(?:\n(?!Explanation|Illustration|Exception|Proviso|Section|\d+\.)[^\n]*)*)', re.IGNORECASE | re.MULTILINE)
        for match in pattern.finditer(text):
            illustrations.append(match.group(2).strip())
        return illustrations
    
    @staticmethod
    def extract_exceptions(text: str) -> List[str]:
        exceptions = []
        pattern = re.compile(r'(?:^|\n)(Exception\s*\d*\.?\s*)([^\n]*(?:\n(?!Explanation|Illustration|Exception|Proviso|Section|\d+\.)[^\n]*)*)', re.IGNORECASE | re.MULTILINE)
        for match in pattern.finditer(text):
            exceptions.append(match.group(2).strip())
        return exceptions
    
    @staticmethod
    def extract_provisos(text: str) -> List[str]:
        provisos = []
        pattern = re.compile(r'(?:^|\n)(Proviso\s*\d*\.?\s*)([^\n]*(?:\n(?!Explanation|Illustration|Exception|Proviso|Section|\d+\.)[^\n]*)*)', re.IGNORECASE | re.MULTILINE)
        for match in pattern.finditer(text):
            provisos.append(match.group(2).strip())
        return provisos
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        legal_terms = [
            "punishment", "imprisonment", "fine", "bailable", "cognizable", "compoundable",
            "offence", "crime", "court", "judge", "appeal", "appealate", "plaintiff",
            "defendant", "witness", "evidence", "testimony", "burden of proof"
        ]
        text_lower = text.lower()
        keywords = [term for term in legal_terms if term in text_lower]
        return keywords

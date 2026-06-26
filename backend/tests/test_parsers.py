
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.parsers import PDFLegalParser, ParsedSection, ParsedAct
from app.ingestion.validators import LegalCorpusValidator
from app.ingestion.deduplicator import Deduplicator
from app.ingestion.chunker import LegalTextChunker


def test_parsed_section_dataclass():
    """Test that ParsedSection dataclass works correctly."""
    section = ParsedSection(
        section_number="302",
        section_title="Murder",
        bare_text="Whoever commits murder shall be punished...",
        is_bailable=False,
        is_cognizable=True
    )
    
    assert section.section_number == "302"
    assert section.section_title == "Murder"
    assert section.is_bailable is False
    assert section.is_cognizable is True
    print("✅ test_parsed_section_dataclass passed")


def test_validator():
    """Test LegalCorpusValidator."""
    act = ParsedAct(
        short_title="Test Act",
        full_title="The Test Act, 2024",
        year=2024,
        act_type="CENTRAL",
        category="CRIMINAL",
        sections=[
            ParsedSection(
                section_number="1",
                section_title="Short Title",
                bare_text="This act may be called the Test Act."
            )
        ]
    )
    
    validator = LegalCorpusValidator()
    result = validator.validate_act(act)
    
    assert result["valid"] is True
    assert result["section_count"] == 1
    print("✅ test_validator passed")


def test_deduplicator():
    """Test Deduplicator."""
    sections = [
        ParsedSection(
            section_number="1",
            section_title="Title",
            bare_text="Content here"
        ),
        ParsedSection(  # Duplicate
            section_number="1",
            section_title="Title",
            bare_text="Content here"
        ),
        ParsedSection(
            section_number="2",
            section_title="Another Title",
            bare_text="Other content"
        )
    ]
    
    deduplicator = Deduplicator()
    unique = deduplicator.deduplicate_sections(sections, "Test Act")
    
    assert len(unique) == 2
    print("✅ test_deduplicator passed")


def test_chunker():
    """Test LegalTextChunker."""
    chunker = LegalTextChunker()
    text = """
    Section 1. This is the main section content.
    Explanation 1. This is an explanation of the section.
    Illustration. This is an example illustration.
    """
    
    chunks = chunker.chunk_section(text, {"test": "data"})
    
    assert len(chunks) &gt; 0
    print("✅ test_chunker passed")


if __name__ == "__main__":
    print("Running parser tests...")
    test_parsed_section_dataclass()
    test_validator()
    test_deduplicator()
    test_chunker()
    print("\n✅ All tests passed!")

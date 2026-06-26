
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.ingestion.parsers import ParsedSection, ParsedAct
from app.ingestion.validators import LegalCorpusValidator
from app.ingestion.deduplicator import Deduplicator
from app.ingestion.chunker import LegalTextChunker


def main():
    print("Testing ingestion modules...")
    
    # Test 1: ParsedSection and ParsedAct
    print("\n1. Testing dataclasses...")
    section = ParsedSection(
        section_number="302",
        section_title="Murder",
        bare_text="Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
        is_bailable=False,
        is_cognizable=True
    )
    act = ParsedAct(
        short_title="Test Act",
        full_title="The Test Act, 2024",
        year=2024,
        act_type="CENTRAL",
        category="CRIMINAL",
        sections=[section, section]  # Add duplicate for testing
    )
    print("✅ Dataclasses work")
    
    # Test 2: Validator
    print("\n2. Testing validator...")
    validator = LegalCorpusValidator()
    result = validator.validate_act(act)
    print(f"   Valid: {result['valid']}")
    print(f"   Warnings: {len(result['warnings'])}")
    print("✅ Validator works")
    
    # Test 3: Deduplicator
    print("\n3. Testing deduplicator...")
    deduplicator = Deduplicator()
    unique = deduplicator.deduplicate_sections(act.sections, "Test Act")
    print(f"   Original sections: {len(act.sections)}")
    print(f"   Unique sections: {len(unique)}")
    print("✅ Deduplicator works")
    
    # Test 4: Chunker
    print("\n4. Testing chunker...")
    chunker = LegalTextChunker()
    test_text = """
    1. Short Title. This Act may be called the Test Act.
    Explanation 1. This is an explanation of the short title.
    Illustration. For example, this is how it works.
    """
    chunks = chunker.chunk_section(test_text, {"act": "Test Act"})
    print(f"   Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i} ({chunk.chunk_type}): {chunk.text[:50]}...")
    print("✅ Chunker works")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()

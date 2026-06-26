
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 80)
print("🧪 NYAYA AI - SANITY CHECK (No External Services Needed)")
print("=" * 80)

all_passed = True


def test_parsers():
    global all_passed
    print("\n📄 1. Testing Parsers...")
    try:
        from app.ingestion.parsers import ParsedSection, ParsedAct

        # Test dataclasses
        section = ParsedSection(
            section_number="300",
            section_title="Murder",
            bare_text="Whoever commits murder shall be punished...",
            is_bailable=False,
            is_cognizable=True
        )
        act = ParsedAct(
            short_title="BNS",
            full_title="Bharatiya Nyaya Sanhita",
            year=2023,
            act_type="CENTRAL",
            category="CRIMINAL",
            sections=[section]
        )

        assert section.section_number == "300"
        assert section.section_title == "Murder"
        assert act.short_title == "BNS"
        assert len(act.sections) == 1
        print("  ✅ Parsers module works")
        return True
    except Exception as e:
        print(f"  ❌ Parsers failed: {e}")
        all_passed = False
        return False


def test_deduplicator():
    global all_passed
    print("\n🔍 2. Testing Deduplicator...")
    try:
        from app.ingestion.deduplicator import Deduplicator
        from app.ingestion.parsers import ParsedSection

        deduplicator = Deduplicator()

        sections = [
            ParsedSection(section_number="1", section_title="A", bare_text="Test 1"),
            ParsedSection(section_number="1", section_title="A", bare_text="Test 1"),  # Duplicate
            ParsedSection(section_number="2", section_title="B", bare_text="Test 2")
        ]

        unique = deduplicator.deduplicate_sections(sections, "Test Act")
        assert len(unique) == 2
        print("  ✅ Deduplicator works")
        return True
    except Exception as e:
        print(f"  ❌ Deduplicator failed: {e}")
        all_passed = False
        return False


def test_chunker():
    global all_passed
    print("\n✂️  3. Testing Chunker...")
    try:
        from app.ingestion.chunker import LegalTextChunker

        chunker = LegalTextChunker()
        test_text = """
        Section 300: Murder.
        Explanation 1: This explains murder.
        Illustration: A shoots B.
        Exception: Nothing except this.
        """

        chunks = chunker.chunk_section(test_text, {"test": "data"})
        assert len(chunks) >= 1
        print(f"  ✅ Chunker works, split into {len(chunks)} chunks")
        return True
    except Exception as e:
        print(f"  ❌ Chunker failed: {e}")
        all_passed = False
        return False


def test_validator():
    global all_passed
    print("\n✅ 4. Testing Validator...")
    try:
        from app.ingestion.validators import LegalCorpusValidator
        from app.ingestion.parsers import ParsedAct, ParsedSection

        validator = LegalCorpusValidator()

        act = ParsedAct(
            short_title="Test",
            full_title="Test Act",
            year=2024,
            act_type="CENTRAL",
            category="CRIMINAL",
            sections=[
                ParsedSection(section_number="1", section_title="A", bare_text="Test 1"),
                ParsedSection(section_number="2", section_title="B", bare_text="Test 2")
            ]
        )

        result = validator.validate_act(act)
        assert result["valid"] is True
        assert result["section_count"] == 2
        print("  ✅ Validator works")
        return True
    except Exception as e:
        print(f"  ❌ Validator failed: {e}")
        all_passed = False
        return False


def test_json_seed_data():
    global all_passed
    print("\n📦 5. Testing JSON Seed Data...")
    try:
        import json

        DATA_DIR = Path(__file__).parent / "data"
        DATA_FILES = ["bns.json", "bnss.json", "bsa.json"]

        for filename in DATA_FILES:
            file_path = DATA_DIR / filename
            assert file_path.exists()
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) >= 1
            print(f"  ✅ {filename} is valid JSON")

        return True
    except Exception as e:
        print(f"  ❌ JSON Seed Data failed: {e}")
        all_passed = False
        return False


def main():
    print("\nStarting sanity checks...")

    test_parsers()
    test_deduplicator()
    test_chunker()
    test_validator()
    test_json_seed_data()

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL SANITY CHECKS PASSED!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. docker-compose up -d  # Start services")
        print("  2. cd backend")
        print("  3. python -m scripts.run_full_pipeline  # Run full pipeline")
        print("  4. python -m scripts.validate_corpus  # Verify")
        return 0
    else:
        print("❌ SOME SANITY CHECKS FAILED!")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

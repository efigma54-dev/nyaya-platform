
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section
from app.ingestion.parsers import PDFLegalParser, ParsedAct
from app.ingestion.validators import LegalCorpusValidator
from sqlalchemy import select


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


async def ingest_act(parsed_act: ParsedAct):
    """Ingest a parsed act into the database."""
    async with AsyncSessionLocal() as db:
        # Check if act already exists
        result = await db.execute(select(Act).where(Act.short_title == parsed_act.short_title))
        existing_act = result.scalar_one_or_none()
        
        if existing_act:
            print(f"ℹ️ Act '{parsed_act.short_title}' already exists, skipping...")
            return
        
        # Create new act
        act = Act(
            short_title=parsed_act.short_title,
            full_title=parsed_act.full_title,
            year=parsed_act.year,
            act_type=parsed_act.act_type,
            category=parsed_act.category,
            source_url=parsed_act.source_url,
            is_active=True
        )
        db.add(act)
        await db.flush()
        
        # Add sections
        inserted = 0
        for parsed_section in parsed_act.sections:
            section = Section(
                act_id=act.id,
                section_number=parsed_section.section_number,
                section_title=parsed_section.section_title,
                bare_text=parsed_section.bare_text,
                plain_language=parsed_section.plain_language,
                is_bailable=parsed_section.is_bailable,
                is_cognizable=parsed_section.is_cognizable,
                is_compoundable=parsed_section.is_compoundable,
                punishment_summary=parsed_section.punishment_summary,
                min_punishment=parsed_section.min_punishment,
                max_punishment=parsed_section.max_punishment,
                fine_amount=parsed_section.fine_amount,
                relevant_court=parsed_section.relevant_court,
                limitation_period=parsed_section.limitation_period,
                is_active=True,
                is_amended=False
            )
            db.add(section)
            inserted += 1
        
        await db.commit()
        print(f"✅ Ingested act '{parsed_act.short_title}' with {inserted} sections")


async def main():
    pdf_files = {
        "bns.pdf": ("parse_bns", "Bharatiya Nyaya Sanhita"),
        "bnss.pdf": ("parse_bnss", "Bharatiya Nagarik Suraksha Sanhita"),
        "bsa.pdf": ("parse_bsa", "Bharatiya Sakshya Adhiniyam")
    }
    
    validator = LegalCorpusValidator()
    
    for filename, (parse_method, act_name) in pdf_files.items():
        pdf_path = DATA_DIR / filename
        if not pdf_path.exists():
            print(f"⚠️ {filename} not found, skipping {act_name}")
            continue
        
        print(f"\n📄 Processing {act_name} from {filename}...")
        parser = PDFLegalParser(pdf_path)
        parse_func = getattr(parser, parse_method)
        parsed_act = parse_func()
        
        # Validate
        validation_result = validator.validate_act(parsed_act)
        
        if validation_result["valid"]:
            print(f"✅ Validation passed for {act_name}")
            await ingest_act(parsed_act)
        else:
            print(f"❌ Validation failed for {act_name}:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
            for warning in validation_result["warnings"]:
                print(f"  ⚠️ {warning}")
    
    print("\n🎉 Ingestion pipeline complete!")


if __name__ == "__main__":
    asyncio.run(main())

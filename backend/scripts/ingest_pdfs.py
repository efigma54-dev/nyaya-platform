
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section
from app.ingestion.parsers import PDFLegalParser, ParsedAct
from app.ingestion.validators import LegalCorpusValidator
from app.ingestion.deduplicator import Deduplicator
from app.ingestion.chunker import LegalTextChunker
from app.rag.embedder import get_embedder
from app.rag.vector_store import get_vector_store
from sqlalchemy import select


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


async def ingest_act(parsed_act: ParsedAct):
    """Ingest a parsed act into the database, with chunking and embedding."""
    async with AsyncSessionLocal() as db:
        # Check if act already exists
        result = await db.execute(select(Act).where(Act.short_title == parsed_act.short_title))
        existing_act = result.scalar_one_or_none()
        
        if existing_act:
            print(f"ℹ️ Act '{parsed_act.short_title}' already exists, skipping...")
            return None
        
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
        
        # Initialize embedding components
        embedder = get_embedder()
        vector_store = get_vector_store()
        chunker = LegalTextChunker()
        
        inserted = 0
        embedded = 0
        
        # Add sections
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
                effective_date=parsed_section.effective_date,
                is_active=True,
                is_amended=False
            )
            db.add(section)
            await db.flush()
            inserted += 1
            
            # Chunk and embed the section
            try:
                metadata = {
                    "act_id": act.id,
                    "act_short_title": parsed_act.short_title,
                    "section_id": section.id,
                    "section_number": section.section_number,
                    "section_title": section.section_title or ""
                }
                
                chunks = chunker.chunk_section(section.bare_text, metadata)
                
                for chunk in chunks:
                    embedding = embedder.embed_text(chunk.text)
                    vector_store.add_vectors(
                        texts=[chunk.text],
                        embeddings=[embedding],
                        metadatas=[chunk.metadata]
                    )
                    
                embedded += 1
                
            except Exception as e:
                print(f"⚠️ Failed to embed section {section.section_number}: {e}")
            
        await db.commit()
        print(f"✅ Ingested act '{parsed_act.short_title}':")
        print(f"   - {inserted} sections added to DB")
        print(f"   - {embedded} sections embedded in vector store")
        
        return act


async def main():
    pdf_files = {
        "bns.pdf": ("parse_bns", "Bharatiya Nyaya Sanhita 2023"),
        "bnss.pdf": ("parse_bnss", "Bharatiya Nagarik Suraksha Sanhita 2023"),
        "bsa.pdf": ("parse_bsa", "Bharatiya Sakshya Adhiniyam 2023")
    }
    
    validator = LegalCorpusValidator()
    deduplicator = Deduplicator()
    
    for filename, (parse_method, act_name) in pdf_files.items():
        pdf_path = DATA_DIR / filename
        if not pdf_path.exists():
            print(f"⚠️ {filename} not found, skipping {act_name}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing {act_name} from {filename}")
        print(f"{'='*60}")
        
        # Parse PDF
        parser = PDFLegalParser(pdf_path)
        parse_func = getattr(parser, parse_method)
        parsed_act = parse_func()
        
        if not parsed_act.sections:
            print(f"❌ No sections extracted from {act_name}")
            continue
        
        # Deduplicate
        parsed_act.sections = deduplicator.deduplicate_sections(
            parsed_act.sections,
            act_name
        )
        
        # Validate
        validation_result = validator.validate_act(parsed_act)
        
        print(f"\nValidation result for {act_name}:")
        print(f"  Valid: {validation_result['valid']}")
        print(f"  Total sections: {validation_result['total_sections']}")
        print(f"  Valid sections: {validation_result['valid_sections']}")
        if validation_result['errors']:
            print(f"  Errors: {len(validation_result['errors'])}")
            for err in validation_result['errors']:
                print(f"    - {err}")
        if validation_result['warnings']:
            print(f"  Warnings: {len(validation_result['warnings'])}")
        
        # Ingest if valid
        if validation_result['valid'] or validation_result['valid_sections'] &gt; 0:
            await ingest_act(parsed_act)
        else:
            print(f"❌ Not ingesting {act_name} due to validation errors")
    
    print("\n" + "="*60)
    print("🎉 Ingestion pipeline complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

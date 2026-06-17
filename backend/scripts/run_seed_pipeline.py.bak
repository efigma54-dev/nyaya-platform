#!/usr/bin/env python
"""
Full seed + embed pipeline for Nyaya legal platform.
Runs migrations, seeds all data, and embeds sections into Qdrant.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal, engine
from app.models.legal import Base
from sqlalchemy import select, func, text
from app.models.legal import Act, Section
from app.rag.embedder import embed_text
from app.rag.vector_store import insert_sections_to_qdrant, get_qdrant_client, COLLECTION_NAME


async def run_migrations():
    """Run Alembic migrations."""
    print("🔄 Running Alembic migrations...")
    import subprocess
    result = subprocess.run(["alembic", "upgrade", "head"], cwd=Path(__file__).parent.parent)
    if result.returncode != 0:
        print("❌ Migrations failed")
        return False
    print("✅ Migrations completed")
    return True


async def seed_bns_sections():
    """Seed comprehensive BNS sections."""
    print("🔄 Seeding BNS sections...")
    from scripts.seed_bns_comprehensive import seed_bns_sections as seed_func
    await seed_func()
    print("✅ BNS sections seeded")


async def embed_all_sections():
    """Embed all sections into Qdrant."""
    print("🔄 Embedding sections into Qdrant...")
    
    async with AsyncSessionLocal() as db:
        # Get all active sections
        result = await db.execute(
            select(Section).where(Section.is_active == True).order_by(Section.id)
        )
        sections = result.scalars().all()
        
        if not sections:
            print("⚠️  No sections to embed")
            return
        
        print(f"  Found {len(sections)} sections to embed")
        
        # Batch embed and insert
        batch_size = 10
        for i in range(0, len(sections), batch_size):
            batch = sections[i:i+batch_size]
            embeddings = []
            section_dicts = []
            
            for section in batch:
                # Create embedding
                text_to_embed = f"{section.section_title} {section.plain_language}"
                try:
                    embedding = await asyncio.to_thread(embed_text, text_to_embed)
                    embeddings.append(embedding)
                    
                    section_dict = {
                        "id": section.id,
                        "section_number": section.section_number,
                        "section_title": section.section_title,
                        "act_id": section.act_id,
                        "bare_text": section.bare_text,
                        "plain_language": section.plain_language,
                        "is_bailable": section.is_bailable,
                        "is_cognizable": section.is_cognizable,
                        "punishment_summary": section.punishment_summary,
                    }
                    section_dicts.append(section_dict)
                except Exception as e:
                    print(f"  ⚠️  Failed to embed section {section.section_number}: {e}")
                    continue
            
            if embeddings:
                try:
                    # Insert batch to Qdrant
                    client = get_qdrant_client()

                    await asyncio.to_thread(
                        insert_sections_to_qdrant,
                        client,
                        section_dicts,
                        embeddings
                    )

                    print(f"  ✅ Embedded batch {i//batch_size + 1}/{(len(sections)-1)//batch_size + 1}")
                except Exception as e:
                    print(f"  ❌ Failed to insert batch: {e}")
        
        # Verify
        try:
            client = get_qdrant_client()
            vector_count = client.get_collection(COLLECTION_NAME).vectors_count
            print(f"✅ Embedded {vector_count} sections into Qdrant")
        except Exception as e:
            print(f"⚠️  Could not verify embeddings: {e}")


async def main():
    """Run full pipeline."""
    print("=" * 60)
    print("🚀 Nyaya Legal Platform - Full Seed + Embed Pipeline")
    print("=" * 60)
    
    try:
        # 1. Migrations
        if not await run_migrations():
            sys.exit(1)
        
        # 2. Seed
        await seed_bns_sections()
        
        # 3. Embed
        await embed_all_sections()
        
        print("=" * 60)
        print("✅ Pipeline complete!")
        print("=" * 60)
    
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

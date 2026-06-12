#!/usr/bin/env python
"""Embed all sections into Qdrant for vector search."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.legal import Section
from sqlalchemy import select
from app.rag.embedder import embed_text
from app.rag.vector_store import get_qdrant_client, COLLECTION_NAME
from qdrant_client.http.models import PointStruct

async def embed_sections():
    """Embed all sections and upsert to Qdrant."""
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
        
        print(f"  Found {len(sections)} sections to embed\n")
        
        client = get_qdrant_client()
        points = []
        
        for i, section in enumerate(sections, 1):
            # Create embedding
            text_to_embed = f"{section.section_title} {section.plain_language}"
            try:
                embedding = await asyncio.to_thread(embed_text, text_to_embed)
                
                # Create Qdrant point
                point = PointStruct(
                    id=section.id,
                    vector=embedding,
                    payload={
                        "section_number": section.section_number,
                        "section_title": section.section_title,
                        "act_id": section.act_id,
                        "bare_text": section.bare_text[:500],  # Truncate for storage
                        "plain_language": section.plain_language[:500],
                        "is_bailable": section.is_bailable,
                        "is_cognizable": section.is_cognizable,
                        "punishment_summary": section.punishment_summary or "",
                    }
                )
                points.append(point)
                
                if i % 5 == 0:
                    print(f"  Embedded {i}/{len(sections)} sections...")
                
            except Exception as e:
                print(f"  ⚠️  Failed to embed section {section.section_number}: {e}")
                continue
        
        if not points:
            print("❌ No embeddings created")
            return
        
        # Upsert all points to Qdrant in one batch
        print(f"\n  Upserting {len(points)} vectors to Qdrant...")
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"✅ Successfully embedded {len(points)} sections")
            
            # Verify
            info = client.get_collection(COLLECTION_NAME)
            print(f"✅ Qdrant now has {info.vectors_count} vectors")
            
        except Exception as e:
            print(f"❌ Failed to upsert: {e}")

if __name__ == "__main__":
    asyncio.run(embed_sections())

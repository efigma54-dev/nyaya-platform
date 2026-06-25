
import asyncio
import sys
from pathlib import Path

# Add current script's parent's parent to path (in container: /app/scripts → /app)
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.legal import Section
from sqlalchemy import select, func
from app.rag.vector_store import get_qdrant_client, COLLECTION_NAME

async def get_postgres_section_count():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(Section.id)))
        count = result.scalar_one()
        active_result = await db.execute(select(func.count(Section.id)).where(Section.is_active == True))
        active_count = active_result.scalar_one()
        return {"total": count, "active": active_count}

async def get_qdrant_vector_count():
    try:
        client = get_qdrant_client()
        collection_info = client.get_collection(COLLECTION_NAME)
        return collection_info.points_count
    except Exception as e:
        print(f"Qdrant error: {e}")
        return 0

async def main():
    print("=" * 60)
    print("Nyaya Platform - Current Data Counts")
    print("=" * 60)
    
    print("\n[1] Querying PostgreSQL...")
    pg_counts = await get_postgres_section_count()
    print(f"  Total sections: {pg_counts['total']}")
    print(f"  Active sections: {pg_counts['active']}")
    
    print("\n[2] Querying Qdrant...")
    qdrant_count = await get_qdrant_vector_count()
    print(f"  Total vectors: {qdrant_count}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

"""
Embed all active sections into Qdrant (batch bge-m3).
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tqdm import tqdm
from app.core.config import settings
from app.models.legal import Act, Section
from app.rag.embedder import embed_batch
from app.rag.vector_store import ensure_collection, upsert_section

BATCH_SIZE = 16


def build_embed_text(section: Section, act_title: str) -> str:
    parts = [
        f"Act: {act_title}",
        f"Section {section.section_number}: {section.section_title or ''}",
        section.bare_text or "",
    ]
    if section.plain_language:
        parts.append(f"Plain meaning: {section.plain_language}")
    if section.punishment_summary:
        parts.append(f"Punishment: {section.punishment_summary}")
    return "\n".join(filter(None, parts))[:1800]


def build_payload(section: Section, act: Act) -> dict:
    return {
        "section_id": section.id,
        "act_id": act.id,
        "act_title": act.short_title,
        "category": getattr(act.category, 'value', str(act.category)) if act.category else None,
        "section_number": section.section_number,
        "section_title": section.section_title or "",
        "bare_text": (section.bare_text or "")[:500],
        "plain_language": section.plain_language or "",
        "is_bailable": section.is_bailable,
        "is_cognizable": section.is_cognizable,
        "is_compoundable": section.is_compoundable,
        "punishment_summary": section.punishment_summary or "",
        "max_punishment": section.max_punishment or "",
        "min_punishment": section.min_punishment or "",
        "relevant_court": section.relevant_court or "",
        "limitation_period": section.limitation_period or "",
    }


async def embed_all_sections() -> None:
    print("🔮 Nyaya — Embedding sections into Qdrant")
    client = ensure_collection()

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        result = await session.execute(
            select(Section, Act)
            .join(Act, Act.id == Section.act_id)
            .where(Section.is_active.is_(True))
            .order_by(Section.id)
        )
        rows = list(result.all())

    if not rows:
        print("❌ No sections in DB. Run seed scripts first.")
        await engine.dispose()
        return

    print(f"  Found {len(rows)} sections")
    embedded = 0
    errors = 0

    for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Embedding"):
        batch = rows[i : i + BATCH_SIZE]
        texts = [build_embed_text(s, a.short_title) for s, a in batch]
        try:
            vectors = await asyncio.to_thread(embed_batch, texts)
        except Exception as e:
            print(f"❌ Batch {i} embed failed: {e}")
            errors += len(batch)
            continue

        for (section, act), vector in zip(batch, vectors):
            try:
                upsert_section(client, section.id, vector, build_payload(section, act))
                embedded += 1
            except Exception as e:
                print(f"❌ Upsert section {section.id}: {e}")
                errors += 1

    async with SessionLocal() as db:
        for section, _ in rows:
            res = await db.execute(select(Section).where(Section.id == section.id))
            s = res.scalar_one_or_none()
            if s:
                s.qdrant_id = str(section.id)
                s.embedding_model = "BAAI/bge-m3"
        await db.commit()

    await engine.dispose()
    print(f"✅ Done — embedded {embedded}, errors {errors}")


if __name__ == "__main__":
    asyncio.run(embed_all_sections())

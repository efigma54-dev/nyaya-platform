# scripts/embed_sections.py
# Embeds all DB sections into Qdrant. Run after sections are seeded.

from __future__ import annotations

import asyncio

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tqdm import tqdm

from app.core.config import settings
from app.models.legal import Act, Section
from app.rag.embedder import embed_batch
from app.rag.vector_store import ensure_collection, get_qdrant_client, upsert_section

BATCH_SIZE = 16


def build_embed_text(section: Section, act_title: str) -> str:
    """Text to embed: act + section + bare + optional plain + punishment."""
    parts = [
        f"Act: {act_title}",
        f"Section {section.section_number}: {section.section_title or ''}",
        section.bare_text or "",
    ]
    if section.plain_language:
        parts.append(f"Plain meaning: {section.plain_language}")
    if section.punishment_summary:
        parts.append(f"Punishment: {section.punishment_summary}")

    full_text = "\n".join(filter(None, parts))
    return full_text[:1800]


def build_payload(section: Section, act: Act) -> dict:
    """Payload stored with each vector (for cards / citations without extra SQL)."""
    return {
        "section_id": section.id,
        "act_id": act.id,
        "act_title": act.short_title,
        "category": act.category.value,
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


async def get_all_sections(session: AsyncSession) -> list[tuple[Section, Act]]:
    result = await session.execute(
        select(Section, Act)
        .join(Act, Act.id == Section.act_id)
        .where(Section.is_active.is_(True))
        .order_by(Section.id)
    )
    return list(result.all())


async def main() -> None:
    print("🔮 Nyaya — Embedding sections into Qdrant")
    print("=" * 50)

    print("\n📦 Setting up Qdrant collection...")
    client = ensure_collection()

    print("\n📚 Loading sections from database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with SessionLocal() as session:
        rows = await get_all_sections(session)

    print(f"  Found {len(rows)} sections to embed")

    if not rows:
        print("❌ No sections found. Run seed scripts first.")
        await engine.dispose()
        return

    print(f"\n🧠 Embedding with BAAI/bge-m3 (batch size={BATCH_SIZE})...")
    print("  First run downloads the model — may take several minutes.\n")

    embedded = 0
    errors = 0

    for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Embedding batches"):
        batch = rows[i : i + BATCH_SIZE]
        texts = [build_embed_text(section, act.short_title) for section, act in batch]

        try:
            vectors = embed_batch(texts)
        except Exception as e:
            print(f"\n❌ Embedding batch {i} failed: {e}")
            errors += len(batch)
            continue

        if len(vectors) != len(batch):
            print(f"\n❌ Batch {i}: expected {len(batch)} vectors, got {len(vectors)}")
            errors += len(batch)
            continue

        for (section, act), vector in zip(batch, vectors, strict=True):
            try:
                payload = build_payload(section, act)
                upsert_section(client, section.id, vector, payload)
                embedded += 1
            except Exception as e:
                print(f"\n❌ Upsert failed for section {section.id}: {e}")
                errors += 1

    print(f"\n💾 Updating qdrant_id in PostgreSQL...")
    async with SessionLocal() as db:
        for section, _act in rows:
            res = await db.execute(select(Section).where(Section.id == section.id))
            s = res.scalar_one_or_none()
            if s:
                s.qdrant_id = str(section.id)
                s.embedding_model = "BAAI/bge-m3"
        await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 50}")
    print("✅ Embedding complete")
    print(f"   Embedded : {embedded}")
    print(f"   Errors   : {errors}")
    print("\nNext: docker compose run --rm api python scripts/test_search.py")


if __name__ == "__main__":
    asyncio.run(main())

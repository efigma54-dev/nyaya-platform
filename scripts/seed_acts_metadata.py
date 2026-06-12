# scripts/seed_acts_metadata.py
# Run this FIRST — seeds Act rows before section ingestion

from __future__ import annotations

import asyncio

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.legal import Act, ActType, LawCategory

ACTS_TO_SEED = [
    {
        "short_title": "Bharatiya Nyaya Sanhita 2023",
        "full_title": "The Bharatiya Nyaya Sanhita, 2023 (replacing IPC 1860)",
        "act_number": "45",
        "year": 2023,
        "act_type": ActType.CENTRAL,
        "category": LawCategory.CRIMINAL,
        "state": None,
        "source_url": "https://www.indiacode.nic.in/handle/123456789/20062",
        "is_active": True,
    },
    {
        "short_title": "Constitution of India — Fundamental Rights",
        "full_title": "The Constitution of India — Part III: Fundamental Rights (Articles 12–35)",
        "act_number": None,
        "year": 1950,
        "act_type": ActType.CONSTITUTIONAL,
        "category": LawCategory.CONSTITUTIONAL,
        "state": None,
        "source_url": "https://www.indiacode.nic.in/handle/123456789/15240",
        "is_active": True,
    },
    {
        "short_title": "Consumer Protection Act 2019",
        "full_title": "The Consumer Protection Act, 2019",
        "act_number": "35",
        "year": 2019,
        "act_type": ActType.CENTRAL,
        "category": LawCategory.CONSUMER,
        "state": None,
        "source_url": "https://www.indiacode.nic.in/handle/123456789/13772",
        "is_active": True,
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        for act_data in ACTS_TO_SEED:
            result = await session.execute(
                select(Act).where(Act.short_title == act_data["short_title"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"⏭  Already exists: {act_data['short_title']}")
                continue

            act = Act(**act_data)
            session.add(act)
            await session.commit()
            await session.refresh(act)
            print(f"✅ Seeded act id={act.id}: {act.short_title}")

    async with SessionLocal() as session:
        result = await session.execute(select(Act).order_by(Act.id))
        rows = result.scalars().all()
        print("\nDone. Acts in DB:")
        for a in rows:
            print(f"  id={a.id}  {a.short_title}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

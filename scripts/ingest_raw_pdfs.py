from __future__ import annotations

import asyncio
import io
from pathlib import Path

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.legal import Act, Section

# reuse parsing functions from ingest_bare_acts
from scripts.ingest_bare_acts import parse_bns_pdf, ingest_act

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

FILE_MAP = {
    "bns.pdf": "Bharatiya Nyaya Sanhita 2023",
    "bnss.pdf": "Bharatiya Nagarik Suraksha Sanhita 2023",
    "bsa.pdf": "Bharatiya Sakshya Adhiniyam 2023",
}


async def main() -> None:
    print("🔎 Ingesting local raw PDFs from data/raw")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    for filename, act_title in FILE_MAP.items():
        path = RAW_DIR / filename
        if not path.exists():
            print(f"⚠️  Missing file: {path}")
            continue

        print(f"\n📥 Reading {path}")
        pdf_bytes = path.read_bytes()

        print("  📄 Parsing PDF into sections...")
        sections = parse_bns_pdf(pdf_bytes)
        print(f"  🔢 Parsed {len(sections)} sections for {act_title}")

        if not sections:
            print("  ⚠️  No sections parsed; skipping ingestion for this file.")
            continue

        async with SessionLocal() as session:
            inserted = await ingest_act(session, act_title, sections)
            print(f"  ✅ Ingested {inserted} sections for {act_title}")

    await engine.dispose()
    print("\n✅ Local PDF ingestion complete.")


if __name__ == "__main__":
    asyncio.run(main())

# scripts/ingest_bare_acts.py

from __future__ import annotations

import asyncio
import io
import re

import httpx
import pdfplumber
from tqdm import tqdm

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.legal import Act, Section
from utils import (
    clean_text,
    extract_punishment,
    is_bailable_from_text,
    is_cognizable_from_text,
)

# ─── PDF Sources (direct government PDFs) ─────────────────────
PDF_SOURCES = {
    "Bharatiya Nyaya Sanhita 2023": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/20062/1/a2023-45.pdf",
        "fallback_url": "https://prsindia.org/files/bills_acts/acts_parliament/2023/Bharatiya-Nyaya-Sanhita-2023.pdf",
        "fallback_url_2": "https://www.indiacode.nic.in/bitstream/123456789/20062/2/a2023-45.pdf",
    },
    "Consumer Protection Act 2019": {
        "url": "https://consumeraffairs.nic.in/sites/default/files/CP%20Act%202019.pdf",
        "fallback_url": "https://prsindia.org/files/bills_acts/acts_parliament/2019/Consumer_Protection_Act_2019.pdf",
        "fallback_url_2": "https://www.indiacode.nic.in/bitstream/123456789/13772/1/A2019-35.pdf",
    },
}

# ─── Hardcoded sections for Constitution Part III ─────────────
CONSTITUTION_PART_III = [
    {
        "section_number": "12",
        "section_title": "Definition of State",
        "bare_text": "In this Part, unless the context otherwise requires, 'the State' includes the Government and Parliament of India and the Government and the Legislature of each of the States and all local or other authorities within the territory of India or under the control of the Government of India.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court (Writ Jurisdiction)",
    },
    {
        "section_number": "13",
        "section_title": "Laws inconsistent with or in derogation of the fundamental rights",
        "bare_text": "(1) All laws in force in the territory of India immediately before the commencement of this Constitution, in so far as they are inconsistent with the provisions of this Part, shall, to the extent of such inconsistency, be void.\n(2) The State shall not make any law which takes away or abridges the rights conferred by this Part and any law made in contravention of this clause shall, to the extent of the contravention, be void.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court",
    },
    {
        "section_number": "14",
        "section_title": "Equality before law",
        "bare_text": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court (Article 32 / 226 writ)",
        "plain_language": "Every person — citizen or foreigner — has the right to equal treatment under the law. The government cannot discriminate arbitrarily.",
    },
    {
        "section_number": "15",
        "section_title": "Prohibition of discrimination",
        "bare_text": "(1) The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.\n(2) No citizen shall, on grounds only of religion, race, caste, sex, place of birth or any of them, be subject to any disability, liability, restriction or condition with regard to— (a) access to shops, public restaurants, hotels and places of public entertainment; or (b) the use of wells, tanks, bathing ghats, roads and places of public resort maintained wholly or partly out of State funds or dedicated to the use of the general public.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court",
        "plain_language": "The government cannot discriminate against citizens based on religion, caste, race, sex or place of birth. Public places must be accessible to all.",
    },
    {
        "section_number": "19",
        "section_title": "Protection of six freedoms",
        "bare_text": "(1) All citizens shall have the right— (a) to freedom of speech and expression; (b) to assemble peaceably and without arms; (c) to form associations or unions or co-operative societies; (d) to move freely throughout the territory of India; (e) to reside and settle in any part of the territory of India; and (g) to practise any profession, or to carry on any occupation, trade or business.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court",
        "plain_language": "Every citizen has six fundamental freedoms: speech, peaceful assembly, forming associations, moving freely, residing anywhere, and choosing any profession.",
    },
    {
        "section_number": "21",
        "section_title": "Protection of life and personal liberty",
        "bare_text": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court (Article 32) / High Court (Article 226)",
        "plain_language": "Nobody can be arrested, detained, or killed except by a fair legal process. This is the most fundamental right — it underlies every other liberty.",
    },
    {
        "section_number": "21A",
        "section_title": "Right to education",
        "bare_text": "The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court",
        "plain_language": "Every child aged 6 to 14 has a fundamental right to free education. The State must provide it.",
    },
    {
        "section_number": "22",
        "section_title": "Protection against arrest and detention",
        "bare_text": "(1) No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest nor shall he be denied the right to consult, and to be defended by, a legal practitioner of his choice.\n(2) Every person who is arrested and detained in custody shall be produced before the nearest magistrate within a period of twenty-four hours of such arrest excluding the time necessary for the journey from the place of arrest to the court of the magistrate and no such person shall be detained in custody beyond the said period without the authority of a magistrate.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court / Magistrate Court",
        "plain_language": "When arrested: (1) You must be told WHY you are being arrested. (2) You have the right to a lawyer. (3) You must be produced before a magistrate within 24 hours. Police cannot hold you longer without magistrate's permission.",
    },
    {
        "section_number": "32",
        "section_title": "Right to constitutional remedies",
        "bare_text": "(1) The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed.\n(2) The Supreme Court shall have power to issue directions or orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari, whichever may be appropriate, for the enforcement of any of the rights conferred by this Part.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court of India",
        "plain_language": "If any fundamental right is violated, you can directly approach the Supreme Court. This is itself a fundamental right — Dr. Ambedkar called it the 'heart and soul' of the Constitution.",
    },
]


async def download_pdf(*urls: str | None) -> bytes | None:
    """Download PDF; try each URL until one returns PDF bytes (%PDF magic)."""
    base_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
    }
    for target_url in (u for u in urls if u):
            try:
                preview = target_url[:80] + ("…" if len(target_url) > 80 else "")
                print(f"  📥 Downloading from {preview}")
                headers = dict(base_headers)
                if "indiacode.nic.in" in target_url:
                    headers["Referer"] = "https://www.indiacode.nic.in/"
                verify_ssl = "consumeraffairs.nic.in" not in target_url
                async with httpx.AsyncClient(
                    timeout=90.0,
                    follow_redirects=True,
                    verify=verify_ssl,
                ) as client:
                    response = await client.get(target_url, headers=headers)
                data = response.content
                if data[:4] == b"%PDF":
                    print(f"  ✅ Downloaded {len(data) / 1024:.1f} KB (HTTP {response.status_code})")
                    return data
                print(f"  ⚠️  HTTP {response.status_code} (not a PDF body)")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
    return None


def parse_bns_pdf(pdf_bytes: bytes) -> list[dict]:
    """Parse BNS PDF into sections."""
    sections: list[dict] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        print(f"  📄 PDF has {len(pdf.pages)} pages")
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # Accept headings where the title may start in Latin (English) OR Devanagari (Hindi).
    # Example matches: "1. Title..." or "1. उपबंध ..."
    section_pattern = re.compile(
        r"(?:^|\n)(\d{1,3}[A-Z]?)\.\s+([A-Z\u0900-\u097F][^\n]{3,120})\n",
        re.MULTILINE,
    )

    matches = list(section_pattern.finditer(full_text))
    # If the stricter heading pattern found nothing, try a looser numeric-heading pattern
    # that captures lines starting with a number + dot followed by any non-empty title.
    if not matches:
        alt_pattern = re.compile(r"(?:^|\n)(\d{1,3}[A-Z]?)\.\s+([^\n]{1,120})\n", re.MULTILINE)
        matches = list(alt_pattern.finditer(full_text))
        print(f"  🔍 Found {len(matches)} section headings (loose numeric fallback)")
    else:
        print(f"  🔍 Found {len(matches)} section headings")

    for i, match in enumerate(matches):
        sec_num = match.group(1).strip()
        sec_title = match.group(2).strip()

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = full_text[start:end].strip()
        body = clean_text(body)

        if len(body) < 20:
            continue

        punishment = extract_punishment(body)

        sections.append(
            {
                "section_number": sec_num,
                "section_title": sec_title,
                "bare_text": body,
                "is_bailable": is_bailable_from_text(body),
                "is_cognizable": is_cognizable_from_text(body),
                **punishment,
                "relevant_court": _detect_court(body),
            }
        )

    return sections


def parse_consumer_protection_pdf(pdf_bytes: bytes) -> list[dict]:
    """Parse Consumer Protection Act PDF."""
    sections: list[dict] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    section_pattern = re.compile(
        r"(?:^|\n)(\d{1,3})\.\s+([A-Z][^\n]{3,100})[.—]\s*\n",
        re.MULTILINE,
    )
    matches = list(section_pattern.finditer(full_text))

    for i, match in enumerate(matches):
        sec_num = match.group(1).strip()
        sec_title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = clean_text(full_text[start:end])

        if len(body) < 20:
            continue

        sections.append(
            {
                "section_number": sec_num,
                "section_title": sec_title,
                "bare_text": body,
                "is_bailable": None,
                "is_cognizable": None,
                "relevant_court": "District Consumer Disputes Redressal Commission",
                "punishment_summary": None,
                "max_punishment": None,
                "min_punishment": None,
                "fine_amount": None,
            }
        )

    return sections


def _detect_court(text: str) -> str | None:
    """Detect which court handles this section."""
    text_lower = text.lower()
    if "sessions court" in text_lower or "sessions judge" in text_lower:
        return "Sessions Court"
    if "magistrate" in text_lower:
        return "Magistrate Court"
    if "high court" in text_lower:
        return "High Court"
    if "supreme court" in text_lower:
        return "Supreme Court"
    return None


async def ingest_act(
    session: AsyncSession,
    act_title: str,
    sections_data: list[dict],
) -> int:
    """Insert sections for an act into the database."""
    result = await session.execute(select(Act).where(Act.short_title == act_title))
    act = result.scalar_one_or_none()
    if not act:
        print(f"❌ Act not found: {act_title}. Run seed_acts_metadata.py first.")
        return 0

    inserted = 0
    skipped = 0

    for data in tqdm(sections_data, desc=f"  Inserting {act_title[:40]}"):
        existing = await session.execute(
            select(Section).where(
                Section.act_id == act.id,
                Section.section_number == data["section_number"],
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        section = Section(
            act_id=act.id,
            section_number=data["section_number"],
            section_title=data.get("section_title"),
            bare_text=data["bare_text"],
            plain_language=data.get("plain_language"),
            is_bailable=data.get("is_bailable"),
            is_cognizable=data.get("is_cognizable"),
            punishment_summary=data.get("punishment_summary"),
            max_punishment=data.get("max_punishment"),
            min_punishment=data.get("min_punishment"),
            fine_amount=data.get("fine_amount"),
            relevant_court=data.get("relevant_court"),
            is_active=True,
        )
        session.add(section)
        inserted += 1

    await session.commit()
    print(f"  ✅ Inserted {inserted} sections, skipped {skipped} existing")
    return inserted


async def main() -> None:
    print("🏛  Nyaya Legal Data Ingestion")
    print("=" * 50)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with SessionLocal() as session:
        print("\n📜 Ingesting Constitution of India — Part III...")
        count = await ingest_act(
            session,
            "Constitution of India — Fundamental Rights",
            CONSTITUTION_PART_III,
        )
        print(f"  Constitution: {count} articles ingested")

        print("\n⚖️  Ingesting Bharatiya Nyaya Sanhita 2023...")
        source = PDF_SOURCES["Bharatiya Nyaya Sanhita 2023"]
        pdf_bytes = await download_pdf(
            source["url"],
            source.get("fallback_url"),
            source.get("fallback_url_2"),
        )

        if pdf_bytes:
            bns_sections = parse_bns_pdf(pdf_bytes)
            print(f"  Parsed {len(bns_sections)} BNS sections from PDF")
            if bns_sections:
                count = await ingest_act(session, "Bharatiya Nyaya Sanhita 2023", bns_sections)
                print(f"  BNS: {count} sections ingested")
            else:
                print("  ⚠️  PDF parsed but no sections extracted — PDF layout may differ")
        else:
            print("  ⚠️  Could not download BNS PDF — skipping")

        print("\n🛒 Ingesting Consumer Protection Act 2019...")
        source = PDF_SOURCES["Consumer Protection Act 2019"]
        pdf_bytes = await download_pdf(
            source["url"],
            source.get("fallback_url"),
            source.get("fallback_url_2"),
        )

        if pdf_bytes:
            cpa_sections = parse_consumer_protection_pdf(pdf_bytes)
            print(f"  Parsed {len(cpa_sections)} CPA sections from PDF")
            if cpa_sections:
                count = await ingest_act(session, "Consumer Protection Act 2019", cpa_sections)
                print(f"  CPA: {count} sections ingested")
        else:
            print("  ⚠️  Could not download CPA PDF — skipping")

    await engine.dispose()

    print("\n" + "=" * 50)
    print("✅ Ingestion complete.")
    print("Next: run scripts/embed_sections.py to build Qdrant vector index")


if __name__ == "__main__":
    asyncio.run(main())

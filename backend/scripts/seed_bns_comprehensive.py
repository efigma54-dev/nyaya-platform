import asyncio
import json
from pathlib import Path

from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILES = ["bns.json", "bnss.json", "bsa.json"]

DEFAULT_BNS_SECTIONS = [
    {
        "act": {
            "short_title": "Bharatiya Nyaya Sanhita 2023",
            "full_title": "The Bharatiya Nyaya Sanhita, 2023",
            "year": 2023,
            "act_type": "CENTRAL",
            "category": "CRIMINAL",
        },
        "sections": [
            {"number": "103", "title": "Definitions", "bare_text": "In this Sanhita, unless the context otherwise requires, the following definitions apply...", "plain_language": "This section defines key legal terms used throughout the BNS 2023 including concepts like 'act', 'voluntarily', 'person', and other fundamental legal definitions.", "is_bailable": True, "is_cognizable": False},
            {"number": "104", "title": "General Exceptions", "bare_text": "Nothing is an offence which is done by a person who, at the time of doing it, by reason of unsoundness of mind, is incapable of knowing the nature of the act, or that he is doing what is either wrong or contrary to law.", "plain_language": "A person cannot be punished for an act done while suffering from mental illness if they couldn't understand their actions or their wrongfulness.", "is_bailable": True, "is_cognizable": False},
            {"number": "105", "title": "Act of a person of unsound mind", "bare_text": "No act is an offence by reason of any harm which it may cause to a person who, at the time when it is done, is incapable of knowing that the act is harm to him, or knowing it is so, has given his consent in circumstances which, though the circumstances invalidate the consent, in law do not make the act an offence by reason of the unsoundness of mind.", "plain_language": "Acts done to persons mentally incapable of consenting are not offences if they cannot understand the harm.", "is_bailable": True, "is_cognizable": False},
            {"number": "109", "title": "Act done by a person not knowing it is illegal", "bare_text": "Nothing is an offence which is done by a person who, at the time of doing it, by reason of a mistake of fact and not by reason of a mistake of law in force in India, is incapable of knowing that the act is an offence, or that he is doing what is wrong or contrary to law.", "plain_language": "If someone commits an act by honest mistake of fact (not law), they cannot be punished if they couldn't know it was wrong.", "is_bailable": True, "is_cognizable": False},
            {"number": "115", "title": "Definitions of 'Voluntarily'", "bare_text": "A person is said to cause an effect 'voluntarily' when he causes it by means whereby he intended to cause it, or by means which, at the time of employing them, he knew or had reason to believe to be likely to cause it.", "plain_language": "An act is voluntary when a person intends to cause the effect or knows their actions are likely to cause it.", "is_bailable": True, "is_cognizable": False},
            {"number": "116", "title": "Act of person bound by law", "bare_text": "Whoever, being bound by law to take charge of any person in a state of unsoundness of mind, leaves that person in circumstances under which, if he were in a sound state of mind, he would be unable to save himself from death, is guilty of an offence.", "plain_language": "A caregiver who abandons a mentally ill person in dangerous circumstances commits an offence.", "is_bailable": False, "is_cognizable": True, "punishment_summary": "Imprisonment up to 6 months or fine up to ₹500"},
            {"number": "300", "title": "Definition of murder", "bare_text": "Except in the cases hereinafter excepted, culpable homicide by causing death with the intention of causing death, or with the knowledge that the act is so imminently dangerous that it must in all probability cause death, shall amount to the offence of murder.", "plain_language": "Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death.", "is_bailable": False, "is_cognizable": True, "punishment_summary": "Life imprisonment or death penalty"},
            {"number": "301", "title": "Culpable homicide not amounting to murder", "bare_text": "Whoever causes death by doing an act with the intention of causing death, or with knowledge that he is likely by such act to cause death, commits the offence of culpable homicide not amounting to murder, if the circumstances of the case do not amount to culpable homicide amounting to murder.", "plain_language": "Causing death without the specific intention or knowledge required for murder, but with criminal negligence or recklessness.", "is_bailable": False, "is_cognizable": True, "punishment_summary": "Imprisonment up to 10 years or fine up to ₹10,000"},
        ]
    }
]


def load_json_file(path: Path) -> list[dict]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return []
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}, got {type(data).__name__}")
    return data


def load_seed_acts() -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    loaded_acts: list[dict] = []

    for filename in DATA_FILES:
        path = DATA_DIR / filename
        acts = load_json_file(path)
        if acts:
            print(f"🔁 Loaded {len(acts)} act(s) from {filename}")
            loaded_acts.extend(acts)

    if loaded_acts:
        return loaded_acts

    print("⚠️  No JSON seed files found in data/. Falling back to built-in demo BNS dataset.")
    return DEFAULT_BNS_SECTIONS


async def seed_bns_sections():
    act_entries = load_seed_acts()
    if not act_entries:
        print("⚠️  No act entries available to seed.")
        return

    async with AsyncSessionLocal() as db:
        for act_data in act_entries:
            act_meta = act_data["act"]
            short_title = act_meta["short_title"]

            result = await db.execute(select(Act).where(Act.short_title == short_title))
            existing_acts = result.scalars().all()

            if existing_acts:
                if len(existing_acts) > 1:
                    print(f"🗑️  Cleaning up {len(existing_acts) - 1} duplicate acts for {short_title}...")
                    for act in existing_acts[1:]:
                        await db.delete(act)
                    await db.commit()
                act = existing_acts[0]
            else:
                act = Act(
                    short_title=act_meta["short_title"],
                    full_title=act_meta["full_title"],
                    year=act_meta["year"],
                    act_type=act_meta["act_type"],
                    category=act_meta["category"],
                    is_active=True,
                )
                db.add(act)
                await db.flush()

            inserted = 0
            for sec_data in act_data.get("sections", []):
                existing_section = await db.execute(
                    select(Section).where(
                        Section.act_id == act.id,
                        Section.section_number == sec_data["number"],
                    )
                )
                if existing_section.scalar_one_or_none():
                    continue

                section = Section(
                    act_id=act.id,
                    section_number=sec_data["number"],
                    section_title=sec_data.get("title"),
                    bare_text=sec_data["bare_text"],
                    plain_language=sec_data.get("plain_language"),
                    is_bailable=sec_data.get("is_bailable"),
                    is_cognizable=sec_data.get("is_cognizable"),
                    punishment_summary=sec_data.get("punishment_summary"),
                    max_punishment=sec_data.get("max_punishment"),
                    min_punishment=sec_data.get("min_punishment"),
                    fine_amount=sec_data.get("fine_amount"),
                    relevant_court=sec_data.get("relevant_court"),
                    limitation_period=sec_data.get("limitation_period"),
                    is_active=True,
                    is_amended=False,
                )
                db.add(section)
                inserted += 1

            if inserted:
                await db.commit()
                print(f"✅ Seeded {inserted} new section(s) for {short_title}")
            else:
                print(f"✅ {short_title} already has its seed sections")


if __name__ == "__main__":
    asyncio.run(seed_bns_sections())

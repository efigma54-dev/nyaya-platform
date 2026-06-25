
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from app.models.legal import Act, Section, ActType, LawCategory
from app.core.database import AsyncSessionLocal, engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio

CONSTITUTION_PART_III = [
    {
        "section_number": "12",
        "section_title": "Definition of State",
        "bare_text": "In this Part, unless the context otherwise requires, 'the State' includes the Government and Parliament of India and the Government and the Legislature of each of the States and all local or other authorities within the territory of India or under the control of the Government of India.",
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "Supreme Court / High Court (Writ Jurisdiction)",
        "plain_language": "Every person — citizen or foreigner — has the right to equal treatment under the law. The government cannot discriminate arbitrarily.",
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

async def seed_constitution():
    async with AsyncSessionLocal() as session:
        # Check if the Constitution act already exists
        result = await session.execute(select(Act).where(Act.short_title == "Constitution of India — Fundamental Rights"))
        act = result.scalar_one_or_none()
        
        if not act:
            print("Creating Constitution of India — Fundamental Rights act")
            act = Act(
                short_title="Constitution of India — Fundamental Rights",
                full_title="Constitution of India — Part III (Fundamental Rights)",
                act_type=ActType.CONSTITUTIONAL,
                category=LawCategory.CONSTITUTIONAL,
                is_active=True,
            )
            session.add(act)
            await session.commit()
            await session.refresh(act)
        
        print(f"Act ID: {act.id}")
        
        # Seed the sections
        inserted = 0
        for section_data in CONSTITUTION_PART_III:
            # Check if section already exists
            result = await session.execute(
                select(Section).where(
                    Section.act_id == act.id,
                    Section.section_number == section_data["section_number"],
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                print(f"Inserting Section {section_data['section_number']}")
                section = Section(
                    act_id=act.id,
                    section_number=section_data["section_number"],
                    section_title=section_data["section_title"],
                    bare_text=section_data["bare_text"],
                    plain_language=section_data.get("plain_language"),
                    is_bailable=section_data.get("is_bailable"),
                    is_cognizable=section_data.get("is_cognizable"),
                    relevant_court=section_data.get("relevant_court"),
                    is_active=True,
                    is_amended=False,
                )
                session.add(section)
                inserted += 1
        
        if inserted:
            await session.commit()
            print(f"Inserted {inserted} Constitution sections")
        else:
            print("All Constitution sections already exist")

if __name__ == "__main__":
    asyncio.run(seed_constitution())

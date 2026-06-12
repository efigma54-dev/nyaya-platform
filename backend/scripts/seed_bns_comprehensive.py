import asyncio
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section

BNS_SECTIONS = [
    {
        "act": {"short_title": "Bharatiya Nyaya Sanhita 2023", "full_title": "The Bharatiya Nyaya Sanhita, 2023", "year": 2023, "act_type": "CENTRAL", "category": "CRIMINAL"},
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

async def seed_bns_sections():
    async with AsyncSessionLocal() as db:
        # Check if BNS 2023 already exists
        result = await db.execute(
            select(Act).where(Act.short_title == "Bharatiya Nyaya Sanhita 2023")
        )
        existing_acts = result.scalars().all()
        
        if existing_acts:
            # Check if we have exactly 1 act with 8 sections
            if len(existing_acts) == 1:
                count = await db.scalar(
                    select(func.count(Section.id)).where(Section.act_id == existing_acts[0].id)
                )
                if count == 8:
                    print("✅ BNS data already properly seeded, skipping...")
                    return
            
            # Delete duplicates — keep only first one
            print(f"🗑️  Cleaning up {len(existing_acts)} duplicate acts...")
            for act in existing_acts[1:]:
                await db.delete(act)
            await db.commit()
        
        # Now seed if needed
        result = await db.execute(
            select(Act).where(Act.short_title == "Bharatiya Nyaya Sanhita 2023")
        )
        existing_acts = result.scalars().all()
        
        if not existing_acts:
            for act_data in BNS_SECTIONS:
                # Create Act
                act = Act(
                    short_title=act_data["act"]["short_title"],
                    full_title=act_data["act"]["full_title"],
                    year=act_data["act"]["year"],
                    act_type=act_data["act"]["act_type"],
                    category=act_data["act"]["category"],
                    is_active=True
                )
                db.add(act)
                await db.flush()
                
                # Create Sections
                for sec_data in act_data["sections"]:
                    section = Section(
                        act_id=act.id,
                        section_number=sec_data["number"],
                        section_title=sec_data["title"],
                        bare_text=sec_data["bare_text"],
                        plain_language=sec_data["plain_language"],
                        is_bailable=sec_data.get("is_bailable"),
                        is_cognizable=sec_data.get("is_cognizable"),
                        punishment_summary=sec_data.get("punishment_summary"),
                        is_active=True,
                        is_amended=False
                    )
                    db.add(section)
                
                await db.commit()
            
            print("✅ BNS Sections seeded successfully")

if __name__ == "__main__":
    asyncio.run(seed_bns_sections())

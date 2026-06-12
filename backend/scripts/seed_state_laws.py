import asyncio
from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section, ActType, LawCategory

async def seed_state_laws():
    async with AsyncSessionLocal() as db:
        acts = [
            Act(
                short_title="Maharashtra Police Act",
                full_title="The Maharashtra Police Act, 1951",
                year=1951,
                act_type=ActType.STATE,
                category=LawCategory.CRIMINAL,
                state="Maharashtra"
            ),
            Act(
                short_title="UP Revenue Code",
                full_title="The Uttar Pradesh Revenue Code, 2006",
                year=2006,
                act_type=ActType.STATE,
                category=LawCategory.PROPERTY,
                state="Uttar Pradesh"
            )
        ]
        db.add_all(acts)
        await db.flush() # Get IDs
        
        sections = [
            Section(
                act_id=acts[0].id,
                section_number="33",
                section_title="Power to make rules for regulation of traffic",
                bare_text="The Commissioner, with the previous sanction of the State Government, may from time to time make rules...",
                plain_language="Gives the Police Commissioner power to make traffic rules with state government approval.",
                is_active=True
            ),
            Section(
                act_id=acts[1].id,
                section_number="101",
                section_title="Classes of tenures",
                bare_text="There shall be the following classes of tenure holders, namely— (a) bhumidhar with transferable rights...",
                plain_language="Defines different types of land ownership in Uttar Pradesh.",
                is_active=True
            )
        ]
        db.add_all(sections)
        await db.commit()
        print(f"✅ State laws seeded successfully")

if __name__ == "__main__":
    asyncio.run(seed_state_laws())

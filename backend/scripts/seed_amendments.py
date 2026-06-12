import asyncio
import sys
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section, Amendment

async def seed_amendments():
    async with AsyncSessionLocal() as db:
        # Get some sections to attach amendments to
        result = await db.execute(select(Section, Act).join(Act).limit(10))
        rows = result.all()
        
        if not rows:
            print("No sections found to attach amendments. Run seed_laws first.")
            return

        print(f"Seeding amendments for {len(rows)} sections...")
        
        for s, act in rows:
            # Add a mock amendment
            amendment = Amendment(
                section_id=s.id,
                effective_date="2024-07-01",
                old_text="[Text from previous law version]",
                new_text=s.bare_text,
                amendment_act="Bharatiya Nyaya Sanhita, 2023",
                notes="This section was transitioned from the IPC to the BNS as part of the 2023 legal reforms."
            )
            db.add(amendment)
            s.is_amended = True
            
        await db.commit()
        print("✅ Amendments seeded successfully")

if __name__ == "__main__":
    asyncio.run(seed_amendments())

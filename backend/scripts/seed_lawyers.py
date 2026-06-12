import asyncio
from app.core.database import AsyncSessionLocal
from app.models.lawyer import Lawyer

async def seed_lawyers():
    async with AsyncSessionLocal() as db:
        lawyers = [
            Lawyer(
                full_name="Adv. Rajesh Khanna",
                specialization="Criminal Law",
                location="New Delhi",
                experience_years=15,
                bio="Expert in IPC and BNS 2023 transitions. 15+ years experience in District and High Courts.",
                is_verified=True,
                rating=5
            ),
            Lawyer(
                full_name="Adv. Meera Sethi",
                specialization="Family Law",
                location="Mumbai",
                experience_years=10,
                bio="Specialist in matrimonial disputes, divorce, and domestic violence cases.",
                is_verified=True,
                rating=4
            ),
            Lawyer(
                full_name="Adv. Amit Verma",
                specialization="Consumer Rights",
                location="Bangalore",
                experience_years=8,
                bio="Dedicated to consumer protection and compensation claims against corporate entities.",
                is_verified=True,
                rating=5
            ),
            Lawyer(
                full_name="Adv. Priya Sharma",
                specialization="Cyber Law",
                location="Pune",
                experience_years=6,
                bio="Focuses on IT Act violations, online fraud, and data privacy issues.",
                is_verified=True,
                rating=4
            )
        ]
        
        db.add_all(lawyers)
        await db.commit()
        print(f"✅ {len(lawyers)} lawyers seeded successfully")

if __name__ == "__main__":
    asyncio.run(seed_lawyers())

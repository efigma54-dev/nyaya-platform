
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.lawyer import Lawyer
from app.models.legal import Amendment
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        lawyers = await db.execute(select(Lawyer))
        amendments = await db.execute(select(Amendment))
        print(f"Lawyers in DB: {len(lawyers.scalars().all())}")
        print(f"Amendments in DB: {len(amendments.scalars().all())}")

if __name__ == "__main__":
    asyncio.run(check())

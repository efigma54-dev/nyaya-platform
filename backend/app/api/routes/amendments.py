from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.legal import Amendment, Section, Act

router = APIRouter()

@router.get("/recent")
async def get_recent_amendments(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Returns the most recent amendments across all acts.
    """
    stmt = (
        select(Amendment, Section, Act)
        .join(Section, Amendment.section_id == Section.id)
        .join(Act, Section.act_id == Act.id)
        .order_by(desc(Amendment.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "id": a.id,
            "section_number": s.section_number,
            "act_title": act.short_title,
            "effective_date": a.effective_date,
            "amendment_act": a.amendment_act,
            "notes": a.notes,
            "new_text_snippet": a.new_text[:200] + "..." if len(a.new_text) > 200 else a.new_text
        }
        for a, s, act in rows
    ]

@router.get("/section/{section_id}")
async def get_section_amendments(section_id: int, db: AsyncSession = Depends(get_db)):
    """
    Returns all amendments for a specific section (the timeline).
    """
    stmt = (
        select(Amendment)
        .where(Amendment.section_id == section_id)
        .order_by(desc(Amendment.effective_date))
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return rows

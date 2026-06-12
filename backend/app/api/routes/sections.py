# backend/app/api/routes/sections.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.legal import Act, LawCategory, Section

router = APIRouter(tags=["sections"])


@router.get("/search")
async def search_sections(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
    limit: int = 20
):
    """
    Search sections using PostgreSQL Full-Text Search.
    Searches section_number, section_title, and bare_text.
    """
    # Use plainto_tsquery for natural language, or to_tsquery for specific syntax
    # We combine section_number, section_title, and bare_text for the search vector
    search_query = func.plainto_tsquery('english', q)
    
    # We'll use raw SQL for the FTS ranking to keep it simple and performant
    stmt = (
        select(Section, Act)
        .join(Act)
        .where(
            Section.is_active.is_(True),
            or_(
                func.to_tsvector('english', Section.section_title + " " + Section.bare_text + " " + Section.section_number).op('@@')(search_query),
                Section.section_number.ilike(f"%{q}%") # Fallback for exact section numbers
            )
        )
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return {
        "results": [
            {
                "id": s.id,
                "act_title": a.short_title,
                "section_number": s.section_number,
                "section_title": s.section_title,
                "plain_language": s.plain_language,
                "punishment_summary": s.punishment_summary,
                "is_bailable": s.is_bailable,
                "is_cognizable": s.is_cognizable,
                "relevant_court": s.relevant_court,
            }
            for s, a in rows
        ],
        "count": len(rows)
    }


@router.get("/")
async def list_sections(
    act_id: int | None = None,
    category: str | None = None,
    state: str | None = None,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Section, Act).join(Act).where(Section.is_active.is_(True))
    if act_id:
        query = query.where(Section.act_id == act_id)
    if state:
        query = query.where(Act.state == state)
    if category:
        try:
            cat = LawCategory(category)
        except ValueError as e:
            raise HTTPException(400, "Invalid category") from e
        query = query.where(Act.category == cat)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    return {
        "sections": [
            {
                "id": s.id,
                "act_title": a.short_title,
                "section_number": s.section_number,
                "section_title": s.section_title,
                "plain_language": s.plain_language,
                "punishment_summary": s.punishment_summary,
                "is_bailable": s.is_bailable,
                "is_cognizable": s.is_cognizable,
                "relevant_court": s.relevant_court,
            }
            for s, a in rows
        ],
        "count": len(rows),
    }


@router.get("/acts/list")
async def list_acts(
    state: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Registered before /{section_id} so `/sections/acts/list` resolves correctly."""
    stmt = (
        select(
            Act.id,
            Act.short_title,
            Act.year,
            Act.category,
            Act.act_type,
            Act.state,
            func.count(Section.id).label("section_count"),
        )
        .outerjoin(Section, Section.act_id == Act.id)
    )
    
    if state:
        stmt = stmt.where(Act.state == state)
        
    stmt = stmt.group_by(Act.id, Act.short_title, Act.year, Act.category, Act.act_type, Act.state).order_by(Act.id)
    
    result = await db.execute(stmt)
    rows = result.mappings().all()

    # Deduplicate by short_title (keep lowest id) when legacy seeds created duplicates
    seen_titles: dict[str, dict] = {}
    for r in rows:
        title = r["short_title"]
        if title not in seen_titles or r["id"] < seen_titles[title]["id"]:
            seen_titles[title] = dict(r)

    acts_out = sorted(seen_titles.values(), key=lambda x: x["id"])
    return {
        "acts": [
            {
                "id": r["id"],
                "short_title": r["short_title"],
                "year": r["year"],
                "category": r["category"].value,
                "act_type": r["act_type"].value,
                "state": r["state"],
                "section_count": r["section_count"],
            }
            for r in acts_out
        ]
    }


@router.get("/{section_id}")
async def get_section(section_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Section, Act)
        .join(Act)
        .where(Section.id == section_id, Section.is_active.is_(True))
    )
    row = result.first()
    if not row:
        raise HTTPException(404, "Section not found")

    s, a = row
    return {
        "id": s.id,
        "act_title": a.short_title,
        "act_year": a.year,
        "category": a.category.value,
        "section_number": s.section_number,
        "section_title": s.section_title,
        "bare_text": s.bare_text,
        "plain_language": s.plain_language,
        "is_bailable": s.is_bailable,
        "is_cognizable": s.is_cognizable,
        "is_compoundable": s.is_compoundable,
        "punishment_summary": s.punishment_summary,
        "max_punishment": s.max_punishment,
        "min_punishment": s.min_punishment,
        "fine_amount": s.fine_amount,
        "relevant_court": s.relevant_court,
        "limitation_period": s.limitation_period,
    }

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.analytics import QueryLog
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns high-level stats for the admin dashboard.
    """
    # Total queries
    total_result = await db.execute(select(func.count(QueryLog.id)))
    total_queries = total_result.scalar() or 0
    
    # Category distribution
    cat_result = await db.execute(
        select(QueryLog.category, func.count(QueryLog.id))
        .group_by(QueryLog.category)
        .order_by(desc(func.count(QueryLog.id)))
    )
    categories = {row[0] or "other": row[1] for row in cat_result.all()}
    
    # Language distribution
    lang_result = await db.execute(
        select(QueryLog.lang, func.count(QueryLog.id))
        .group_by(QueryLog.lang)
    )
    languages = {row[0]: row[1] for row in lang_result.all()}
    
    # Recent queries
    recent_result = await db.execute(
        select(QueryLog.query_text, QueryLog.created_at, QueryLog.category)
        .order_by(desc(QueryLog.created_at))
        .limit(10)
    )
    recent = [{"query": row[0], "time": row[1], "category": row[2]} for row in recent_result.all()]
    
    return {
        "total_queries": total_queries,
        "categories": categories,
        "languages": languages,
        "recent_queries": recent
    }

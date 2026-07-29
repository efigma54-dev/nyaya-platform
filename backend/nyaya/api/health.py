from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.core.database import get_db
from nyaya.db.repositories.crud import IPCBNSMappingRepository, SectionRepository, ActRepository
from nyaya.evaluation import count_questions
from nyaya.schemas import HealthStatus
from nyaya.services.qdrant_client import get_qdrant
from nyaya.services.redis_client import ping_sync

router = APIRouter(tags=["health"])


def _pg_ok() -> bool:
    return True


@router.get("/health", response_model=HealthStatus)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    acts = ActRepository(db)
    secs = SectionRepository(db)
    maps = IPCBNSMappingRepository(db)
    q_ok = "ok"
    try:
        client = get_qdrant()
        client.get_collections()
    except Exception:
        q_ok = "unhealthy"
    r_ok = "ok" if ping_sync() else "unhealthy"
    pg = "ok" if _pg_ok() else "unhealthy"
    return {
        "status": "ok" if all(x == "ok" for x in (q_ok, r_ok, pg)) else "degraded",
        "app_env": "development",
        "postgres": pg,
        "qdrant": q_ok,
        "redis": r_ok,
        "sections_count": await secs.count(),
        "acts_count": await acts.count(),
        "mappings_count": await maps.count(),
        "questions_count": await count_questions(db),
        "timestamp": datetime.utcnow(),
    }

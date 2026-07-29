from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nyaya.db.models.schema import Act, IPCBNSMapping, KGRelation, Section


class ActRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: dict[str, Any]) -> Act:
        obj = Act(**payload)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def get(self, act_id: int) -> Optional[Act]:
        return await self.db.get(Act, act_id)

    async def list_all(self, limit: int = 500, offset: int = 0) -> list[Act]:
        stmt = select(Act).order_by(Act.year.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(self) -> int:
        res = await self.db.execute(select(func.count(Act.id)))
        return int(res.scalar_one())

    async def by_short_title(self, title: str) -> Optional[Act]:
        stmt = select(Act).where(Act.short_title.ilike(title))
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class SectionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: dict[str, Any]) -> Section:
        obj = Section(**payload)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def get(self, section_id: int) -> Optional[Section]:
        stmt = select(Section).options(joinedload(Section.act)).where(Section.id == section_id)
        res = await self.db.execute(stmt)
        return res.unique().scalar_one_or_none()

    async def count(self) -> int:
        res = await self.db.execute(select(func.count(Section.id)))
        return int(res.scalar_one())

    async def list_by_act(self, act_id: int) -> list[Section]:
        stmt = (
            select(Section)
            .options(joinedload(Section.act))
            .where(Section.act_id == act_id)
            .order_by(Section.chapter.nullsfirst(), Section.section_number.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all())

    async def list_all(self, limit: int = 5000) -> list[Section]:
        stmt = select(Section).options(joinedload(Section.act)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all())

    async def list_by_ids(self, section_ids: Sequence[int]) -> list[Section]:
        if not section_ids:
            return []
        stmt = (
            select(Section)
            .options(joinedload(Section.act))
            .where(Section.id.in_(list(section_ids)))
        )
        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all())

    async def search_text(self, q: str, limit: int = 100) -> list[Section]:
        if not q.strip():
            return []
        like = f"%{q}%"
        stmt = (
            select(Section)
            .options(joinedload(Section.act))
            .where(
                or_(
                    Section.title.ilike(like),
                    Section.bare_text.ilike(like),
                    Section.plain_language.ilike(like),
                    Section.section_number.ilike(like),
                )
            )
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all())

    async def by_act_and_number(self, act_id: int, section_number: str) -> Optional[Section]:
        stmt = (
            select(Section)
            .options(joinedload(Section.act))
            .where(Section.act_id == act_id, Section.section_number == section_number)
        )
        res = await self.db.execute(stmt)
        return res.unique().scalar_one_or_none()


class IPCBNSMappingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: dict[str, Any]) -> IPCBNSMapping:
        obj = IPCBNSMapping(**payload)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def count(self) -> int:
        res = await self.db.execute(select(func.count(IPCBNSMapping.id)))
        return int(res.scalar_one())

    async def for_section(self, section_id: int) -> list[IPCBNSMapping]:
        stmt = (
            select(IPCBNSMapping)
            .options(
                joinedload(IPCBNSMapping.source_section).joinedload(Section.act),
                joinedload(IPCBNSMapping.target_section).joinedload(Section.act),
            )
            .where(
                or_(
                    IPCBNSMapping.source_section_id == section_id,
                    IPCBNSMapping.target_section_id == section_id,
                )
            )
        )
        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all())

    async def list_all(self) -> list[IPCBNSMapping]:
        stmt = select(IPCBNSMapping).options(
            joinedload(IPCBNSMapping.source_section).joinedload(Section.act),
            joinedload(IPCBNSMapping.target_section).joinedload(Section.act),
        )
        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all())


class KGRelationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: dict[str, Any]) -> KGRelation:
        obj = KGRelation(**payload)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def count(self) -> int:
        res = await self.db.execute(select(func.count(KGRelation.id)))
        return int(res.scalar_one())

    async def neighbors(
        self, section_id: int, depth: int = 1
    ) -> tuple[set[int], list[KGRelation]]:
        visited: set[int] = {section_id}
        edges: list[KGRelation] = []
        frontier: set[int] = {section_id}
        for _ in range(max(1, depth)):
            if not frontier:
                break
            stmt = (
                select(KGRelation)
                .options(
                    joinedload(KGRelation.source_section).joinedload(Section.act),
                    joinedload(KGRelation.target_section).joinedload(Section.act),
                )
                .where(
                    or_(
                        KGRelation.source_section_id.in_(list(frontier)),
                        KGRelation.target_section_id.in_(list(frontier)),
                    )
                )
            )
            res = await self.db.execute(stmt)
            new_edges = list(res.unique().scalars().all())
            edges.extend(new_edges)
            next_frontier: set[int] = set()
            for e in new_edges:
                if e.source_section_id not in visited:
                    next_frontier.add(e.source_section_id)
                if e.target_section_id not in visited:
                    next_frontier.add(e.target_section_id)
            visited.update(next_frontier)
            frontier = next_frontier
        return visited, edges

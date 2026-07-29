from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.db.models.schema import KGRelationType
from nyaya.db.repositories.crud import KGRelationRepository, SectionRepository
from nyaya.schemas import KGRelationOut, KGSubgraph, SectionOutWithAct


def _section_out(s) -> SectionOutWithAct:
    act = getattr(s, "act", None)
    data = {
        **{col.name: getattr(s, col.name) for col in type(s).__table__.columns},
        "act_short_title": getattr(act, "short_title", None),
        "act_year": getattr(act, "year", None),
    }
    return SectionOutWithAct.model_validate(data)


class KnowledgeGraphService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.sections = SectionRepository(db)
        self.relations = KGRelationRepository(db)

    async def subgraph(self, section_id: int, depth: int = 2) -> KGSubgraph:
        visited, edges = await self.relations.neighbors(section_id, depth=depth)
        nodes_objs = await self.sections.list_by_ids(list(visited))
        edge_outs = [
            KGRelationOut.model_validate(
                {col.name: getattr(e, col.name) for col in type(e).__table__.columns}
            )
            for e in edges
        ]
        return KGSubgraph(nodes=[_section_out(s) for s in nodes_objs], edges=edge_outs)

    async def add_relation(
        self, source_id: int, target_id: int, rel_type: KGRelationType, weight: float = 0.8, evidence: str | None = None
    ):
        payload = {
            "source_section_id": int(source_id),
            "target_section_id": int(target_id),
            "relation_type": rel_type,
            "weight": float(weight),
            "evidence": evidence,
        }
        return await self.relations.create(payload)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.core.database import get_db
from nyaya.db.models.schema import KGRelationType
from nyaya.db.repositories.crud import (
    ActRepository,
    IPCBNSMappingRepository,
    KGRelationRepository,
    SectionRepository,
)
from nyaya.schemas import (
    ActCreate,
    ActOut,
    IPCBNSMappingCreate,
    IPCBNSMappingOut,
    IPCBNSCompare,
    KGRelationCreate,
    KGRelationOut,
    KGSubgraph,
    SectionCreate,
    SectionOut,
    SectionOutWithAct,
)
from nyaya.search.dense_index import delete_section, upsert_section
from nyaya.search.kg_service import KnowledgeGraphService

router = APIRouter(prefix="/corpus", tags=["corpus"])


def _sec_out_full(s) -> SectionOutWithAct:
    act = getattr(s, "act", None)
    data = {col.name: getattr(s, col.name) for col in type(s).__table__.columns}
    data["act_short_title"] = getattr(act, "short_title", None)
    data["act_year"] = getattr(act, "year", None)
    return SectionOutWithAct.model_validate(data)


@router.get("/acts", response_model=list[ActOut])
async def list_acts(db: AsyncSession = Depends(get_db)):
    acts = ActRepository(db)
    return await acts.list_all()


@router.post("/acts", response_model=ActOut, status_code=status.HTTP_201_CREATED)
async def create_act(payload: ActCreate, db: AsyncSession = Depends(get_db)):
    acts = ActRepository(db)
    existing = await acts.by_short_title(payload.short_title)
    if existing is not None:
        raise HTTPException(409, "ACT_SHORT_TITLE_EXISTS")
    return await acts.create(payload.model_dump(exclude_unset=True))


@router.get("/acts/{act_id}/sections", response_model=list[SectionOutWithAct])
async def list_sections_for_act(act_id: int, db: AsyncSession = Depends(get_db)):
    acts = ActRepository(db)
    if await acts.get(act_id) is None:
        raise HTTPException(404, "ACT_NOT_FOUND")
    secs = SectionRepository(db)
    out = await secs.list_by_act(act_id)
    return [_sec_out_full(s) for s in out]


@router.get("/sections/{section_id}", response_model=SectionOutWithAct)
async def get_section(section_id: int, db: AsyncSession = Depends(get_db)):
    secs = SectionRepository(db)
    s = await secs.get(section_id)
    if s is None:
        raise HTTPException(404, "SECTION_NOT_FOUND")
    return _sec_out_full(s)


@router.post("/sections", response_model=SectionOut, status_code=status.HTTP_201_CREATED)
async def create_section(payload: SectionCreate, db: AsyncSession = Depends(get_db)):
    acts = ActRepository(db)
    if await acts.get(payload.act_id) is None:
        raise HTTPException(404, "ACT_NOT_FOUND")
    secs = SectionRepository(db)
    existing = await secs.by_act_and_number(payload.act_id, payload.section_number)
    if existing is not None:
        raise HTTPException(409, "SECTION_NUMBER_EXISTS_FOR_ACT")
    data = payload.model_dump(exclude_unset=True)
    obj = await secs.create(data)
    try:
        upsert_section(obj.id, obj.title, list(obj.keywords or []), obj.bare_text, obj.plain_language)
    except Exception:
        pass
    return obj


@router.get("/sections/{section_id}/ipc-bns", response_model=list[IPCBNSMappingOut])
async def list_ipc_bns_for_section(section_id: int, db: AsyncSession = Depends(get_db)):
    repo = IPCBNSMappingRepository(db)
    return [
        IPCBNSMappingOut.model_validate(
            {col.name: getattr(m, col.name) for col in type(m).__table__.columns}
        )
        for m in await repo.for_section(section_id)
    ]


@router.post("/ipc-bns", response_model=IPCBNSMappingOut, status_code=status.HTTP_201_CREATED)
async def create_ipc_bns_mapping(payload: IPCBNSMappingCreate, db: AsyncSession = Depends(get_db)):
    secs = SectionRepository(db)
    src = await secs.get(payload.source_section_id)
    tgt = await secs.get(payload.target_section_id)
    if src is None or tgt is None:
        raise HTTPException(404, "SECTION_NOT_FOUND")
    repo = IPCBNSMappingRepository(db)
    obj = await repo.create(payload.model_dump(exclude_unset=True))
    return IPCBNSMappingOut.model_validate(
        {col.name: getattr(obj, col.name) for col in type(obj).__table__.columns}
    )


@router.get("/ipc-bns/compare/{section_id}", response_model=list[IPCBNSCompare])
async def ipc_bns_compare(section_id: int, db: AsyncSession = Depends(get_db)):
    repo = IPCBNSMappingRepository(db)
    secs = SectionRepository(db)
    mappings = await repo.for_section(section_id)
    out: list[IPCBNSCompare] = []
    for m in mappings:
        src = await secs.get(m.source_section_id)
        tgt = await secs.get(m.target_section_id)
        if src is None or tgt is None:
            continue
        out.append(
            IPCBNSCompare(
                left=_sec_out_full(src),
                right=_sec_out_full(tgt),
                mapping=IPCBNSMappingOut.model_validate(
                    {col.name: getattr(m, col.name) for col in type(m).__table__.columns}
                ),
                plain_translation=None,
            )
        )
    return out


@router.post("/kg/relations", response_model=KGRelationOut, status_code=status.HTTP_201_CREATED)
async def create_kg_relation(payload: KGRelationCreate, db: AsyncSession = Depends(get_db)):
    secs = SectionRepository(db)
    if (await secs.get(payload.source_section_id)) is None or (await secs.get(payload.target_section_id)) is None:
        raise HTTPException(404, "SECTION_NOT_FOUND")
    repo = KGRelationRepository(db)
    obj = await repo.create(payload.model_dump(exclude_unset=True))
    return KGRelationOut.model_validate(
        {col.name: getattr(obj, col.name) for col in type(obj).__table__.columns}
    )


@router.get("/kg/subgraph/{section_id}", response_model=KGSubgraph)
async def kg_subgraph(
    section_id: int,
    depth: int = Query(default=2, ge=1, le=4),
    db: AsyncSession = Depends(get_db),
):
    svc = KnowledgeGraphService(db)
    secs = SectionRepository(db)
    if await secs.get(section_id) is None:
        raise HTTPException(404, "SECTION_NOT_FOUND")
    return await svc.subgraph(section_id, depth=depth)

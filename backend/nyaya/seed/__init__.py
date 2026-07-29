from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.db.models.schema import BenchmarkQuestion
from nyaya.db.repositories.crud import (
    ActRepository,
    IPCBNSMappingRepository,
    KGRelationRepository,
    SectionRepository,
)
from nyaya.db.models.schema import KGRelationType
from nyaya.search.dense_index import upsert_many
from nyaya.seed.acts import ACTS
from nyaya.seed.benchmark_questions import BENCHMARK_QUESTIONS
from nyaya.seed.ipc_bns_mappings import IPC_BNS_MAPPINGS
from nyaya.seed.kg_relations import KG_EDGES
from nyaya.seed.sections import SECTIONS


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def load_acts(db: AsyncSession) -> dict[str, int]:
    acts_repo = ActRepository(db)
    out: dict[str, int] = {}
    for a in ACTS:
        existing = await acts_repo.by_short_title(a["short_title"])
        if existing is None:
            obj = await acts_repo.create(dict(a))
            out[a["short_title"]] = obj.id
        else:
            out[a["short_title"]] = existing.id
    return out


async def load_sections(db: AsyncSession, act_ids: dict[str, int]) -> dict[tuple[str, str], int]:
    sec_repo = SectionRepository(db)
    out: dict[tuple[str, str], int] = {}
    qdrant_batch: list[dict[str, Any]] = []
    for s in SECTIONS:
        act_short = s.pop("act_short_title")
        if act_short not in act_ids:
            continue
        act_id = act_ids[act_short]
        sn = s["section_number"]
        existing = await sec_repo.by_act_and_number(act_id, sn)
        if "checksum_sha256" not in s or not s["checksum_sha256"]:
            s["checksum_sha256"] = _sha256(
                f"{act_short}|{sn}|{s.get('title','')}|{s.get('bare_text','')}"
            )
        if existing is None:
            s_with_act = {**s, "act_id": act_id}
            obj = await sec_repo.create(s_with_act)
            out[(act_short, sn)] = obj.id
            qdrant_batch.append(
                {
                    "section_id": obj.id,
                    "title": obj.title,
                    "keywords": list(obj.keywords or []),
                    "bare_text": obj.bare_text,
                    "plain_language": obj.plain_language,
                }
            )
        else:
            out[(act_short, sn)] = existing.id
            if qdrant_batch:
                upsert_many(qdrant_batch)
                qdrant_batch = []
    if qdrant_batch:
        try:
            upsert_many(qdrant_batch)
        except Exception:
            pass
    return out


async def load_ipc_bns_mappings(db: AsyncSession, section_ids: dict[tuple[str, str], int]) -> int:
    repo = IPCBNSMappingRepository(db)
    created = 0
    for src_act, src_sn, tgt_act, tgt_sn in IPC_BNS_MAPPINGS:
        src = section_ids.get((src_act, src_sn))
        tgt = section_ids.get((tgt_act, tgt_sn))
        if src is None or tgt is None:
            continue
        existing = await repo.for_section(src)
        found = any(m.target_section_id == tgt for m in existing)
        if found:
            continue
        payload = {
            "source_section_id": src,
            "target_section_id": tgt,
            "mapping_kind": "ipc_to_bns",
            "equivalence": "exact",
            "notes": f"Maps {src_act} Sec {src_sn} → {tgt_act} Sec {tgt_sn}",
        }
        await repo.create(payload)
        reverse_exists = any(m.source_section_id == tgt for m in await repo.for_section(tgt))
        if not reverse_exists:
            await repo.create(
                {
                    "source_section_id": tgt,
                    "target_section_id": src,
                    "mapping_kind": "bns_to_ipc",
                    "equivalence": "exact",
                    "notes": f"Maps {tgt_act} Sec {tgt_sn} → {src_act} Sec {src_sn}",
                }
            )
        created += 1
    return created


async def load_kg_relations(db: AsyncSession, section_ids: dict[tuple[str, str], int]) -> int:
    repo = KGRelationRepository(db)
    created = 0
    for src_act, src_sn, tgt_act, tgt_sn, rtype, weight, evidence in KG_EDGES:
        src = section_ids.get((src_act, src_sn))
        tgt = section_ids.get((tgt_act, tgt_sn))
        if src is None or tgt is None:
            continue
        _, edges = await repo.neighbors(src, depth=1)
        found = any(
            e.target_section_id == tgt
            and (e.relation_type.value if hasattr(e.relation_type, "value") else e.relation_type) == rtype
            for e in edges
        )
        if found:
            continue
        rt = KGRelationType(rtype) if isinstance(rtype, str) else rtype
        await repo.create(
            {
                "source_section_id": src,
                "target_section_id": tgt,
                "relation_type": rt,
                "weight": float(weight),
                "evidence": evidence,
            }
        )
        created += 1
    return created


async def load_benchmark_questions(db: AsyncSession, section_ids: dict[tuple[str, str], int]) -> int:
    created = 0
    for qtype, difficulty, query, rels, ideal, tags in BENCHMARK_QUESTIONS:
        relevant_ids: list[int] = []
        for r in rels:
            if ":" in r:
                act_short, sn = r.rsplit(":", 1)
                sid = section_ids.get((act_short, sn))
                if sid is not None:
                    relevant_ids.append(int(sid))
        obj = BenchmarkQuestion(
            query=query,
            query_type=qtype,
            difficulty=difficulty,
            relevant_section_ids=relevant_ids,
            ideal_answer=ideal,
            tags=list(tags),
        )
        db.add(obj)
        created += 1
    await db.flush()
    return created


async def seed_all(db: AsyncSession, baseline: bool = True) -> dict[str, int]:
    from nyaya.services.qdrant_client import ensure_collection

    ensure_collection()
    act_ids = await load_acts(db)
    section_ids = await load_sections(db, act_ids)
    mappings = await load_ipc_bns_mappings(db, section_ids)
    edges = await load_kg_relations(db, section_ids)
    questions = await load_benchmark_questions(db, section_ids) if baseline else 0
    return {
        "acts": len(act_ids),
        "sections": len(section_ids),
        "ipc_bns_mappings": mappings,
        "kg_edges": edges,
        "benchmark_questions": questions,
    }

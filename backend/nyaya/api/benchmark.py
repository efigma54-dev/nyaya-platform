from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.core.database import get_db
from nyaya.db.repositories.crud import SectionRepository
from nyaya.evaluation import EvalMetrics, run_benchmark
from nyaya.schemas import BenchmarkMetrics
from nyaya.search.bm25_index import BM25Corpus
from nyaya.search.dense_index import dense_search
from nyaya.search.hybrid import apply_rerank, combine_scores, validate_citations

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/run", response_model=BenchmarkMetrics)
async def run_benchmark_endpoint(
    run_name: str = Query(default="adhoc"),
    sample: int | None = Query(default=None, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
) -> BenchmarkMetrics:
    secs = SectionRepository(db)
    all_sections = await secs.list_all(limit=100000)
    bm25 = BM25Corpus.build(all_sections)
    sections_map = {s.id: s for s in all_sections}

    def retriever(q: str) -> list[int]:
        if not q.strip():
            return []
        b_hits = bm25.query(q, top_k=50)
        d_hits = dense_search(q, top_k=50)
        combined = combine_scores(b_hits, d_hits)
        for c in combined.values():
            c.section_obj = sections_map.get(c.section_id)
        ordered = apply_rerank(q, combined, top_k=100)
        return [c.section_id for c in ordered]

    def validator(q: str, ids: list[int]) -> dict[int, bool]:
        from nyaya.search.hybrid import HybridCandidate

        cands = [
            (lambda s: HybridCandidate(section_id=s.id, section_obj=s))(sections_map[i])
            for i in ids if i in sections_map
        ]
        out: dict[int, bool] = {}
        for _, ok, _, _ in validate_citations(q, cands):
            # we need to pair properly; re-run via helper below
            pass
        # simpler: re-run validate with proper pairs
        cands2 = [
            (lambda s: HybridCandidate(section_id=s.id, section_obj=s, title=getattr(s, "title", ""),
                                        bare_text=getattr(s, "bare_text", "")))(sections_map[i])
            for i in ids if i in sections_map
        ]
        v2 = validate_citations(q, cands2)
        for cand, ok, _, _ in v2:
            out[cand.section_id] = ok
        return out

    metrics: EvalMetrics = await run_benchmark(db, run_name=run_name, retriever=retriever,
                                               citation_validator=validator, sample=sample)
    return BenchmarkMetrics(**{k: v for k, v in vars(metrics).items()})

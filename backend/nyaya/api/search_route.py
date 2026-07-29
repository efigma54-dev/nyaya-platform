from __future__ import annotations

import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.core.database import get_db
from nyaya.db.repositories.crud import SectionRepository
from nyaya.schemas import SearchQuery, SearchResponse, SearchResult
from nyaya.search.bm25_index import BM25Corpus
from nyaya.search.dense_index import dense_search
from nyaya.search.hybrid import apply_rerank, combine_scores, finalize_results, validate_citations

router = APIRouter(prefix="/search", tags=["search"])

_bm25_global: BM25Corpus | None = None


async def _get_bm25(db: AsyncSession) -> BM25Corpus:
    global _bm25_global
    if _bm25_global is None or len(_bm25_global) == 0:
        secs = SectionRepository(db)
        all_sections = await secs.list_all(limit=100000)
        _bm25_global = BM25Corpus.build(all_sections)
    return _bm25_global


def _reset_bm25_cache() -> None:
    global _bm25_global
    _bm25_global = None


@router.post("", response_model=SearchResponse)
@router.get("", response_model=SearchResponse)
async def hybrid_search(
    q: str = Query(default="", description="Query string"),
    top_k: int = Query(default=10, ge=1, le=100),
    rerank: bool = Query(default=True),
    include_bm25: bool = Query(default=True),
    include_dense: bool = Query(default=True),
    validate_citations: bool = Query(default=True),
    payload: SearchQuery | None = None,
    db: AsyncSession = Depends(get_db),
):
    if payload is not None:
        q = payload.q or q
        top_k = payload.top_k or top_k
        include_bm25 = payload.include_bm25
        include_dense = payload.include_dense
        rerank = payload.rerank
        validate_citations = payload.validate_citations
    t0 = time.perf_counter()
    bm25_hits: list[tuple[int, float]] = []
    dense_hits: list[tuple[int, float]] = []
    if include_bm25 and q.strip():
        bm25 = await _get_bm25(db)
        bm25_hits = bm25.query(q, top_k=500)
    if include_dense and q.strip():
        dense_hits = dense_search(q, top_k=500)
    combined = combine_scores(bm25_hits, dense_hits)
    secs = SectionRepository(db)
    id_set = list(combined.keys())
    sections_loaded = {s.id: s for s in await secs.list_by_ids(id_set)}
    for c in combined.values():
        c.section_obj = sections_loaded.get(c.section_id)
    ordered = list(combined.values())
    if rerank and q.strip():
        ordered = apply_rerank(q, combined, top_k=200)
    validated: list = []
    if validate_citations and q.strip():
        validated = validate_citations(q, ordered)
    results: list[SearchResult] = finalize_results(q, ordered, validated, limit=top_k)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return SearchResponse(query=q, total=len(results), latency_ms=latency_ms, results=results)

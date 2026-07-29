from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from nyaya.config.settings import get_settings
from nyaya.schemas import SearchResult
from nyaya.services.embeddings import cross_encoder_rerank

settings = get_settings()

_SENT_RE = re.compile(r"(?<=[।.!?])\s+")


@dataclass
class HybridCandidate:
    section_id: int
    bm25_score: Optional[float] = None
    dense_score: Optional[float] = None
    combined_score: float = 0.0
    section_obj: Optional[object] = None

    @property
    def bare_text(self) -> str:
        if self.section_obj is None:
            return ""
        return str(getattr(self.section_obj, "bare_text", "") or "")

    @property
    def title(self) -> str:
        if self.section_obj is None:
            return ""
        return str(getattr(self.section_obj, "title", "") or "")


def _minmax(values: list[float]) -> list[float]:
    if not values:
        return values
    lo = min(values)
    hi = max(values)
    if hi - lo < 1e-12:
        return [1.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def combine_scores(bm25_hits: list[tuple[int, float]], dense_hits: list[tuple[int, float]]) -> dict[int, HybridCandidate]:
    merged: dict[int, HybridCandidate] = {}
    if bm25_hits:
        ids, scores = zip(*bm25_hits)
        normed = _minmax(list(scores))
        for sid, sc in zip(ids, normed):
            merged[int(sid)] = HybridCandidate(section_id=int(sid), bm25_score=float(sc))
    if dense_hits:
        ids, scores = zip(*dense_hits)
        normed = _minmax(list(scores))
        for sid, sc in zip(ids, normed):
            sid = int(sid)
            if sid in merged:
                merged[sid].dense_score = float(sc)
            else:
                merged[sid] = HybridCandidate(section_id=sid, dense_score=float(sc))
    dw = settings.hybrid_dense_weight
    bw = settings.hybrid_bm25_weight
    for c in merged.values():
        b = c.bm25_score if c.bm25_score is not None else 0.0
        d = c.dense_score if c.dense_score is not None else 0.0
        c.combined_score = float(bw * b + dw * d)
    return merged


def apply_rerank(query: str, candidates: dict[int, HybridCandidate], top_k: int = 50) -> list[HybridCandidate]:
    ordered = sorted(candidates.values(), key=lambda c: c.combined_score, reverse=True)[:top_k]
    if not ordered:
        return []
    passages = []
    for c in ordered:
        t = c.title
        b = c.bare_text
        passages.append(f"{t}\n{b}" if (t and b) else (t or b or ""))
    ranked = cross_encoder_rerank(query, passages, top_k=len(ordered))
    idx_to_score: dict[int, float] = {i: s for i, s in ranked}
    for i, c in enumerate(ordered):
        c.combined_score = idx_to_score.get(i, c.combined_score * 0.5)
    ordered.sort(key=lambda c: c.combined_score, reverse=True)
    return ordered


def _snippets(query: str, text: str, k: int = 2, win: int = 40) -> list[str]:
    if not text or not query:
        return []
    sentences = [s.strip() for s in _SENT_RE.split(text) if s.strip()]
    if not sentences:
        return []
    ql = query.lower()
    scored = sorted(
        sentences, key=lambda s: SequenceMatcher(None, ql, s.lower()).ratio() + (0.3 if ql in s.lower() else 0.0), reverse=True
    )
    snippets = []
    for s in scored[:k]:
        snippet = s if len(s) <= win * 2 else s[:win] + " … " + s[-win:]
        snippets.append(snippet)
    return snippets


def validate_citations(
    query: str, candidates: list[HybridCandidate]
) -> list[tuple[HybridCandidate, bool, float, list[str]]]:
    threshold = settings.citation_validator_threshold
    out: list[tuple[HybridCandidate, bool, float, list[str]]] = []
    ql = query.lower()
    for c in candidates:
        text = f"{c.title} {c.bare_text}".lower()
        sim = SequenceMatcher(None, ql, text[:1200]).ratio()
        # bonus for keyword overlap
        qtoks = set(re.findall(r"[\w\u0900-\u097F]+", ql))
        ttoks = set(re.findall(r"[\w\u0900-\u097F]+", text))
        shared = len(qtoks & ttoks) / max(1, min(len(qtoks), 8))
        sim = min(1.0, sim + 0.15 * shared)
        snippets = _snippets(query, c.bare_text, k=2)
        out.append((c, sim >= threshold, float(sim), snippets))
        if not sim >= threshold:
            c.combined_score = c.combined_score * (1.0 - settings.hallucination_penalty)
    return out


def finalize_results(
    query: str,
    candidates: list[HybridCandidate],
    validated: list[tuple[HybridCandidate, bool, float, list[str]]],
    limit: int = 10,
) -> list[SearchResult]:
    lookup: dict[int, tuple[bool, float, list[str]]] = {}
    for c, ok, sim, snips in validated:
        lookup[c.section_id] = (ok, sim, snips)
    ordered = sorted(candidates, key=lambda c: c.combined_score, reverse=True)
    results: list[SearchResult] = []
    for i, c in enumerate(ordered[:limit]):
        ok, sim, snips = lookup.get(c.section_id, (False, 0.0, []))
        section_blob = None
        if c.section_obj is not None:
            try:
                from nyaya.schemas import SectionOutWithAct

                act = getattr(c.section_obj, "act", None)
                data = {
                    **{col.name: getattr(c.section_obj, col.name) for col in type(c.section_obj).__table__.columns},
                    "act_short_title": getattr(act, "short_title", None),
                    "act_year": getattr(act, "year", None),
                }
                section_blob = SectionOutWithAct.model_validate(data)
            except Exception:
                section_blob = None
        results.append(
            SearchResult(
                section_id=c.section_id,
                rank=i + 1,
                bm25_score=c.bm25_score,
                dense_score=c.dense_score,
                rerank_score=c.combined_score,
                combined_score=c.combined_score,
                citation_validated=ok,
                citation_similarity=sim,
                snippets=snips,
                section=section_blob,
            )
        )
    return results

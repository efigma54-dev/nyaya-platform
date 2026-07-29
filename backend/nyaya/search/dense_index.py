from __future__ import annotations

from typing import Optional

import numpy as np
from qdrant_client import models

from nyaya.config.settings import get_settings
from nyaya.services.embeddings import encode_query, encode_section
from nyaya.services.qdrant_client import ensure_collection, get_qdrant

settings = get_settings()


def upsert_section(section_id: int, title: str, keywords: list[str], bare_text: str,
                   plain_language: Optional[str], payload_extra: Optional[dict] = None) -> None:
    ensure_collection()
    vector = encode_section(section_id, title, keywords, bare_text, plain_language)
    payload = {"section_id": int(section_id), "title": title, "keywords": list(keywords)}
    if payload_extra:
        payload.update(payload_extra)
    get_qdrant().upsert(
        collection_name=settings.qdrant_collection,
        points=[
            models.PointStruct(
                id=int(section_id),
                vector=vector.tolist(),
                payload=payload,
            )
        ],
    )


def upsert_many(sections: list[dict]) -> None:
    if not sections:
        return
    ensure_collection()
    points = []
    vecs = [
        encode_section(
            int(s["section_id"]),
            s.get("title", ""),
            list(s.get("keywords", []) or []),
            s.get("bare_text", ""),
            s.get("plain_language"),
        )
        for s in sections
    ]
    for s, v in zip(sections, vecs):
        points.append(
            models.PointStruct(
                id=int(s["section_id"]),
                vector=v.tolist(),
                payload={"section_id": int(s["section_id"]), "title": s.get("title", ""),
                         "keywords": list(s.get("keywords", []) or [])},
            )
        )
    get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points)


def delete_section(section_id: int) -> None:
    try:
        get_qdrant().delete(
            collection_name=settings.qdrant_collection,
            points_selector=models.PointIdsList(points=[int(section_id)]),
        )
    except Exception:
        pass


def dense_search(query: str, top_k: int = 50, act_filter: Optional[list[int]] = None) -> list[tuple[int, float]]:
    ensure_collection()
    qvec = encode_query(query)
    qf: Optional[models.Filter] = None
    if act_filter:
        qf = models.Filter(
            must=[
                models.FieldCondition(
                    key="act_id",
                    match=models.MatchAny(any=list(act_filter)),
                )
            ]
        )
    hits = get_qdrant().search(
        collection_name=settings.qdrant_collection,
        query_vector=qvec.tolist(),
        limit=max(1, top_k),
        with_payload=False,
        query_filter=qf,
    )
    out: list[tuple[int, float]] = []
    for h in hits:
        sid = int(h.id)
        score = float(h.score if h.score is not None else 0.0)
        out.append((sid, score))
    return out


def dense_vector(section_id: int) -> Optional[np.ndarray]:
    ensure_collection()
    res = get_qdrant().retrieve(
        collection_name=settings.qdrant_collection, ids=[int(section_id)], with_vectors=True, with_payload=False
    )
    if not res:
        return None
    v = res[0].vector
    if v is None:
        return None
    return np.asarray(v, dtype=np.float32)

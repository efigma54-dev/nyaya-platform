from __future__ import annotations

import hashlib
from functools import lru_cache
from typing import Iterable, Optional

import numpy as np

from nyaya.config.settings import get_settings

settings = get_settings()

_st_model = None
_ce_model = None
_DIM = settings.qdrant_vector_size


def _get_st():
    global _st_model
    if _st_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _st_model = SentenceTransformer(settings.embedding_model, device="cpu")
        except Exception as exc:  # pragma: no cover - hardware/network dependent
            raise RuntimeError(f"Failed to load embedding model {settings.embedding_model}: {exc}") from exc
    return _st_model


def _get_ce():
    global _ce_model
    if _ce_model is None:
        try:
            from sentence_transformers import CrossEncoder

            _ce_model = CrossEncoder(settings.cross_encoder_model, device="cpu")
        except Exception as exc:  # pragma: no cover - hardware/network dependent
            raise RuntimeError(f"Failed to load cross-encoder {settings.cross_encoder_model}: {exc}") from exc
    return _ce_model


def deterministic_fallback(texts: Iterable[str]) -> np.ndarray:
    out = []
    for t in texts:
        h = hashlib.sha256(t.encode("utf-8")).digest()
        ints = np.frombuffer(h, dtype=np.uint8).astype(np.float32) / 255.0
        vec = np.zeros(_DIM, dtype=np.float32)
        for i in range(min(len(ints), _DIM)):
            vec[i] = ints[i]
        rng = np.random.default_rng(seed=int.from_bytes(h[:8], "big"))
        extra = rng.random(max(0, _DIM - len(ints)), dtype=np.float32)
        vec[-len(extra):] = extra
        norm = np.linalg.norm(vec) + 1e-12
        out.append(vec / norm)
    return np.vstack(out).astype(np.float32)


try:
    _get_st()
    _embed_ok = True
except Exception:
    _embed_ok = False


def encode_texts(texts: list[str], batch_size: int = 16, use_st: bool = True) -> np.ndarray:
    if use_st and _embed_ok:
        try:
            model = _get_st()
            vecs = model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return np.asarray(vecs, dtype=np.float32)
        except Exception:
            pass
    return deterministic_fallback(texts)


def encode_query(query: str) -> np.ndarray:
    if not query.strip():
        return np.zeros(_DIM, dtype=np.float32)
    vecs = encode_texts([f"Represent this sentence for searching relevant passages: {query}"])
    return vecs[0]


def encode_section(section_id: int, title: str, keywords: list[str], bare_text: str, plain: Optional[str]) -> np.ndarray:
    text = f"Title: {title}\nKeywords: {', '.join(keywords)}\nBare: {bare_text}"
    if plain:
        text += f"\nPlain: {plain}"
    return encode_texts([text])[0]


def cross_encoder_rerank(query: str, passages: list[str], top_k: int = 50) -> list[tuple[int, float]]:
    if not passages:
        return []
    pairs = [[query, p] for p in passages]
    try:
        ce = _get_ce()
        scores = ce.predict(pairs, batch_size=32, convert_to_numpy=True, show_progress_bar=False)
    except Exception:
        from difflib import SequenceMatcher

        scores = np.array([SequenceMatcher(None, query.lower(), p.lower()).ratio() for p in passages], dtype=np.float32)
    ranked = sorted(enumerate(np.asarray(scores, dtype=np.float32).tolist()), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]

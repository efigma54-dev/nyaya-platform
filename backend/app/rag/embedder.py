# backend/app/rag/embedder.py
# Local embeddings: BAAI/bge-m3 via sentence-transformers (Hindi + English legal text)

from __future__ import annotations

import hashlib
import json
from functools import lru_cache

import numpy as np
import redis
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def get_redis_client() -> redis.Redis:
    """Reuse the sync Redis client for embedding cache lookups."""
    return redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load once, reuse forever. bge-m3 is multilingual.
    First run downloads the model (~2GB with PyTorch); HF cache speeds reruns.
    """
    print("🔄 Loading BAAI/bge-m3 (first run = download)...")
    model = SentenceTransformer("BAAI/bge-m3", trust_remote_code=True)
    print("✅ Embedding model loaded")
    return model


def _embedding_cache_key(text: str) -> str:
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    return f"embed:{digest}"


def embed_text(text: str) -> list[float]:
    cache_key = _embedding_cache_key(text)
    redis_client = get_redis_client()
    cached = redis_client.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            pass

    model = get_embedding_model()
    v = model.encode(text, normalize_embeddings=True)
    vector = _to_list(v)
    redis_client.setex(cache_key, 86400, json.dumps(vector, ensure_ascii=False))
    return vector


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    arr = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    if isinstance(arr, np.ndarray) and arr.ndim == 2:
        return [row.tolist() for row in arr]
    return [_to_list(arr)]


def _to_list(v: np.ndarray | list) -> list[float]:
    if isinstance(v, np.ndarray):
        return v.reshape(-1).astype(float).tolist()
    return list(map(float, v))

# backend/app/rag/vector_store.py
# Qdrant collection for legal sections (sync client — scripts + API)

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

COLLECTION_NAME = "nyaya_sections"
VECTOR_SIZE = 1024  # bge-m3


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
        timeout=180,
    )


def ensure_collection() -> QdrantClient:
    """Create Qdrant collection if it doesn't exist."""
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Created Qdrant collection: {COLLECTION_NAME}")
    else:
        print(f"⏭  Collection already exists: {COLLECTION_NAME}")

    return client


def upsert_section(
    client: QdrantClient,
    section_id: int,
    vector: list[float],
    payload: dict,
) -> None:
    """Insert or update a single section vector."""
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=section_id,
                vector=vector,
                payload=payload,
            )
        ],
    )


def insert_sections_to_qdrant(
    client: QdrantClient,
    sections: list[dict],
    vectors: list[list[float]],
) -> str | list[str]:
    """Insert or update one or more sections in Qdrant."""
    points = []
    ids: list[str] = []
    for section, vector in zip(sections, vectors, strict=True):
        ids.append(str(section["id"]))
        points.append(
            PointStruct(
                id=section["id"],
                vector=vector,
                payload=section,
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return ids[0] if len(ids) == 1 else ids


def search_sections(
    query_vector: list[float],
    top_k: int = 5,
    act_category: str | None = None,
    act_categories: list[str] | None = None,
    act_id: int | None = None,
    state: str | None = None,
) -> list[dict]:
    """
    Semantic search with optional filters.
    act_category: single LawCategory value (legacy)
    act_categories: one or more categories (OR filter), e.g. ['family', 'criminal']
    act_id: filter to a specific act
    state: filter to a specific state (None = Central)
    """
    client = get_qdrant_client()

    categories = act_categories
    if categories is None and act_category:
        categories = [act_category]

    conditions: list[FieldCondition] = []
    if categories:
        if len(categories) == 1:
            conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchValue(value=categories[0]),
                )
            )
        else:
            conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchAny(any=categories),
                )
            )
    if act_id is not None:
        conditions.append(
            FieldCondition(
                key="act_id",
                match=MatchValue(value=act_id),
            )
        )
    if state:
        conditions.append(
            FieldCondition(
                key="state",
                match=MatchValue(value=state),
            )
        )

    query_filter = Filter(must=conditions) if conditions else None

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    )

    return [
        {
            "section_id": hit.id,
            "score": round(float(hit.score), 4),
            "payload": hit.payload or {},
        }
        for hit in results
    ]

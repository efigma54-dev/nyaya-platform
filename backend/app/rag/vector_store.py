# backend/app/rag/vector_store.py
# Qdrant collections for legal corpus (sections, judgments, rules, notifications)

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
    TextIndexParams,
    TokenizerType,
    Query,
)

from app.core.config import settings

# Collection names
COLLECTION_SECTIONS = "nyaya_sections"
COLLECTION_JUDGMENTS = "nyaya_judgments"
COLLECTION_RULES = "nyaya_rules"
COLLECTION_NOTIFICATIONS = "nyaya_notifications"

VECTOR_SIZE = 1024  # bge-m3


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
        timeout=180,
    )


def ensure_collection(collection_name: str, vector_size: int = VECTOR_SIZE) -> QdrantClient:
    """Create Qdrant collection if it doesn't exist, with keyword index for hybrid search."""
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]

    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        # Create keyword index for BM25
        client.create_payload_index(
            collection_name=collection_name,
            field_name="content",
            field_schema=TextIndexParams(
                type="text",
                tokenizer=TokenizerType.WORD,
                min_token_len=2,
                max_token_len=20,
            ),
        )
        print(f"✅ Created Qdrant collection: {collection_name} with keyword index")
    else:
        print(f"⏭  Collection already exists: {collection_name}")

    return client


def ensure_all_collections() -> QdrantClient:
    """Ensure all required collections exist."""
    client = ensure_collection(COLLECTION_SECTIONS)
    ensure_collection(COLLECTION_JUDGMENTS)
    ensure_collection(COLLECTION_RULES)
    ensure_collection(COLLECTION_NOTIFICATIONS)
    return client


def upsert_section(
    client: QdrantClient,
    section_id: int,
    vector: list[float],
    payload: dict,
) -> None:
    """Insert or update a single section vector."""
    client.upsert(
        collection_name=COLLECTION_SECTIONS,
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

    client.upsert(collection_name=COLLECTION_SECTIONS, points=points)
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
        collection_name=COLLECTION_SECTIONS,
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
            "type": "section",
        }
        for hit in results
    ]


def search_hybrid(
    query_vector: list[float],
    query_text: str,
    top_k: int = 5,
    act_categories: list[str] | None = None,
    state: str | None = None,
) -> list[dict]:
    """
    Hybrid search combining vector (semantic) and keyword (BM25) search.
    Searches across sections, judgments, rules, and notifications.
    """
    client = get_qdrant_client()
    all_results = []

    # Search sections
    conditions = []
    if act_categories:
        if len(act_categories) == 1:
            conditions.append(FieldCondition(key="category", match=MatchValue(value=act_categories[0])))
        else:
            conditions.append(FieldCondition(key="category", match=MatchAny(any=act_categories)))
    if state:
        conditions.append(FieldCondition(key="state", match=MatchValue(value=state)))
    section_filter = Filter(must=conditions) if conditions else None

    # 1. Vector search on sections (semantic)
    vector_results = client.search(
        collection_name=COLLECTION_SECTIONS,
        query_vector=query_vector,
        limit=top_k * 2,  # Retrieve more for later re-ranking
        query_filter=section_filter,
        with_payload=True,
    )
    vector_dict = {hit.id: hit.score for hit in vector_results}
    all_results.extend([
        {
            "id": hit.id,
            "score": round(float(hit.score), 4),
            "payload": hit.payload or {},
            "type": "section",
            "source": "vector"
        }
        for hit in vector_results
    ])

    # 2. Text/keyword search (BM25-style via Qdrant text index)
    if query_text and len(query_text.strip()) > 0:
        try:
            text_results = client.query(
                collection_name=COLLECTION_SECTIONS,
                query=Query(
                    text=query_text
                ),
                limit=top_k * 2,
                filter=section_filter,
                with_payload=True,
            )
            # Merge results, keeping max score for duplicates
            for hit in text_results:
                if hit.id not in vector_dict:
                    all_results.append({
                        "id": hit.id,
                        "score": round(float(hit.score), 4),
                        "payload": hit.payload or {},
                        "type": "section",
                        "source": "text"
                    })
                else:
                    # For duplicates, take the maximum score from either vector or text search
                    for res in all_results:
                        if res["id"] == hit.id:
                            res["score"] = max(res["score"], round(float(hit.score), 4))
                            res["source"] = "hybrid"
                            break
        except Exception as e:
            print(f"Text search failed (falling back to vector only): {e}")

    # Merge and rank results
    all_results.sort(key=lambda x: x["score"], reverse=True)
    # Deduplicate by id
    seen = set()
    unique_results = []
    for res in all_results:
        if res["id"] not in seen:
            seen.add(res["id"])
            unique_results.append(res)
            if len(unique_results) >= top_k:
                break
    return unique_results

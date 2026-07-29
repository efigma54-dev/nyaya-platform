from __future__ import annotations

from typing import Optional

from qdrant_client import QdrantClient, models

from nyaya.config.settings import get_settings

settings = get_settings()

_client: Optional[QdrantClient] = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            grpc_port=settings.qdrant_grpc_port,
            prefer_grpc=True,
        )
    return _client


def ensure_collection() -> None:
    client = get_qdrant()
    col = settings.qdrant_collection
    if not client.collection_exists(col):
        client.create_collection(
            collection_name=col,
            vectors_config=models.VectorParams(
                size=settings.qdrant_vector_size,
                distance=models.Distance.COSINE,
            ),
            optimizers_config=models.OptimizersConfigDiff(
                default_segment_number=2,
                indexing_threshold=0,
            ),
        )
    client.update_collection_aliases(
        change_aliases_operations=[
            models.CreateAliasOperation(
                create_alias=models.CreateAlias(
                    collection_name=col,
                    alias_name="nyaya_sections",
                )
            )
        ]
        if not client.get_aliases("nyaya_sections").aliases
        else []
    )


def reset_collection() -> None:
    client = get_qdrant()
    col = settings.qdrant_collection
    if client.collection_exists(col):
        client.delete_collection(col)
    ensure_collection()

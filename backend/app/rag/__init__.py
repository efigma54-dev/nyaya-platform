
from app.rag.embedder import embed_text, embed_batch
from app.rag.vector_store import (
    get_qdrant_client,
    ensure_all_collections,
    search_sections,
    search_hybrid,
    COLLECTION_SECTIONS,
)


def get_embedder():
    """Return a simple embedder wrapper."""
    class Embedder:
        @staticmethod
        def embed_text(text):
            return embed_text(text)
        
        @staticmethod
        def embed_batch(texts):
            return embed_batch(texts)
    
    return Embedder()


def get_vector_store():
    """Return a simple vector store wrapper."""
    class VectorStore:
        def __init__(self):
            self.client = ensure_all_collections()
        
        def add_vectors(self, texts, vectors, metadatas):
            """Add vectors to Qdrant (simple wrapper)."""
            from qdrant_client.models import PointStruct
            import uuid
            
            points = []
            for text, vec, meta in zip(texts, vectors, metadatas):
                point_id = str(uuid.uuid4())
                payload = {**meta, "content": text}
                points.append(PointStruct(id=point_id, vector=vec, payload=payload))
            
            if points:
                self.client.upsert(collection_name=COLLECTION_SECTIONS, points=points)
        
        def get_collection_stats(self):
            """Get collection statistics."""
            try:
                collection_info = self.client.get_collection(COLLECTION_SECTIONS)
                return {
                    "points_count": collection_info.points_count,
                    "vectors_count": collection_info.vectors_count
                }
            except Exception:
                return {"points_count": 0}
    
    return VectorStore()


__all__ = [
    "embed_text",
    "embed_batch",
    "get_embedder",
    "get_vector_store",
    "search_sections",
    "search_hybrid",
]

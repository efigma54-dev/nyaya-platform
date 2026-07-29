# Nyaya Platform

Legal AI platform for Indian statutory corpus with hybrid search, IPC-BNS bidirectional mapping, and a knowledge graph of amendments, interpretations, and citations.

## Stack
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend**: FastAPI + SQLAlchemy 2.x (asyncpg) + Pydantic v2
- **Databases**: PostgreSQL 16 (relational), Qdrant (dense vectors), Redis 7 (cache/BM25 state)
- **Retrieval**: BM25 (token-level) + BGE-M3 dense (1024-dim) → Cross-Encoder rerank → Citation Validator
- **Knowledge Graph**: Replaces / amended_by / interpreted_by / cited_in / related_sections edges
- **Evaluation**: 1,000+ question benchmark measuring Recall@5/10, Precision@10, MRR, Hallucination (<2%)

## Quick Start (Docker Compose)

```bash
cp .env.example .env
docker compose up --build -d
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
# Seed + validation evidence logs appear in evidence/
```

## Baseline (Verified)
- 10 Acts, 51 Sections seeded (incl. IPC 1860 → BNS 2023 mappings for Sec. 302, 376, 498A, 377, etc.)

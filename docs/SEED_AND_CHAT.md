# Nyaya — Seed pipeline & chat verification

## Priority 1: Fix chat fallback

Chat returns `ai_provider: "fallback"` when RAG or AI fails. Most often **Qdrant has 0 vectors** because only Postgres was seeded, not embedded.

### Run pipeline (Docker)

```bash
docker compose up -d postgres redis qdrant
docker compose build api
docker compose run --rm --entrypoint "python" -e PYTHONPATH=/app api /scripts/run_seed_pipeline.py

# Or step by step (required: override entrypoint or uvicorn starts instead of the script):
docker compose run --rm --entrypoint "python" -e PYTHONPATH=/app api /scripts/seed_corpus_v2.py
docker compose run --rm --entrypoint "python" -e PYTHONPATH=/app api /scripts/embed_sections.py
# Or recreate API so entrypoint runs seeds + embed on start:
docker compose up -d --force-recreate api
```

### Run pipeline (local, from repo root)

```bash
# Postgres + Qdrant must be reachable via .env DATABASE_URL / QDRANT_URL
python scripts/run_seed_pipeline.py
```

Order executed:

1. `scripts/seed_acts_metadata.py` — acts (skips duplicates by `short_title`)
2. `scripts/seed_bns_sections.py` — BNS + CPA sections
3. `scripts/seed_corpus_v2.py` — PWDVA, IT Act, RTI, POCSO, etc.
4. `scripts/embed_sections.py` — vectors into Qdrant

### Verify Qdrant

```bash
docker compose run --rm api python -c "
from app.rag.vector_store import get_qdrant_client, COLLECTION_NAME
c = get_qdrant_client()
info = c.get_collection(COLLECTION_NAME)
print('Vectors in Qdrant:', info.vectors_count)
"
```

Expect **50+** vectors after full corpus seed.

### Test chat

```bash
curl -s http://localhost:8000/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "murder BNS section", "session_id": "t1"}' | jq .ai_provider
```

Expect `groq/llama-3.3-70b` or `gemini/...`, **not** `fallback`.

### Frontend (port 3005)

- Chat POST must be **`/api/chat`** (no trailing slash) — proxies to backend `/chat`.
- Rebuild after changes: `docker compose build frontend && docker compose up -d --force-recreate frontend`

## Browse Laws empty

- Fixed duplicate acts in API (`/sections/acts/list` dedupes by `short_title`).
- Re-run seed pipeline if `section_count` is 0.

## Environment

- `GROQ_API_KEY` (or `GEMINI_API_KEY`) required for AI answers.
- `TAVILY_API_KEY` optional — recent-law web grounding in `chat_service.py`.

## Hindi

- UI toggle sends `lang: "hi"` on chat requests.
- Backend also auto-detects Hindi queries via `langdetect` when `lang` is `en`.

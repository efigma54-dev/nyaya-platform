from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from nyaya.api.auth import router as auth_router
from nyaya.api.benchmark import router as benchmark_router
from nyaya.api.corpus import router as corpus_router
from nyaya.api.health import router as health_router
from nyaya.api.search_route import router as search_router
from nyaya.config.settings import get_settings
from nyaya.core.database import close_db, get_engine, init_db
from nyaya.services.qdrant_client import ensure_collection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _ = get_engine()
    await init_db(drop_first=False)
    ensure_collection()
    try:
        from nyaya.core.database import get_session_factory

        factory = get_session_factory()
        async with factory() as db:
            from nyaya.seed import seed_all

            counts = await seed_all(db, baseline=True)
            app.state.seed_counts = counts
            await db.commit()
    except Exception as exc:  # pragma: no cover
        app.state.seed_error = repr(exc)
    yield
    await close_db()


app = FastAPI(
    title="Nyaya AI — Legal Statutory Corpus Platform",
    description=(
        "Indian statutory corpus with hybrid search (BM25 + BGE-M3 dense + cross-encoder rerank + citation "
        "validator), bidirectional IPC ↔ BNS mappings, Knowledge Graph of amendments/citations/interpretations, "
        "and a benchmark harness measuring R@5/10, P@10, MRR, and hallucination rates."
    ),
    version="0.1.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={"name": "Nyaya AI Engineering"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-nyaya-request-id"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(corpus_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(benchmark_router, prefix="/api/v1")


@app.get("/api", include_in_schema=False)
async def api_root() -> dict:
    return {
        "name": "Nyaya Platform API",
        "version": app.version,
        "docs": "/docs",
        "endpoints": ["/api/v1/health", "/api/v1/auth/login", "/api/v1/corpus/acts",
                      "/api/v1/corpus/sections/{id}", "/api/v1/search", "/api/v1/benchmark/run"],
    }

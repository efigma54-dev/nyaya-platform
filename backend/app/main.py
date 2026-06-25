# backend/app/main.py

import asyncio
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.api.routes.chat import router as chat_router
from app.api.routes.sections import router as sections_router
from app.api.routes.fir import router as fir_router
from app.api.routes.docgen import router as docgen_router
from app.api.routes.amendments import router as amendments_router
from app.api.routes.lawyers import router as lawyers_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.whatsapp import router as whatsapp_router
from app.api.routes.auth import router as auth_router
from app.api.routes.user import router as user_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.rag.embedder import get_embedding_model
from prometheus_fastapi_instrumentator import Instrumentator
from app.rag.vector_store import ensure_collection

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)

# ─── Startup / Shutdown ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⚡ Nyaya backend starting...")
    
    # Initialize state attributes early to avoid AttributeErrors in health check
    app.state.redis = None
    app.state.qdrant = None
    app.state.model_ready = False

    logger.info("Initializing vector store collection...")
    await asyncio.to_thread(ensure_collection)
    
    # Load model in background without blocking startup
    async def load_model_background():
        try:
            print("🔄 Loading BAAI/bge-m3 in background...")
            await asyncio.to_thread(get_embedding_model)
            app.state.model_ready = True
            print("✅ Embedding model ready")
        except Exception as e:
            print(f"❌ Model load failed: {e}")
            app.state.model_ready = False
    
    # Schedule background task without awaiting (doesn't block startup)
    asyncio.create_task(load_model_background())

    app.state.redis = aioredis.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=True
    )
    app.state.qdrant = AsyncQdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )
    print("✅ Database, Redis, Qdrant connected")
    yield

    if app.state.redis:
        await app.state.redis.aclose()
    if app.state.qdrant:
        await app.state.qdrant.close()
    print("👋 Nyaya backend shutdown")


# ─── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="Nyaya Legal Platform API",
    description="AI-powered Indian legal information platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Initialize Prometheus
Instrumentator().instrument(app).expose(app)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(sections_router, prefix="/sections", tags=["sections"])
app.include_router(fir_router, prefix="/fir", tags=["fir"])
app.include_router(docgen_router, prefix="/generate", tags=["generate"])
app.include_router(amendments_router, prefix="/amendments", tags=["amendments"])
app.include_router(lawyers_router, prefix="/lawyers", tags=["lawyers"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])


# ─── Health Check ─────────────────────────────────────────────
@app.get("/health")
async def health(request: Request):
    checks = {}
    
    # Model
    checks["model"] = "ready" if getattr(request.app.state, "model_ready", False) else "loading"

    # PostgreSQL
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "healthy"
    except Exception as e:
        checks["postgres"] = f"error: {str(e)}"

    # Redis
    try:
        redis = getattr(request.app.state, "redis", None)
        if redis:
            await redis.ping()
            checks["redis"] = "healthy"
        else:
            checks["redis"] = "initializing"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    # Qdrant
    try:
        qdrant = getattr(request.app.state, "qdrant", None)
        if qdrant:
            await qdrant.get_collections()
            checks["qdrant"] = "healthy"
        else:
            checks["qdrant"] = "initializing"
    except Exception as e:
        checks["qdrant"] = f"error: {str(e)}"

    all_healthy = all(v == "healthy" or v == "ready" for v in checks.values())
    return {
        "status": "ok" if all_healthy else "degraded",
        "env": settings.APP_ENV,
        "services": checks,
    }


@app.get("/")
async def root():
    return {"message": "Nyaya Legal Platform API", "docs": "/docs"}

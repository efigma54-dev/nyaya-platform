# backend/app/api/routes/chat.py

from __future__ import annotations

import json
import logging

import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, root_validator

from app.core.config import settings
from app.core.database import get_db
from app.services.chat_service import answer_query
from app.models.analytics import QueryLog
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

SESSION_TTL = 60 * 60 * 24  # 24 hours


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    message: str | None = None
    session_id: str | None = None
    stream: bool = False
    lang: str = "en"

    @root_validator(pre=True)
    def allow_message_alias(cls, values):
        if not values.get("query") and values.get("message"):
            values["query"] = values["message"]
        return values


class ChatResponse(BaseModel):
    answer: str
    sections: list[dict]
    category: str | None
    session_id: str | None
    response_time_ms: int
    ai_provider: str
    emergency: dict | None = None
    low_confidence: bool = False
    ipc_bns_note: bool = False
    lang: str = "en"


async def load_session(redis: aioredis.Redis, session_id: str) -> list[dict]:
    try:
        raw = await redis.get(f"session:{session_id}")
        return json.loads(raw) if raw else []
    except Exception:
        return []


async def save_session(
    redis: aioredis.Redis,
    session_id: str,
    history: list[dict],
    query: str,
    answer: str,
):
    try:
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": answer})
        await redis.setex(
            f"session:{session_id}",
            SESSION_TTL,
            json.dumps(history[-10:]),
        )
    except Exception:
        pass


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
async def chat(request: Request, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Main chat endpoint.
    - Retrieves relevant legal sections via RAG
    - Routes to best AI provider
    - Returns cited answer + section cards + emergency alerts
    """
    if not getattr(request.app.state, "model_ready", False):
        logger.info("Chat request while embedding model still loading (first query may be slow)")

    if len(body.query.strip()) < 3:
        raise HTTPException(400, "Query too short")

    redis_client: aioredis.Redis = request.app.state.redis
    history = await load_session(redis_client, body.session_id) if body.session_id else []

    try:
        result = await answer_query(
            query=body.query,
            session_history=history,
            stream=False,
            lang=body.lang,
        )
    except Exception as e:
        logger.error(f"Error in answer_query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")

    if body.session_id:
        await save_session(
            redis_client, body.session_id, history,
            body.query, result["answer"]
        )

    resp = ChatResponse(
        answer=result["answer"],
        sections=result["sections"],
        category=result["category"],
        session_id=body.session_id,
        response_time_ms=result["response_time_ms"],
        ai_provider=result["provider"],
        emergency=result.get("emergency"),
        low_confidence=result.get("low_confidence", False),
        ipc_bns_note=result.get("ipc_bns_note", False),
        lang=body.lang,
    )

    # Analytics
    try:
        log = QueryLog(
            query_text=body.query,
            response_text=result["answer"],
            category=result.get("category"),
            provider=result.get("provider"),
            response_time_ms=result.get("response_time_ms"),
            lang=body.lang
        )
        db.add(log)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to log query: {e}")

    return resp


@router.post("/stream")
async def chat_stream(request: Request, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Streaming endpoint — returns Server-Sent Events.
    Frontend reads word by word, appears instantly.
    """
    if not getattr(request.app.state, "model_ready", False):
        logger.info("Stream chat while embedding model still loading")

    redis_client: aioredis.Redis = request.app.state.redis
    history = await load_session(redis_client, body.session_id) if body.session_id else []

    try:
        result = await answer_query(
            query=body.query,
            session_history=history,
            stream=True,
            lang=body.lang,
        )
    except Exception as e:
        logger.error(f"Failed to initialize chat stream: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    # Send emergency data first (instant)
    async def generate():
        full_answer = ""
        logger.info(f"Streaming started for query: {body.query[:50]}...")

        try:
            # 1. Send emergency block immediately if detected
            if result.get("emergency"):
                logger.debug("Sending emergency data")
                yield f"data: {json.dumps({'type': 'emergency', 'data': result['emergency']})}\n\n"

            # 2. Send sections immediately (from RAG, no AI wait)
            if result.get("sections"):
                logger.debug(f"Sending {len(result['sections'])} sections")
                yield f"data: {json.dumps({'type': 'sections', 'data': result['sections']})}\n\n"

            # 3. Send metadata
            logger.debug(f"Sending meta data (provider: {result.get('provider')})")
            yield f"data: {json.dumps({'type': 'meta', 'data': {'category': result.get('category'), 'provider': result.get('provider'), 'low_confidence': result.get('low_confidence', False)}})}\n\n"

            # 4. Stream the AI response token by token
            stream_obj = result.get("stream")
            if stream_obj:
                logger.debug("Beginning token stream")
                try:
                    provider = result.get("provider", "")

                    if "cerebras" in provider or "groq" in provider:
                        # OpenAI-compatible streaming
                        async for chunk in stream_obj:
                            if chunk.choices and chunk.choices[0].delta.content:
                                token = chunk.choices[0].delta.content
                                full_answer += token
                                yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

                    elif "gemini" in provider:
                        # Gemini streaming
                        async for chunk in stream_obj:
                            token = chunk.text
                            full_answer += token
                            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

                except Exception as e:
                    logger.error(f"Stream failed during token generation: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
            else:
                logger.warning("No stream object returned from provider")

            # 5. Done signal
            logger.info("Streaming complete")
            yield f"data: {json.dumps({'type': 'done', 'data': {'full_answer': full_answer}})}\n\n"

            # 6. Save to session
            if body.session_id and full_answer:
                await save_session(
                    redis_client, body.session_id, history,
                    body.query, full_answer
                )
            
            # 7. Analytics
            try:
                log = QueryLog(
                    query_text=body.query,
                    response_text=full_answer,
                    category=result.get("category"),
                    provider=result.get("provider"),
                    lang=body.lang
                )
                db.add(log)
                await db.commit()
            except Exception as e:
                logger.error(f"Failed to log streaming query: {e}")
        except Exception as e:
            logger.error(f"General stream failure: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': 'Stream connection lost'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def chat_health():
    return {"status": "ok", "providers": ["cerebras", "groq", "gemini", "openrouter"]}


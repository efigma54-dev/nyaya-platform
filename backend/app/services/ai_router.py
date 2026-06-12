# backend/app/services/ai_router.py
# Routes queries to the best free AI provider based on complexity.
# Priority: Groq (reliable) → Gemini → OpenRouter
# Zero paid APIs. All free tiers stacked.

import time
import asyncio
from enum import Enum
from dataclasses import dataclass
from app.core.config import settings


class ModelProvider(str, Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


@dataclass
class RouteDecision:
    provider: ModelProvider
    model: str
    reason: str


def classify_complexity(query: str, retrieved_sections: list[dict]) -> str:
    """
    Classify query complexity to pick the right model.
    simple/medium → Groq (reliable free tier)
    complex      → Gemini (best reasoning, 1M context)
    """
    query_lower = query.lower()

    # Multi-law indicators — needs Gemini
    multi_law_keywords = [
        "also", "additionally", "and also", "multiple", "both",
        "employer", "harass",   # labour + POSH potentially
        "sc community", "scheduled caste", "dalit",  # SC/ST Act
        "minor", "child",  # POCSO potentially
        "government", "public servant",  # constitutional + criminal
    ]

    # Long queries = complex situation
    if len(query.split()) > 40:
        return "complex"

    # Multiple law categories retrieved = complex
    if retrieved_sections:
        categories = set(r["payload"].get("category", "") for r in retrieved_sections)
        if len(categories) >= 3:
            return "complex"

    # Keyword-based complexity
    if any(k in query_lower for k in multi_law_keywords):
        return "medium"

    return "simple"


def decide_route(
    query: str,
    retrieved_sections: list[dict],
    groq_rate_limited: bool = False,
) -> RouteDecision:
    """Pick the best provider for this query."""
    complexity = classify_complexity(query, retrieved_sections)

    if complexity == "complex":
        return RouteDecision(
            provider=ModelProvider.GEMINI,
            model="gemini-2.0-flash",
            reason="complex multi-law query"
        )

    # Groq is reliable free tier for simple/medium
    if not groq_rate_limited and settings.GROQ_API_KEY:
        return RouteDecision(
            provider=ModelProvider.GROQ,
            model="llama-3.3-70b-versatile",
            reason="reliable free tier"
        )

    # Fallback → Gemini
    if settings.GEMINI_API_KEY:
        return RouteDecision(
            provider=ModelProvider.GEMINI,
            model="gemini-2.0-flash",
            reason="primary fallback"
        )

    # Last resort → OpenRouter free models
    return RouteDecision(
        provider=ModelProvider.OPENROUTER,
        model="meta-llama/llama-3.3-70b-instruct:free",
        reason="rate limit fallback"
    )


async def call_groq(
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 1024,
    stream: bool = False,
):
    """Call Groq API — 300 tokens/sec, free tier."""
    from groq import AsyncGroq

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    if stream:
        return await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=0.1,
            stream=True,
        )
    else:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=0.1,
            stream=False,
        )
        return response.choices[0].message.content


async def call_gemini(
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 1500,
    stream: bool = False,
):
    """Call Gemini 2.0 Flash — best reasoning, 1M context, free 1500 req/day."""
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt,
    )

    # Convert messages to Gemini format
    history = []
    last_user_msg = ""
    for msg in messages:
        if msg["role"] == "user":
            last_user_msg = msg["content"]
        elif msg["role"] == "assistant":
            history.append({
                "role": "model",
                "parts": [msg["content"]]
            })

    if stream:
        chat = model.start_chat(history=history)
        return await chat.send_message_async(last_user_msg, stream=True)
    else:
        chat = model.start_chat(history=history)
        response = await chat.send_message_async(last_user_msg)
        return response.text


async def call_openrouter(
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 1024,
):
    """Call OpenRouter free models as fallback."""
    import httpx

    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://nyaya.legal",
                "X-Title": "Nyaya Legal Platform",
            },
            json={
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": full_messages,
                "max_tokens": max_tokens,
                "temperature": 0.1,
            },
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def route_and_call(
    query: str,
    messages: list[dict],
    system_prompt: str,
    retrieved_sections: list[dict],
    stream: bool = False,
) -> tuple[any, str]:
    """
    Main entry point. Returns (response, provider_name).
    Tries providers in order, falls back on rate limit / error.
    """
    decision = decide_route(query, retrieved_sections)
    providers_tried = []

    async def try_provider(decision: RouteDecision):
        providers_tried.append(decision.provider.value)
        try:
            if decision.provider == ModelProvider.GROQ:
                result = await call_groq(
                    messages, system_prompt, stream=stream
                )
                return result, f"groq/{decision.model}"

            elif decision.provider == ModelProvider.GEMINI:
                result = await call_gemini(
                    messages, system_prompt, stream=stream
                )
                return result, f"gemini/{decision.model}"

            elif decision.provider == ModelProvider.OPENROUTER:
                result = await call_openrouter(messages, system_prompt)
                return result, f"openrouter/{decision.model}"

        except Exception as e:
            import traceback

            error_str = str(e).lower()
            print(f"⚠️  {decision.provider.value} failed: {e}")
            print(traceback.format_exc())

            # Rate limited → try next provider
            if "rate" in error_str or "429" in error_str or "limit" in error_str:
                fallback_order = [
                    ModelProvider.GROQ,
                    ModelProvider.GEMINI,
                    ModelProvider.OPENROUTER,
                ]
                for provider in fallback_order:
                    if provider.value not in providers_tried:
                        next_decision = RouteDecision(
                            provider=provider,
                            model=_default_model(provider),
                            reason="rate limit fallback"
                        )
                        return await try_provider(next_decision)

            raise e

    return await try_provider(decision)


def _default_model(provider: ModelProvider) -> str:
    models = {
        ModelProvider.GROQ: "llama-3.3-70b-versatile",
        ModelProvider.GEMINI: "gemini-2.0-flash",
        ModelProvider.OPENROUTER: "meta-llama/llama-3.3-70b-instruct:free",
    }
    return models[provider]

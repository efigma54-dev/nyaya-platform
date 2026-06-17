# backend/app/services/chat_service.py

import json
import time
import asyncio
import logging
import traceback

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from langdetect import detect as langdetect_detect
except ImportError:
    langdetect_detect = None
from app.rag.embedder import embed_text
from app.rag.vector_store import search_sections
from app.services.ai_router import route_and_call, decide_route
from app.services.emergency import detect_emergency
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.legal import Act

# ── IPC → BNS Transition Map ─────────────────────────────────
IPC_TO_BNS = {
    "302": "103", "304": "104", "304A": "106", "306": "109",
    "307": "109", "319": "115", "320": "116", "321": "115",
    "322": "117", "323": "115", "324": "117", "325": "117",
    "354": "74",  "375": "63",  "376": "64",  "377": "100",
    "379": "303", "384": "308", "385": "308", "392": "309",
    "395": "310", "396": "310", "406": "316", "420": "318",
    "498A": "85", "499": "356", "500": "356", "503": "351",
    "504": "352", "505": "353", "506": "351", "509": "79",
}

BNS_TO_IPC = {v: k for k, v in IPC_TO_BNS.items()}

SYSTEM_PROMPT = """You are Nyaya, India's most trusted legal information assistant.

ABSOLUTE RULES:
1. ONLY cite sections that appear in the CONTEXT block. Never invent section numbers.
2. If context lacks relevant sections, say clearly: "I don't have this specific law in my database yet."
3. For IPC sections — always mention the equivalent BNS section (effective July 1, 2024).
4. Always end with the disclaimer.
5. Match language to user: Hindi query → Hindi response, English → English.
6. For complex situations involving multiple laws, address each law separately.

FORMAT YOUR RESPONSE:
**Direct Answer** (1-2 sentences)

**Applicable Laws:**
- [Act Name] Section [X]: [what it says] | Punishment: [X] | [Bailable/Non-Bailable]

**What You Should Do:**
1. [Immediate step]
2. [Next step]
3. [Legal step]

**Important:** [Any critical warning or time limit]

⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.

CONTEXT (only cite from this):
{context}"""


# Domestic / family violence — checked before generic criminal ("beat" etc.)
# These terms help detect PWDVA-style family/domestic violence queries so the
# RAG retrieval can bias toward family law sections rather than generic IPC crime.
FAMILY_DOMESTIC_KEYWORDS = [
    "beats me", "husband beats", "wife beats", "domestic violence",
    "in-laws", "sasural", "dowry", "pati", "patni", "ghar mein maar",
    "my husband beats", "husband is beating", "beating me daily",
    "hitting me daily", "physically abuse", "mujhe maarta hai",
    "husband beating", "pati maar", "pati maarta", "marital violence",
]

_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "criminal": [
        "murder", "kill", "theft", "rape", "assault", "beating", "hurt",
        "robbery", "fraud", "cheat", "extort", "arrest", "fir", "police",
        "mara", "maar", "chori", "dhoka", "pitai", "dacoity", "cheque bounce",
        "cheque bounced",
    ],
    "consumer": [
        "consumer", "product", "defective", "refund", "company", "service",
        "complaint", "shopping", "warranty", "bank", "insurance",
    ],
    "constitutional": [
        "fundamental right", "article 21", "article 14", "arrested",
        "detained", "freedom", "liberty", "maulik adhikar",
    ],
    "family": [
        "divorce", "marriage", "wife", "husband", "domestic",
        "harassment", "cruelty", "maintenance", "alimony", "custody", "talaq",
        "domestic violence", "husband beats", "wife beats", "in-laws",
        "sasural", "dowry", "pati", "patni", "ghar mein maar",
        "marital violence",
    ],
}


def is_family_domestic_query(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in FAMILY_DOMESTIC_KEYWORDS)


def detect_category(query: str) -> str | None:
    """Classify query for RAG filters. Domestic violence maps to family (PWDVA), not generic criminal."""
    if is_family_domestic_query(query):
        return "family"
    query_lower = query.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(k in query_lower for k in keywords):
            return category
    return None


def rag_act_categories(category: str | None, query: str) -> list[str] | None:
    """Category filter(s) for Qdrant. Family/domestic queries should search family + criminal acts."""
    if category == "family":
        return ["family", "criminal"]
    if category:
        return [category]
    return None


def prioritize_domestic_sections(query: str, retrieved: list[dict]) -> list[dict]:
    """Boost PWDVA / domestic violence act sections in ranked results."""
    if not is_family_domestic_query(query):
        return retrieved

    def boosted_score(item: dict) -> float:
        title = (item["payload"].get("act_title") or "").lower()
        bonus = 0.25 if "domestic violence" in title else 0.0
        return float(item["score"]) + bonus

    return sorted(retrieved, key=boosted_score, reverse=True)


def build_context(retrieved: list[dict]) -> str:
    if not retrieved:
        return "No directly relevant sections found."
    lines = []
    for i, r in enumerate(retrieved, 1):
        p = r["payload"]
        # Add IPC equivalent if BNS section
        ipc_note = ""
        sec_num = p.get("section_number", "")
        if sec_num in BNS_TO_IPC:
            ipc_note = f" (replaces IPC Section {BNS_TO_IPC[sec_num]})"

        lines += [
            f"--- [{i}] {p.get('act_title')} § {sec_num}{ipc_note} ---",
            f"Title: {p.get('section_title', '')}",
            f"Text: {p.get('bare_text', '')}",
            f"Plain: {p.get('plain_language', '')}",
            f"Punishment: {p.get('punishment_summary', 'N/A')}",
            f"Bail: {'Bailable' if p.get('is_bailable') else 'Non-Bailable' if p.get('is_bailable') is False else 'N/A'}",
            f"Court: {p.get('relevant_court', 'N/A')}",
            "",
        ]
    return "\n".join(lines)


from app.services.tavily_service import search_web
from app.services.kanoon_service import search_judgments

def resolve_response_lang(query: str, lang: str) -> str:
    """Use UI lang; auto-detect Hindi from query when lang is en/default."""
    if lang == "hi":
        return "hi"
    if langdetect_detect:
        try:
            if langdetect_detect(query) == "hi":
                return "hi"
        except Exception:
            pass
    return lang if lang in ("en", "hi") else "en"


async def answer_query(
    query: str,
    session_history: list[dict] | None = None,
    top_k: int = 5,
    stream: bool = False,
    lang: str = "en",
) -> dict:
    start = time.time()
    lang = resolve_response_lang(query, lang)

    # 1. Emergency check — instant, no AI needed
    emergency = detect_emergency(query)

    retrieved: list[dict] = []
    web_results: list = []
    judgments: list = []
    category: str | None = None
    low_confidence = True
    provider = "fallback"
    answer = ""
    enhanced_query = query

    # 2. Detect IPC references and add BNS equivalents to query
    for ipc, bns in IPC_TO_BNS.items():
        if f"ipc {ipc}" in query.lower() or f"section {ipc}" in query.lower():
            enhanced_query += f" (BNS Section {bns})"

    # 3. Detect state for localized search
    states = ["Maharashtra", "Uttar Pradesh", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "West Bengal", "Rajasthan"]
    detected_state = next((s for s in states if s.lower() in query.lower()), None)

    category = detect_category(query)
    rag_categories = rag_act_categories(category, query)
    search_k = max(top_k, 8) if rag_categories and len(rag_categories) > 1 else top_k

    # RAG retrieval (isolated — empty Qdrant should not block AI)
    try:
        query_vector = await asyncio.to_thread(embed_text, enhanced_query)
        retrieved = await asyncio.to_thread(
            search_sections,
            query_vector=query_vector,
            top_k=search_k,
            act_categories=rag_categories,
            state=detected_state,
        )
        if not retrieved and rag_categories:
            retrieved = await asyncio.to_thread(
                search_sections,
                query_vector=query_vector,
                top_k=search_k,
                act_categories=None,
                state=detected_state,
            )
        retrieved = prioritize_domestic_sections(query, retrieved)[:top_k]

        # If Qdrant payloads lack `act_title`, enrich from DB so reporting shows act names.
        try:
            async with AsyncSessionLocal() as db:
                for r in retrieved:
                    p = r.get("payload", {})
                    act_id = p.get("act_id")
                    if not p.get("act_title") and act_id:
                        try:
                            act_id_int = int(act_id)
                        except Exception:
                            act_id_int = act_id
                        res = await db.execute(select(Act).where(Act.id == act_id_int))
                        act = res.scalar_one_or_none()
                        if act:
                            p["act_title"] = act.short_title
                            logger.info("Enriched payload act_title for act_id=%s -> %s", act_id, act.short_title)
        except Exception as e:
            logger.warning("Act enrichment failed: %s", e)
    except Exception as e:
        logger.error("RAG retrieval failed: %s\n%s", e, traceback.format_exc())
        retrieved = []

    top_score = retrieved[0]["score"] if retrieved else 0
    low_confidence = top_score < 0.40

    recent_keywords = [
        "recent", "amendment", "new law", "new", "2024", "2025", "latest", "update",
    ]
    should_search_web = (
        any(k in query.lower() for k in recent_keywords)
        or top_score < 0.30
        or not retrieved
    )
    if should_search_web:
        try:
            web_results = await search_web(query)
        except Exception as e:
            logger.warning("Web search failed: %s", e)

    legal_keywords = ["case", "judgment", "ruling", "precedent", "supreme court", "high court"]
    if any(k in query.lower() for k in legal_keywords) or (retrieved and top_score > 0.5):
        try:
            judgments = await search_judgments(query)
        except Exception as e:
            logger.warning("Judgment search failed: %s", e)

    context = build_context(retrieved)
    if web_results:
        web_context = "\n\nWEB SEARCH RESULTS (FOR REAL-TIME GROUNDING):\n"
        for res in web_results:
            web_context += f"- {res['title']} ({res['url']}): {res['content'][:300]}...\n"
        context += web_context

    if judgments:
        judgment_context = "\n\nLEGAL JUDGMENTS (FROM INDIAN KANOON):\n"
        for j in judgments:
            judgment_context += f"- {j['title']} ({j['url']}): {j['snippet']}\n"
        context += judgment_context

    messages: list[dict] = []
    if session_history:
        messages = [
            {"role": t["role"], "content": t["content"]}
            for t in session_history[-4:]
        ]
    messages.append({"role": "user", "content": query})

    system = SYSTEM_PROMPT.format(context=context)
    if judgments:
        system += (
            "\n\nNote: I have provided some relevant legal judgments from Indian Kanoon. "
            "Use them to support your explanation of legal principles."
        )
    if web_results:
        system += (
            "\n\nNote: Some information above is from a web search for real-time grounding. "
            "Prioritize official database sections if they conflict."
        )
    if lang == "hi":
        system += (
            "\n\nIMPORTANT: Respond ENTIRELY in Hindi using Devanagari script. "
            "Legal terms may stay in English but explanations must be in Hindi."
        )

    try:
        response, provider = await route_and_call(
            query=query,
            messages=messages,
            system_prompt=system,
            retrieved_sections=retrieved,
            stream=stream,
        )
        if stream:
            return {
                "stream": response,
                "emergency": emergency,
                "sections": [r["payload"] for r in retrieved],
                "web_sources": web_results,
                "judgments": judgments,
                "category": category,
                "provider": provider,
                "low_confidence": low_confidence,
                "ipc_bns_note": bool(enhanced_query != query),
                "lang": lang,
            }
        answer = response
    except Exception as e:
        logger.error(
            "AI route_and_call failed: %s\n%s", e, traceback.format_exc()
        )
        if retrieved:
            lines = [
                "I retrieved these sections from the legal database, but the AI summarizer is temporarily unavailable:\n"
            ]
            for r in retrieved[:5]:
                p = r["payload"]
                lines.append(
                    f"- {p.get('act_title')} § {p.get('section_number')}: {p.get('plain_language', p.get('bare_text', ''))[:200]}"
                )
            lines.append(
                "\n⚠️ This is legal information only, not legal advice. Free legal aid: NALSA 15100."
            )
            answer = "\n".join(lines)
            provider = "rag-only"
        else:
            answer = (
                "The legal database or AI service is temporarily unavailable. "
                "If this persists, ensure sections are seeded and embedded into Qdrant "
                "(run scripts/run_seed_pipeline.py).\n\n"
                "⚠️ This is legal information only, not legal advice. Free legal aid: NALSA 15100."
            )
            provider = "fallback"

    return {
        "answer": answer,
        "emergency": emergency,
        "sections": [r["payload"] for r in retrieved] if retrieved else [],
        "web_sources": web_results,
        "judgments": judgments,
        "category": category,
        "response_time_ms": int((time.time() - start) * 1000),
        "provider": provider,
        "sections_count": len(retrieved) if retrieved else 0,
        "low_confidence": low_confidence,
        "ipc_bns_note": bool(enhanced_query != query),
        "lang": lang,
    }


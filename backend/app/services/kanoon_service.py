import httpx
import logging
from typing import List, Dict
from app.core.config import settings
from app.services.ai_router import route_and_call

logger = logging.getLogger(__name__)

async def search_judgments(query: str, max_results: int = 3) -> List[Dict]:
    """
    Search for legal judgments on Indian Kanoon using Tavily as a proxy.
    """
    if not settings.TAVILY_API_KEY:
        return []

    # Enhance query to specifically look for judgments
    judgment_query = f"{query} site:indiankanoon.org"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": judgment_query,
                    "search_depth": "basic",
                    "max_results": max_results,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            judgments = []
            for res in data.get("results", []):
                judgments.append({
                    "title": res.get("title"),
                    "url": res.get("url"),
                    "snippet": res.get("content")[:500] + "..." if len(res.get("content")) > 500 else res.get("content"),
                })
            return judgments
    except Exception as e:
        logger.error(f"Kanoon search failed: {e}")
        return []

async def summarize_judgment(text: str) -> str:
    """
    Uses the AI router to summarize a long legal judgment.
    """
    prompt = f"""
    You are an expert Indian legal researcher. Summarize the following legal judgment snippet.
    Provide:
    1. Key facts of the case.
    2. The core legal question addressed.
    3. The final decision/precedent established.
    
    Format the summary in clear bullet points.
    
    JUDGMENT TEXT:
    {text}
    """
    
    messages = [{"role": "user", "content": prompt}]
    system = "You are a professional legal analyst specialized in Indian Case Law. Write in English."
    
    try:
        summary, _ = await route_and_call(
            query="Judgment summarization",
            messages=messages,
            system_prompt=system,
            retrieved_sections=[],
            stream=False
        )
        return summary
    except Exception as e:
        logger.error(f"Judgment summarization failed: {e}")
        return "Failed to generate judgment summary. Please review the full text at the provided link."

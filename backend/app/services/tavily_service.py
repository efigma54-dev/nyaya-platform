import httpx
import logging
from typing import List, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

async def search_web(query: str, max_results: int = 3) -> List[Dict]:
    """
    Performs a web search using Tavily API.
    Returns a list of dicts with 'title', 'url', and 'content'.
    """
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY not set, skipping web search.")
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": False,
                    "max_results": max_results,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get("results", []):
                results.append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "content": result.get("content"),
                })
            return results
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return []

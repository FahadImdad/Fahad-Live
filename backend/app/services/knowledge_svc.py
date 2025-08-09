"""Utilities for fetching public snippets about Fahad Imdad."""
from __future__ import annotations

from typing import List
import os
import re

import httpx
from cachetools import TTLCache

_TAVILY_URL = "https://api.tavily.com/search"
_TRIVILY_URL = "https://api.trivily.com/search"
_DOMAIN = "fahadimdad.com"
_CACHE = TTLCache(maxsize=32, ttl=30 * 60)  # 30 minute TTL


def _strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    return " ".join(cleaned.split())


async def _query_service(query: str) -> List[str]:
    api_key = os.getenv("TAVILY_API_KEY") or os.getenv("TRIVILY_API_KEY")
    if not api_key:
        return []
    url = _TAVILY_URL if os.getenv("TAVILY_API_KEY") else _TRIVILY_URL
    payload = {
        "query": query,
        "api_key": api_key,
        "include_domains": [_DOMAIN],
        "max_results": 5,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []
    results = data.get("results", [])
    snippets = []
    seen = set()
    for item in results:
        content = _strip_html(item.get("content", ""))[:120]
        if content and content not in seen:
            seen.add(content)
            snippets.append(content)
    return snippets


async def fetch_personal_snippets(query: str) -> List[str]:
    """Fetch short public info snippets from fahadimdad.com related to query."""
    key = query.lower().strip()
    if not key:
        return []
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    snippets = await _query_service(query)
    _CACHE[key] = snippets
    return snippets

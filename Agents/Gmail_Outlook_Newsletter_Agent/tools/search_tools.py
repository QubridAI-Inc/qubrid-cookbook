"""
tools/search_tools.py

Web search tool for NewsletterAgent research agents.
Uses DuckDuckGo (no API key required) so it works with any LLM backend,
including Qubrid-hosted models via LiteLLM.
"""

import json
import time
import random
try:
    from ddgs import DDGS  # type: ignore
except ImportError:
    from duckduckgo_search import DDGS  # type: ignore
from google.adk.tools import FunctionTool  # type: ignore


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for recent news with retries and jitter to handle rate limits."""
    last_error = ""
    for attempt in range(3):
        try:
            # Add jitter to stagger requests from parallel agents
            time.sleep(random.uniform(0.5, 2.0) * (attempt + 1))
            
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
                if not results:
                    results = list(ddgs.text(query, max_results=max_results))
                
                simplified = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", r.get("href", "")),
                        "summary": r.get("body", r.get("snippet", "")),
                        "date": r.get("date", r.get("published", "recent")),
                        "source": r.get("source", r.get("url", "")),
                    }
                    for r in results
                ]
                return json.dumps(simplified, ensure_ascii=False, indent=2)
        except Exception as exc:
            last_error = str(exc)
            if "Ratelimit" not in last_error and "429" not in last_error:
                break  # Don't retry for non-rate-limit errors
                
    return json.dumps({"error": f"Search limit reached: {last_error}"})


web_search_tool = FunctionTool(web_search)

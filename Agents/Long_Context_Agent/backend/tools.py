"""DuckDuckGo web search tool used by the agentic chat loop."""

from __future__ import annotations


def web_search(query: str, max_results: int = 5) -> str:
    """Run a DuckDuckGo search and return formatted results."""
    try:
        from ddgs import DDGS
    except ImportError:
        return "Web search unavailable: `ddgs` is not installed."

    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=max_results))
    except Exception as exc:
        return f"Search failed: {exc}"

    if not hits:
        return "No results found."

    lines: list[str] = []
    for hit in hits:
        title = hit.get("title", "").strip()
        url = hit.get("href", "").strip()
        body = hit.get("body", "").strip()
        lines.append(f"**{title}**\n{url}\n{body}")

    return "\n\n".join(lines)

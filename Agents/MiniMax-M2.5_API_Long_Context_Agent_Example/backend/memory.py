"""Utilities for long-context memory tracking and lightweight analysis."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta

STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "been",
    "before",
    "being",
    "could",
    "from",
    "have",
    "into",
    "just",
    "like",
    "more",
    "need",
    "really",
    "should",
    "some",
    "than",
    "that",
    "them",
    "they",
    "this",
    "through",
    "want",
    "with",
    "would",
    "your",
}


def build_context_window(messages: list[dict[str, object]]) -> list[dict]:
    """Return the full conversation history without truncation."""
    result = []
    for message in messages:
        raw = message.get("api_content") or message.get("content", "")
        # Detect JSON-serialized multimodal content (list of content parts)
        content: object = str(raw)
        if isinstance(raw, str) and raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    content = parsed
            except (json.JSONDecodeError, ValueError):
                pass
        result.append({"role": str(message.get("role", "")), "content": content})
    return result


def get_turn_count(messages: list[dict[str, object]]) -> int:
    """Count turns as the number of user messages in the conversation."""
    return sum(1 for message in messages if message.get("role") == "user")


def get_memory_stats(messages: list[dict[str, object]]) -> dict[str, object]:
    """Compute lightweight stats for the current conversation memory."""
    total_turns = get_turn_count(messages)
    total_messages = len(messages)
    total_chars = sum(
        len(str(message.get("api_content") or message.get("content", "")))
        for message in messages
    )
    estimated_tokens = max(0, total_chars // 4)

    if total_turns < 20:
        context_health = "Fresh"
    elif total_turns < 50:
        context_health = "Deep"
    elif total_turns < 80:
        context_health = "Very Deep"
    else:
        context_health = "Maximum"

    return {
        "total_turns": total_turns,
        "total_messages": total_messages,
        "total_chars": total_chars,
        "estimated_tokens": estimated_tokens,
        "context_health": context_health,
    }


def extract_key_topics(messages: list[dict[str, object]]) -> list[str]:
    """Extract up to five recurring topics from user messages."""
    user_texts = [
        str(message.get("api_content") or message.get("content", ""))
        for message in messages
        if message.get("role") == "user"
    ]
    if not user_texts:
        return []

    full_text = "\n".join(user_texts)
    proper_nouns = Counter(re.findall(r"\b[A-Z][A-Za-z0-9-]+\b", full_text))

    words = re.findall(r"\b[a-zA-Z]{4,}\b", full_text.lower())
    repeated = Counter(word for word in words if word not in STOPWORDS)

    scored_topics: dict[str, int] = {}
    for topic, count in proper_nouns.items():
        scored_topics[topic] = scored_topics.get(topic, 0) + (count * 3)

    for topic, count in repeated.items():
        if count > 2:
            display = topic.capitalize()
            scored_topics[display] = scored_topics.get(display, 0) + count

    ordered_topics = sorted(
        scored_topics.items(),
        key=lambda item: (-item[1], item[0].lower()),
    )
    return [topic for topic, _score in ordered_topics[:5]]


def format_relative_time(timestamp: str) -> str:
    """Render an ISO or SQLite timestamp in a compact relative format."""
    if not timestamp:
        return ""

    cleaned_timestamp = timestamp.replace("Z", "+00:00").strip()
    parsed = None
    try:
        parsed = datetime.fromisoformat(cleaned_timestamp)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
            try:
                parsed = datetime.strptime(cleaned_timestamp, fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        return timestamp

    if parsed.tzinfo is not None:
        now = datetime.now(parsed.tzinfo)
        parsed = parsed.astimezone(parsed.tzinfo)
    else:
        now = datetime.now()

    delta = now - parsed
    if delta < timedelta(seconds=60):
        return "just now"
    if delta < timedelta(hours=1):
        minutes = max(1, int(delta.total_seconds() // 60))
        return f"{minutes} min ago"
    if delta < timedelta(days=1):
        hours = max(1, int(delta.total_seconds() // 3600))
        return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
    if delta < timedelta(days=2):
        return "Yesterday"
    return parsed.strftime("%b %d, %Y")

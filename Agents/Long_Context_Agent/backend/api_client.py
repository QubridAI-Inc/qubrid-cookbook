"""HTTP client for sending chat completions to the Qubrid API."""

from __future__ import annotations

import json
from os import getenv
import re
import time
from collections.abc import Iterator
from typing import Any

import requests
from dotenv import load_dotenv
from requests.exceptions import ConnectionError as RequestsConnectionError

from config.settings import MAX_TOKENS, MODEL_NAME, QUBRID_BASE_URL, TEMPERATURE
from config.prompts import (
    AGENT_WEB_SEARCH_ADDENDUM,
    FOLLOWUP_AGENT_SYSTEM,
    FOLLOWUP_AGENT_USER,
    SUMMARY_AGENT_SYSTEM,
    SUMMARY_AGENT_USER,
    SYSTEM_RESPONSE_RULES,
    TITLE_AGENT_SYSTEM,
    TITLE_AGENT_USER,
)

load_dotenv()

# Detect model-initiated [SEARCH: ...] in the token stream.
_SEARCH_RE = re.compile(r"\[SEARCH:\s*(.+?)\]", re.IGNORECASE | re.DOTALL)
_PROBE_CHARS = 160  # buffer enough chars to catch the search tag reliably


def _friendly_error_message(response: requests.Response | None, detail: str) -> str:
    """Build a short user-facing error message for failed API calls."""
    if response is None:
        return detail

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    api_message = (
        payload.get("error", {}).get("message")
        or payload.get("message")
        or payload.get("detail")
        or response.text.strip()
    )
    if api_message:
        return f"{detail} ({response.status_code}): {api_message}"
    return f"{detail} ({response.status_code})."


def _sanitize_assistant_content(content: str) -> str:
    """Strip leaked tool-call markup from assistant output."""
    leaked_tool_markup = bool(
        re.search(r"<minimax:tool_call\b.*?</minimax:tool_call>", content, flags=re.IGNORECASE | re.DOTALL)
        or re.search(r"<invoke\b.*?</invoke>", content, flags=re.IGNORECASE | re.DOTALL)
    )

    cleaned = re.sub(
        r"<minimax:tool_call\b.*?</minimax:tool_call>",
        "",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(
        r"<invoke\b.*?</invoke>",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(r"</?parameter[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</?minimax:tool_call[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    if not leaked_tool_markup:
        return cleaned

    lowered = cleaned.lower()
    if (not cleaned) or "let me first extract" in lowered or "tool_call" in lowered or "invoke name" in lowered:
        return (
            "I can analyze the uploaded file, but I could not read usable text from it in the current setup. "
            "Upload a text-extractable document or paste the key sections you want reviewed, and I will analyze them directly."
        )
    return cleaned


def _raw_stream(
    messages: list[dict[str, Any]], system_prompt: str, api_key: str
) -> Iterator[str]:
    """Core SSE streaming — yields raw delta tokens from the API."""
    full_message_list = [{"role": "system", "content": system_prompt}] + [
        {"role": m.get("role", ""), "content": m.get("content", "")}
        for m in messages
    ]
    payload = {
        "model": MODEL_NAME,
        "messages": full_message_list,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": True,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with requests.post(
        f"{QUBRID_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line if isinstance(raw_line, bytes) else raw_line.encode()
            if not line.startswith(b"data: "):
                continue
            data = line[6:]
            if data.strip() == b"[DONE]":
                break
            try:
                chunk = json.loads(data)
                delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content") or ""
                if delta:
                    yield delta
            except (json.JSONDecodeError, IndexError, KeyError):
                continue


def chat_agent(
    messages: list[dict[str, Any]],
    persona_system: str,
) -> Iterator[str]:
    """Agentic streaming loop — model autonomously decides when to search the web.

    The model is instructed to output ``[SEARCH: query]`` as its very first
    token when it needs real-time information.  The loop intercepts that tag,
    runs DuckDuckGo, injects results into context, and re-streams the final
    answer.  If no search is needed the tokens flow straight through.
    """
    from backend.tools import web_search as _web_search

    api_key = getenv("QUBRID_API_KEY", "").strip()
    if not api_key:
        yield "Error: Missing `QUBRID_API_KEY` in your `.env` file."
        return

    system_prompt = f"{persona_system}\n\n{SYSTEM_RESPONSE_RULES}\n{AGENT_WEB_SEARCH_ADDENDUM}"

    try:
        token_gen = _raw_stream(list(messages), system_prompt, api_key)
    except Exception as exc:
        yield f"\n\n*Stream error: {exc}*"
        return

    # Buffer the first _PROBE_CHARS tokens to detect [SEARCH: ...]
    probe = ""
    search_detected = False
    for token in token_gen:
        probe += token
        if _SEARCH_RE.search(probe):
            for _ in token_gen:   # drain the rest of the stream
                pass
            search_detected = True
            break
        if len(probe) >= _PROBE_CHARS:
            yield probe           # no search tag — pass through buffered + rest
            yield from token_gen
            return

    if not search_detected:
        if probe:
            yield probe
        return

    # --- Tool node: run the search ---
    match = _SEARCH_RE.search(probe)
    query = match.group(1).strip() if match else probe.strip()
    yield f"🔍 *Searching: {query}*\n\n"
    results = _web_search(query)

    # --- Re-stream with search results injected into context ---
    augmented = list(messages) + [{
        "role": "user",
        "content": (
            f"[Web search results for '{query}']:\n\n{results}\n\n"
            "Use these results to answer the user's question accurately."
        ),
    }]
    try:
        yield from _raw_stream(augmented, system_prompt, api_key)
    except Exception as exc:
        yield f"\n\n*Search-augmented response failed: {exc}*"


def generate_followups(messages: list[dict[str, Any]]) -> list[str]:
    """Agent: generate 3 contextual follow-up questions after each response."""
    api_key = getenv("QUBRID_API_KEY", "").strip()
    if not api_key:
        return []

    recent = messages[-6:]
    convo = "\n".join(
        f"{m['role'].upper()}: {str(m.get('content', ''))[:300]}" for m in recent
    )
    prompt_msgs = [{"role": "user", "content": FOLLOWUP_AGENT_USER.format(convo=convo)}]
    result = chat(prompt_msgs, FOLLOWUP_AGENT_SYSTEM)
    content = result.get("content", "")
    if not content:
        return []
    questions = [
        q.strip().lstrip("•-0123456789. ")
        for q in content.strip().splitlines()
        if q.strip()
    ]
    return questions[:3]


def generate_session_title(messages: list[dict[str, Any]]) -> str:
    """Agent: auto-generate a smart session title after the first exchange."""
    api_key = getenv("QUBRID_API_KEY", "").strip()
    if not api_key:
        return ""

    first_msgs = messages[:4]
    convo = "\n".join(
        f"{m['role'].upper()}: {str(m.get('content', ''))[:200]}" for m in first_msgs
    )
    prompt_msgs = [{"role": "user", "content": TITLE_AGENT_USER.format(convo=convo)}]
    result = chat(prompt_msgs, TITLE_AGENT_SYSTEM)
    title = result.get("content", "").strip().strip("\"'")
    return title[:80]


def summarize_conversation(messages: list[dict[str, Any]]) -> str:
    """Agent: generate a concise bullet-point summary of the conversation."""
    api_key = getenv("QUBRID_API_KEY", "").strip()
    if not api_key:
        return "Error: Missing `QUBRID_API_KEY` in your `.env` file."

    convo_lines: list[str] = []
    for m in messages:
        role = str(m.get("role", "")).upper()
        raw = m.get("api_content") or m.get("content", "")
        if isinstance(raw, list):
            text = " ".join(p.get("text", "") for p in raw if p.get("type") == "text")
        else:
            text = str(raw)
        convo_lines.append(f"{role}: {text[:400]}")

    convo = "\n".join(convo_lines)
    prompt_msgs = [{"role": "user", "content": SUMMARY_AGENT_USER.format(convo=convo)}]
    result = chat(prompt_msgs, SUMMARY_AGENT_SYSTEM)
    return result.get("content") or "Could not generate a summary."


def chat(messages: list[dict[str, Any]], persona_system: str) -> dict[str, Any]:
    """Send the full conversation context to Qubrid and return a normalized payload."""
    api_key = getenv("QUBRID_API_KEY", "").strip()
    if not api_key:
        return {
            "error": "Missing `QUBRID_API_KEY` in your `.env` file.",
            "latency_ms": 0.0,
        }

    system_prompt = f"{persona_system}\n\n{SYSTEM_RESPONSE_RULES}"
    full_message_list = [{"role": "system", "content": system_prompt}] + [
        {"role": message.get("role", ""), "content": message.get("content", "")}
        for message in messages
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": full_message_list,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    start_time = time.time()
    response: requests.Response | None = None
    try:
        response = requests.post(
            f"{QUBRID_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        latency_ms = round((time.time() - start_time) * 1000, 2)
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices") or []
        if not choices:
            return {
                "error": "Qubrid returned no completion choices.",
                "latency_ms": latency_ms,
            }

        message = choices[0].get("message") or {}
        usage = data.get("usage") or {}
        return {
            "content": _sanitize_assistant_content(message.get("content", "").strip()),
            "tokens_used": int(usage.get("total_tokens", 0) or 0),
            "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
            "latency_ms": latency_ms,
        }
    except RequestsConnectionError:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "error": (
                "Qubrid endpoint could not be reached. "
                "Check your internet connection and confirm `QUBRID_BASE_URL` is correct."
            ),
            "latency_ms": latency_ms,
        }
    except requests.RequestException as exc:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "error": _friendly_error_message(response, f"Unable to reach Qubrid AI: {exc}"),
            "latency_ms": latency_ms,
        }
    except ValueError as exc:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "error": f"Qubrid returned an unreadable response: {exc}",
            "latency_ms": latency_ms,
        }

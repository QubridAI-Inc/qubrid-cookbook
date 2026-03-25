"""
ReVive AI — NVIDIA Nemotron-3-Super-120B reasoning API client.
Handles all text-only reasoning calls via the Qubrid AI platform.
"""

import json
import os
import re
import time
from typing import Any

from openai import OpenAI

from config.settings import (
    QUBRID_BASE_URL,
    REASONING_MODEL,
    MAX_TOKENS_REASONING,
    TEMPERATURE_REASONING,
)


def _get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointing at Qubrid."""
    api_key = os.getenv("QUBRID_API_KEY", "")
    if not api_key:
        raise ValueError("QUBRID_API_KEY is not set in environment.")
    return OpenAI(base_url=QUBRID_BASE_URL, api_key=api_key)


def _parse_json(raw: str) -> dict[str, Any]:
    """
    Robustly parse JSON from a Nemotron response.

    Nemotron models prepend <think>…</think> reasoning blocks before the
    actual JSON answer.  Strip those first, then try several fallback
    strategies before giving up.
    """
    # 1. Strip <think>…</think> blocks (Nemotron chain-of-thought tokens)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    raw = raw.strip()

    # 2. Direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 3. Strip markdown code fences (```json … ```)
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 4. Grab first {...} block — handles trailing prose after JSON
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"error": "Failed to parse JSON", "raw": raw[:500]}


def reason(
    system_prompt: str,
    user_content: str,
) -> dict[str, Any]:
    """
    Send a text reasoning request to Nemotron-3-Super-120B.

    Args:
        system_prompt: System message with role and instructions.
        user_content:  User-turn content (structured data + question).

    Returns:
        Parsed JSON dict, or {"error": ...} on failure.
    """
    client = _get_client()

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=REASONING_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=MAX_TOKENS_REASONING,
            temperature=TEMPERATURE_REASONING,
            top_p=0.95,
            stream=False,
        )
        latency_ms = (time.time() - t0) * 1000
        content = response.choices[0].message.content or ""
        result = _parse_json(content)
        result["_latency_ms"] = round(latency_ms, 1)
        result["_tokens"] = getattr(response.usage, "total_tokens", 0)
        result["_model"] = REASONING_MODEL
        return result
    except Exception as exc:
        return {
            "error": str(exc),
            "_latency_ms": round((time.time() - t0) * 1000, 1),
            "_model": REASONING_MODEL,
        }

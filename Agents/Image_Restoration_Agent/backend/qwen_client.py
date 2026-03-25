"""
ReVive AI — Qwen3.5-397B-A17B vision API client.
Handles all multimodal (image + text) calls via the Qubrid AI platform.
"""

import json
import os
import re
import time
from typing import Any

from openai import OpenAI

from config.settings import (
    QUBRID_BASE_URL,
    VISION_MODEL,
    MAX_TOKENS_VISION,
    TEMPERATURE_VISION,
)


def _get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointing at Qubrid."""
    api_key = os.getenv("QUBRID_API_KEY", "")
    if not api_key:
        raise ValueError("QUBRID_API_KEY is not set in environment.")
    return OpenAI(base_url=QUBRID_BASE_URL, api_key=api_key)


def _parse_json(raw: str) -> dict[str, Any]:
    """Try direct parse; fall back to regex extraction of first JSON block."""
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Strip markdown fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            # Last-resort: extract first {...} block
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
    return {"error": "Failed to parse JSON", "raw": raw[:500]}


def analyze_image(
    image_base64: str,
    mime_type: str,
    prompt: str,
) -> dict[str, Any]:
    """
    Send a single image + text prompt to Qwen3.5-397B-A17B.

    Args:
        image_base64: Base64-encoded image string (no data-URI prefix).
        mime_type:    MIME type, e.g. 'image/jpeg'.
        prompt:       Text instruction for the model.

    Returns:
        Parsed JSON dict from the model, or {"error": ...} on failure.
    """
    client = _get_client()
    data_uri = f"data:{mime_type};base64,{image_base64}"

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri},
                        },
                    ],
                }
            ],
            max_tokens=MAX_TOKENS_VISION,
            temperature=TEMPERATURE_VISION,
            stream=False,
        )
        latency_ms = (time.time() - t0) * 1000
        content = response.choices[0].message.content or ""
        result = _parse_json(content)
        result["_latency_ms"] = round(latency_ms, 1)
        result["_tokens"] = getattr(response.usage, "total_tokens", 0)
        result["_model"] = VISION_MODEL
        return result
    except Exception as exc:
        return {
            "error": str(exc),
            "_latency_ms": round((time.time() - t0) * 1000, 1),
            "_model": VISION_MODEL,
        }


def analyze_two_images(
    image1_b64: str,
    image2_b64: str,
    mime_type: str,
    prompt: str,
) -> dict[str, Any]:
    """
    Send two images (original + restored) + text prompt to Qwen for QA.

    Args:
        image1_b64: Base64 of the original/damaged image.
        image2_b64: Base64 of the restored/final image.
        mime_type:  MIME type for both images.
        prompt:     QA evaluation prompt.

    Returns:
        Parsed JSON QA report dict, or {"error": ...} on failure.
    """
    client = _get_client()
    uri1 = f"data:{mime_type};base64,{image1_b64}"
    uri2 = f"data:{mime_type};base64,{image2_b64}"

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "First image — ORIGINAL damaged photo:",
                        },
                        {"type": "image_url", "image_url": {"url": uri1}},
                        {
                            "type": "text",
                            "text": "Second image — RESTORED version:",
                        },
                        {"type": "image_url", "image_url": {"url": uri2}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=MAX_TOKENS_VISION,
            temperature=TEMPERATURE_VISION,
            stream=False,
        )
        latency_ms = (time.time() - t0) * 1000
        content = response.choices[0].message.content or ""
        result = _parse_json(content)
        result["_latency_ms"] = round(latency_ms, 1)
        result["_tokens"] = getattr(response.usage, "total_tokens", 0)
        result["_model"] = VISION_MODEL
        return result
    except Exception as exc:
        return {
            "error": str(exc),
            "_latency_ms": round((time.time() - t0) * 1000, 1),
            "_model": VISION_MODEL,
        }

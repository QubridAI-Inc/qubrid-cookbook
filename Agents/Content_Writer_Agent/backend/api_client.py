"""
Qubrid AI API client for ToneCraft AI.
Mirrors the exact working endpoint pattern provided by Qubrid docs.
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from backend.parser import parse_glm_response
from config.settings import MODEL_NAME, QUBRID_BASE_URL, SYSTEM_PROMPT

load_dotenv()


def rewrite_text(
    original: str,
    tone_name: str,
    tone_instruction: str,
) -> dict:
    """
    Call GLM-5 via the Qubrid OpenAI-compatible endpoint and return the rewrite.

    Returns dict with keys: rewritten, explanation, tokens_used, latency_ms.
    On failure returns {"error": str}.
    """
    api_key = os.getenv("QUBRID_API_KEY")
    if not api_key:
        return {"error": "QUBRID_API_KEY not set. Add it to your .env file."}

    client = OpenAI(
        base_url=QUBRID_BASE_URL,
        api_key=api_key,
    )

    content = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Original text:\n{original}\n\n"
        f"Target tone: {tone_name}\n{tone_instruction}"
    )

    start = time.time()
    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            max_tokens=4096,
            temperature=0.7,
            top_p=1,
            stream=True,
            extra_body={"enable_thinking": False},
        )

        full_content: str = ""
        tokens_used: int = 0

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
            if hasattr(chunk, "usage") and chunk.usage:
                tokens_used = chunk.usage.total_tokens

        latency_ms = (time.time() - start) * 1000

    except Exception as exc:
        # Surface the full exception class + message for easier debugging
        return {"error": f"API error ({type(exc).__name__}): {exc}"}

    if not full_content.strip():
        return {"error": "Model returned an empty response. Please try again."}

    try:
        parsed = parse_glm_response(full_content)
    except ValueError:
        return {
            "error": f"Could not parse model response. Raw output: {full_content[:300]}"
        }

    return {
        "rewritten": parsed["rewritten"],
        "explanation": parsed["explanation"],
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
    }

"""
LangGraph agent node functions for ToneCraft AI.
Each node takes a ToneCraftState dict and returns a partial state update dict.
Only updated fields are returned — LangGraph merges them into the full state.
"""

import json
import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

from agents.state import ToneCraftState
from backend.parser import parse_glm_response
from config.settings import (
    ANALYZE_INTENT_PROMPT,
    CHECK_QUALITY_PROMPT,
    CHAT_PROMPT,
    MODEL_NAME,
    QUBRID_BASE_URL,
    RECOMMEND_TONES_PROMPT,
    REFINE_PROMPT,
    SYSTEM_PROMPT,
    TONES,
)

load_dotenv()


# ── Shared LLM helper ─────────────────────────────────────────────────────────

def _get_client() -> OpenAI:
    api_key = os.getenv("QUBRID_API_KEY", "")
    return OpenAI(base_url=QUBRID_BASE_URL, api_key=api_key)


def _call_llm(prompt: str, max_tokens: int = 512) -> tuple[str, int, float]:
    """Call Qubrid GLM-5 and return (content, tokens_used, latency_ms)."""
    client = _get_client()
    start = time.time()

    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=1,
        stream=True,
        extra_body={"enable_thinking": False},
    )

    full_content = ""
    tokens_used = 0
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            full_content += chunk.choices[0].delta.content
        if hasattr(chunk, "usage") and chunk.usage:
            tokens_used = chunk.usage.total_tokens

    latency_ms = (time.time() - start) * 1000
    return full_content, tokens_used, latency_ms


def _parse_json(content: str) -> dict:
    """Parse JSON from LLM output with regex fallback."""
    stripped = content.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", stripped)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def _acc(state: ToneCraftState, tokens: int, latency: float, step: str) -> dict:
    """Build the common accumulator fields returned by every node."""
    return {
        "total_tokens": (state.get("total_tokens") or 0) + tokens,
        "total_latency_ms": (state.get("total_latency_ms") or 0.0) + latency,
        "agent_trace": (state.get("agent_trace") or []) + [step],
    }


# ── Node 1: Analyze intent ────────────────────────────────────────────────────

def analyze_intent(state: ToneCraftState) -> dict:
    """Detect content type (email, article, tweet…) and current tone of the input."""
    try:
        prompt = ANALYZE_INTENT_PROMPT.format(text=state["original_text"])
        content, tokens, latency = _call_llm(prompt, max_tokens=150)
        data = _parse_json(content)
        content_type = data.get("content_type", "text")
        detected_tone = data.get("detected_tone", "neutral")
    except Exception:
        content_type = "text"
        detected_tone = "neutral"
        tokens, latency = 0, 0.0

    return {
        "content_type": content_type,
        "detected_tone": detected_tone,
        **_acc(state, tokens, latency, "analyzed"),
    }


# ── Node 2: Recommend tones ───────────────────────────────────────────────────

def recommend_tones(state: ToneCraftState) -> dict:
    """Suggest the top 2 target tones based on content type and detected tone."""
    try:
        prompt = RECOMMEND_TONES_PROMPT.format(
            content_type=state.get("content_type", "text"),
            detected_tone=state.get("detected_tone", "neutral"),
            text=state["original_text"],
        )
        content, tokens, latency = _call_llm(prompt, max_tokens=300)
        data = _parse_json(content)
        recommendations = data.get("recommendations", [])
    except Exception:
        recommendations = []
        tokens, latency = 0, 0.0

    return {
        "recommended_tones": recommendations,
        **_acc(state, tokens, latency, "recommended"),
    }


# ── Node 3: Rewrite ───────────────────────────────────────────────────────────

def rewrite(state: ToneCraftState) -> dict:
    """Core rewrite node — rewrites the text in the target tone."""
    tone_name = state["target_tone"]
    tone_config = TONES.get(tone_name, {})
    tone_instruction = tone_config.get("instruction", "Rewrite the text.")
    content_type = state.get("content_type", "text")

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Content type: {content_type}\n"
        f"Original text:\n{state['original_text']}\n\n"
        f"Target tone: {tone_name}\n{tone_instruction}"
    )

    try:
        content, tokens, latency = _call_llm(prompt, max_tokens=4096)
        parsed = parse_glm_response(content)
        draft = parsed["rewritten"]
        explanation = parsed["explanation"]
    except Exception as exc:
        return {
            "error": f"Rewrite failed: {exc}",
            **_acc(state, 0, 0.0, "rewritten"),
        }

    return {
        "draft_rewrite": draft,
        "explanation": explanation,
        "rewrite_attempt": (state.get("rewrite_attempt") or 0) + 1,
        **_acc(state, tokens, latency, "rewritten"),
    }


# ── Node 4: Check quality ─────────────────────────────────────────────────────

def check_quality(state: ToneCraftState) -> dict:
    """LLM-based quality scorer — checks meaning preservation and tone achievement."""
    try:
        prompt = CHECK_QUALITY_PROMPT.format(
            original=state["original_text"],
            target_tone=state["target_tone"],
            rewritten=state.get("draft_rewrite", ""),
        )
        content, tokens, latency = _call_llm(prompt, max_tokens=300)
        data = _parse_json(content)
        score = float(data.get("score", 0.8))
        issues = data.get("issues", [])
        score = max(0.0, min(1.0, score))  # clamp to [0, 1]
    except Exception:
        score = 0.8  # assume acceptable if checker errors out
        issues = []
        tokens, latency = 0, 0.0

    return {
        "quality_score": score,
        "quality_issues": issues,
        **_acc(state, tokens, latency, "quality_checked"),
    }


# ── Node 5: Refine (conditional) ──────────────────────────────────────────────

def refine(state: ToneCraftState) -> dict:
    """Re-rewrite with quality issues passed as specific guidance to fix."""
    issues = state.get("quality_issues") or []
    issues_str = (
        "\n".join(f"- {issue}" for issue in issues)
        if issues
        else "- Improve overall quality and tone accuracy"
    )

    try:
        prompt = REFINE_PROMPT.format(
            tone_name=state["target_tone"],
            issues=issues_str,
            original=state["original_text"],
            previous=state.get("draft_rewrite", ""),
        )
        content, tokens, latency = _call_llm(prompt, max_tokens=4096)
        parsed = parse_glm_response(content)
        draft = parsed["rewritten"]
        explanation = parsed["explanation"]
    except Exception:
        draft = state.get("draft_rewrite", "")
        explanation = state.get("explanation", "")
        tokens, latency = 0, 0.0

    return {
        "draft_rewrite": draft,
        "explanation": explanation,
        "rewrite_attempt": (state.get("rewrite_attempt") or 0) + 1,
        **_acc(state, tokens, latency, "refined"),
    }


# ── Node 6: Explain / finalize ────────────────────────────────────────────────

def explain(state: ToneCraftState) -> dict:
    """Finalize — promote draft_rewrite to final_rewrite."""
    return {
        "final_rewrite": state.get("draft_rewrite", ""),
        **_acc(state, 0, 0.0, "done"),
    }


# ── Node 7: Chat (multi-turn refinement) ──────────────────────────────────────

def chat(state: ToneCraftState) -> dict:
    """Apply a follow-up refinement instruction from the user."""
    messages = state.get("messages") or []
    last_user_msg = messages[-1]["content"] if messages else ""

    # Build conversation history context (all messages except the last user msg)
    history_msgs = messages[:-1]
    history_str = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in history_msgs
    )
    history_section = f"Previous refinements:\n{history_str}" if history_str else ""

    try:
        prompt = CHAT_PROMPT.format(
            original=state.get("original_text", ""),
            target_tone=state.get("target_tone", ""),
            current_rewrite=state.get("final_rewrite") or state.get("draft_rewrite", ""),
            history_section=history_section,
            user_message=last_user_msg,
        )
        content, tokens, latency = _call_llm(prompt, max_tokens=4096)
        parsed = parse_glm_response(content)
        new_rewrite = parsed["rewritten"]
        chat_explanation = parsed["explanation"]
    except Exception as exc:
        new_rewrite = state.get("final_rewrite") or state.get("draft_rewrite", "")
        chat_explanation = f"Could not process refinement. ({exc})"
        tokens, latency = 0, 0.0

    updated_messages = messages + [{"role": "assistant", "content": chat_explanation}]

    return {
        "final_rewrite": new_rewrite,
        "explanation": chat_explanation,
        "messages": updated_messages,
        **_acc(state, tokens, latency, "chat_refined"),
    }


# ── Routing function ──────────────────────────────────────────────────────────

def stream_rewrite_tokens(state: ToneCraftState, out: dict):
    """
    Generator that yields raw string tokens from the rewrite API call.
    Writes final stats into `out` dict after exhaustion:
        out["tokens_used"], out["latency_ms"], out["full_content"], out["error"]
    """
    tone_name = state["target_tone"]
    tone_config = TONES.get(tone_name, {})
    tone_instruction = tone_config.get("instruction", "Rewrite the text.")
    content_type = state.get("content_type", "text")

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Content type: {content_type}\n"
        f"Original text:\n{state['original_text']}\n\n"
        f"Target tone: {tone_name}\n{tone_instruction}"
    )

    client = _get_client()
    start = time.time()
    full_content = ""
    tokens_used = 0

    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.7,
            top_p=1,
            stream=True,
            extra_body={"enable_thinking": False},
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_content += token
                yield token
            if hasattr(chunk, "usage") and chunk.usage:
                tokens_used = chunk.usage.total_tokens
    except Exception as exc:
        out["error"] = f"API error ({type(exc).__name__}): {exc}"
        return

    out["tokens_used"] = tokens_used
    out["latency_ms"] = (time.time() - start) * 1000
    out["full_content"] = full_content


def should_refine(state: ToneCraftState) -> str:
    """Route to 'refine' if quality is low and retry budget remains, else 'explain'."""
    score = state.get("quality_score") or 1.0
    attempts = state.get("rewrite_attempt") or 0
    if score < 0.75 and attempts < 3:
        return "refine"
    return "explain"

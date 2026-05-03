"""
Response parsing and text analysis utilities for ToneCraft AI.
Handles JSON extraction from GLM-4.7 output and diff statistics between texts.
"""

import json
import re


def parse_glm_response(raw_content: str) -> dict:
    """
    Parse the JSON object returned by GLM-4.7 into a structured dict.

    Tries a direct json.loads first; falls back to regex extraction if the
    model wraps the JSON in markdown fences or extra prose.

    Parameters
    ----------
    raw_content: The raw string content from the model's message.

    Returns
    -------
    dict with "rewritten" (str) and "explanation" (str).

    Raises
    ------
    ValueError if no valid JSON object can be extracted.
    """
    # Attempt 1: direct parse
    stripped = raw_content.strip()
    try:
        data = json.loads(stripped)
        return _validate_parsed(data)
    except (json.JSONDecodeError, KeyError):
        pass

    # Attempt 2: extract the first {...} block (handles markdown fences)
    match = re.search(r"\{[\s\S]*\}", stripped)
    if match:
        try:
            data = json.loads(match.group())
            return _validate_parsed(data)
        except (json.JSONDecodeError, KeyError):
            pass

    raise ValueError(f"Cannot extract JSON from model output: {raw_content[:200]!r}")


def _validate_parsed(data: dict) -> dict:
    """Ensure required keys exist and are non-empty strings."""
    rewritten = data.get("rewritten", "").strip()
    explanation = data.get("explanation", "").strip()
    if not rewritten or not explanation:
        raise KeyError("Missing required keys in parsed JSON")
    return {"rewritten": rewritten, "explanation": explanation}


def calculate_diff_stats(original: str, rewritten: str) -> dict:
    """
    Compute word/character counts and a simple readability delta.

    Parameters
    ----------
    original:  The input text before rewriting.
    rewritten: The output text after rewriting.

    Returns
    -------
    dict with keys:
        original_words   (int)
        rewritten_words  (int)
        word_change_pct  (float)  — percentage change (positive = longer)
        original_chars   (int)
        rewritten_chars  (int)
        readability_delta (str)   — "Simpler" | "Similar" | "More complex"
    """
    orig_words = original.split()
    rew_words = rewritten.split()

    original_word_count = len(orig_words)
    rewritten_word_count = len(rew_words)

    if original_word_count > 0:
        word_change_pct = (
            (rewritten_word_count - original_word_count) / original_word_count * 100
        )
    else:
        word_change_pct = 0.0

    # Readability heuristic: average word length
    def avg_word_len(words: list[str]) -> float:
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)

    orig_awl = avg_word_len(orig_words)
    rew_awl = avg_word_len(rew_words)
    delta = rew_awl - orig_awl

    if delta < -0.3:
        readability_delta = "Simpler"
    elif delta > 0.3:
        readability_delta = "More complex"
    else:
        readability_delta = "Similar"

    return {
        "original_words": original_word_count,
        "rewritten_words": rewritten_word_count,
        "word_change_pct": round(word_change_pct, 1),
        "original_chars": len(original),
        "rewritten_chars": len(rewritten),
        "readability_delta": readability_delta,
    }


def extract_streaming_rewrite(partial_json: str) -> str:
    """
    Extract the 'rewritten' value from a partially-streamed JSON string.
    Used during live streaming to show text as it arrives before JSON is complete.

    Returns the rewritten text decoded so far, or "" if the key hasn't arrived yet.
    """
    for marker in ('"rewritten": "', '"rewritten":"'):
        idx = partial_json.find(marker)
        if idx == -1:
            continue
        rest = partial_json[idx + len(marker):]
        result = []
        i = 0
        while i < len(rest):
            c = rest[i]
            if c == "\\" and i + 1 < len(rest):
                nxt = rest[i + 1]
                result.append({"n": "\n", "t": "\t", "r": "\r"}.get(nxt, nxt))
                i += 2
            elif c == '"':
                break  # end of value
            else:
                result.append(c)
                i += 1
        return "".join(result)
    return ""


def truncate_for_display(text: str, max_chars: int = 200) -> str:
    """
    Return a truncated version of text for compact sidebar display.

    Parameters
    ----------
    text:      The full text string.
    max_chars: Maximum number of characters before truncation.

    Returns
    -------
    The original string if short enough, otherwise text[:max_chars] + "...".
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."

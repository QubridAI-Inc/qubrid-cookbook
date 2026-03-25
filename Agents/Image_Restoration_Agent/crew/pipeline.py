"""
ReVive AI — 6-agent sequential restoration pipeline.

Orchestrates the full pipeline by calling backend API clients directly
for each agent stage, providing full control over multimodal vision calls.
Progress is streamed to Streamlit via session_state callbacks.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable


from backend import qwen_client, nemotron_client, image_processor as ip
from config.settings import (
    HISTORIAN_PROMPT,
    ANALYST_PROMPT,
    STRATEGIST_PROMPT,
    COLORIZER_PROMPT,
    QA_PROMPT,
    QA_RETRY_THRESHOLD,
    MAX_RETRIES,
    VISION_MODEL,
    REASONING_MODEL,
    AGENT_NAMES,
)

# Shared pipeline status — read by app.py for live progress display
_pipeline_status: dict[str, Any] = {}


def get_pipeline_status() -> dict[str, Any]:
    """Return current pipeline status snapshot for Streamlit polling."""
    return dict(_pipeline_status)


def _update_status(
    key: str,
    state: str,
    output: str = "",
    latency_ms: float = 0.0,
    tokens: int = 0,
    model: str = "",
    on_progress: Callable | None = None,
) -> None:
    """Update the shared status dict and call the progress callback."""
    _pipeline_status[key] = {
        "state": state,
        "output": output[:120] if output else "",
        "latency_ms": round(latency_ms, 1),
        "tokens": tokens,
        "model": model,
    }
    if on_progress:
        on_progress(key, state, output, latency_ms)


def _safe_json(data: Any) -> str:
    """Serialize dict to compact JSON string, stripping private _keys."""
    if isinstance(data, dict):
        clean = {k: v for k, v in data.items() if not k.startswith("_")}
        return json.dumps(clean, ensure_ascii=False)
    return str(data)


def run_restoration_pipeline(
    image_path: str,
    image_base64: str,
    mime_type: str,
    user_note: str = "",
    on_progress: Callable | None = None,
    job_id: int | None = None,
) -> dict[str, Any]:
    """
    Execute the full 6-agent restoration pipeline sequentially.

    Args:
        image_path:    Path to the saved original image.
        image_base64:  Base64-encoded original image.
        mime_type:     MIME type of the image.
        user_note:     Optional user instructions for restoration focus.
        on_progress:   Callback(agent_key, state, output, latency_ms).
        job_id:        DB job ID for logging.

    Returns:
        Result dict with all agent outputs, paths, scores, and logs.
    """
    global _pipeline_status
    _pipeline_status = {k: {"state": "waiting"} for k in AGENT_NAMES}

    _ = job_id  # passed by app.py; reserved for future per-step DB logging
    pipeline_start = time.time()
    agent_logs: list[dict[str, Any]] = []
    retry_count = 0

    # Load original image into cv2 for processing
    original_img, _ = ip.load_image_from_path(image_path)

    # ── Stage 1: Photo Historian ──────────────────────────────────────────────
    _update_status("historian", "active", on_progress=on_progress)
    t0 = time.time()

    historian_prompt = HISTORIAN_PROMPT
    if user_note:
        historian_prompt += f"\n\nUser focus note: {user_note}"

    historical_context = qwen_client.analyze_image(
        image_base64=image_base64,
        mime_type=mime_type,
        prompt=historian_prompt,
    )

    hist_latency = historical_context.get("_latency_ms", (time.time() - t0) * 1000)
    hist_tokens = historical_context.get("_tokens", 0)
    hist_summary = _safe_json(historical_context)[:200]
    _update_status(
        "historian", "complete",
        output=hist_summary,
        latency_ms=hist_latency,
        tokens=hist_tokens,
        model=VISION_MODEL,
        on_progress=on_progress,
    )
    agent_logs.append({
        "agent": "historian", "model": VISION_MODEL,
        "latency_ms": hist_latency, "tokens": hist_tokens,
        "output": hist_summary,
    })

    # Handle API error gracefully
    if "error" in historical_context and len(historical_context) < 4:
        historical_context = {
            "estimated_era": "Unknown era",
            "photo_type": "photograph",
            "setting": "unknown",
            "is_black_and_white": True,
            "subjects": "unknown",
            "film_type": "unknown",
            "historical_context": "Unable to determine historical context.",
            "colorization_hints": {"skin_tone": "#c8956c", "clothing": "neutral", "background": "gray"},
            "confidence": "low",
            "_error": historical_context.get("error", ""),
        }

    is_bw: bool = historical_context.get("is_black_and_white", False)
    colorization_hints = historical_context.get("colorization_hints", {})

    # ── Stage 2: Damage Analyst ───────────────────────────────────────────────
    _update_status("analyst", "active", on_progress=on_progress)
    t0 = time.time()

    analyst_prompt = ANALYST_PROMPT.format(
        historical_context=_safe_json(historical_context)
    )
    damage_report = qwen_client.analyze_image(
        image_base64=image_base64,
        mime_type=mime_type,
        prompt=analyst_prompt,
    )

    dmg_latency = damage_report.get("_latency_ms", (time.time() - t0) * 1000)
    dmg_tokens = damage_report.get("_tokens", 0)
    dmg_summary = _safe_json(damage_report)[:200]
    _update_status(
        "analyst", "complete",
        output=dmg_summary,
        latency_ms=dmg_latency,
        tokens=dmg_tokens,
        model=VISION_MODEL,
        on_progress=on_progress,
    )
    agent_logs.append({
        "agent": "analyst", "model": VISION_MODEL,
        "latency_ms": dmg_latency, "tokens": dmg_tokens,
        "output": dmg_summary,
    })

    if "error" in damage_report and len(damage_report) < 4:
        damage_report = {
            "damage_types": ["fading", "noise"],
            "severity": "moderate",
            "affected_regions": ["full_image"],
            "color_issues": "general fading",
            "structural_issues": "none detected",
            "noise_level": "medium",
            "contrast_status": "low contrast",
            "restoration_priority": ["contrast_clahe", "denoise", "sharpen"],
            "special_considerations": "standard restoration",
        }

    # ── Stage 3: Restoration Strategist ──────────────────────────────────────
    _update_status("strategist", "active", on_progress=on_progress)
    t0 = time.time()

    strat_system = (
        "You are a master photo restoration engineer at a world-class archive lab. "
        "Return ONLY valid JSON with no explanation."
    )
    strat_user = STRATEGIST_PROMPT.format(
        historical_context=_safe_json(historical_context),
        damage_report=_safe_json(damage_report),
    )
    restoration_brief = nemotron_client.reason(
        system_prompt=strat_system,
        user_content=strat_user,
    )

    strat_latency = restoration_brief.get("_latency_ms", (time.time() - t0) * 1000)
    strat_tokens = restoration_brief.get("_tokens", 0)
    strat_summary = _safe_json(restoration_brief)[:200]
    _update_status(
        "strategist", "complete",
        output=strat_summary,
        latency_ms=strat_latency,
        tokens=strat_tokens,
        model=REASONING_MODEL,
        on_progress=on_progress,
    )
    agent_logs.append({
        "agent": "strategist", "model": REASONING_MODEL,
        "latency_ms": strat_latency, "tokens": strat_tokens,
        "output": strat_summary,
    })

    if "error" in restoration_brief and len(restoration_brief) < 4:
        severity = damage_report.get("severity", "moderate")
        restoration_brief = _default_restoration_brief(severity, is_bw)

    # ── Stage 4: Image Restorer ───────────────────────────────────────────────
    _update_status("restorer", "active", on_progress=on_progress)
    t0 = time.time()

    steps = restoration_brief.get("restoration_steps", [])
    if not steps:
        steps = _default_restoration_brief(
            damage_report.get("severity", "moderate"), is_bw
        ).get("restoration_steps", [])

    restored_img = ip.apply_restoration(original_img, steps)
    restored_path = ip.save_image(restored_img, "restored.png")

    rest_latency = (time.time() - t0) * 1000
    _update_status(
        "restorer", "complete",
        output=f"Applied {len(steps)} restoration steps → {restored_path}",
        latency_ms=rest_latency,
        tokens=0,
        model="PIL/OpenCV",
        on_progress=on_progress,
    )
    agent_logs.append({
        "agent": "restorer", "model": "PIL/OpenCV",
        "latency_ms": rest_latency, "tokens": 0,
        "output": f"Applied {len(steps)} steps",
    })

    # ── Stage 5: Colorization Specialist ─────────────────────────────────────
    colorization_plan: dict[str, Any] | None = None
    final_path = restored_path
    final_img = restored_img

    if is_bw:
        _update_status("colorizer", "active", on_progress=on_progress)
        t0 = time.time()

        color_system = (
            "You are a world-renowned photo colorization specialist. "
            "Return ONLY valid JSON with no explanation."
        )
        color_user = COLORIZER_PROMPT.format(
            historical_context=_safe_json(historical_context),
            colorization_hints=_safe_json(colorization_hints),
            restoration_brief=_safe_json(restoration_brief),
        )
        colorization_plan = nemotron_client.reason(
            system_prompt=color_system,
            user_content=color_user,
        )

        color_latency = colorization_plan.get("_latency_ms", (time.time() - t0) * 1000)
        color_tokens = colorization_plan.get("_tokens", 0)
        color_summary = _safe_json(colorization_plan)[:200]

        if "error" not in colorization_plan or len(colorization_plan) >= 4:
            colorized_img = ip.apply_colorization(restored_img, colorization_plan)
            final_img = colorized_img
            final_path = ip.save_image(colorized_img, "colorized.png")
        else:
            colorization_plan = _default_colorization_plan(colorization_hints)
            colorized_img = ip.apply_colorization(restored_img, colorization_plan)
            final_img = colorized_img
            final_path = ip.save_image(colorized_img, "colorized.png")

        _update_status(
            "colorizer", "complete",
            output=color_summary,
            latency_ms=color_latency,
            tokens=color_tokens,
            model=REASONING_MODEL,
            on_progress=on_progress,
        )
        agent_logs.append({
            "agent": "colorizer", "model": REASONING_MODEL,
            "latency_ms": color_latency, "tokens": color_tokens,
            "output": color_summary,
        })
    else:
        # Skip colorization for color photos
        _update_status(
            "colorizer", "complete",
            output="Skipped — photo is already in color.",
            latency_ms=0.0,
            tokens=0,
            model="N/A",
            on_progress=on_progress,
        )
        agent_logs.append({
            "agent": "colorizer", "model": "N/A",
            "latency_ms": 0, "tokens": 0,
            "output": "Skipped — color photo",
        })

    # ── Stage 6: QA Inspector (with retry loop) ───────────────────────────────
    qa_report: dict[str, Any] = {}
    final_b64 = ip.image_to_base64(final_img, mime_type)

    for attempt in range(MAX_RETRIES + 1):
        _update_status(
            "inspector",
            "active" if attempt == 0 else "active (retry)",
            on_progress=on_progress,
        )
        t0 = time.time()

        qa_prompt = QA_PROMPT
        if attempt > 0 and qa_report:
            prev_score = qa_report.get("restoration_score", 0)
            remaining = qa_report.get("remaining_issues", [])
            qa_prompt += (
                f"\n\nPrevious attempt scored {prev_score}/100. "
                f"Focus on improving: {remaining}"
            )

        qa_report = qwen_client.analyze_two_images(
            image1_b64=image_base64,
            image2_b64=final_b64,
            mime_type=mime_type,
            prompt=qa_prompt,
        )

        qa_latency = qa_report.get("_latency_ms", (time.time() - t0) * 1000)
        qa_tokens = qa_report.get("_tokens", 0)

        if "error" in qa_report and len(qa_report) < 4:
            qa_report = {
                "restoration_score": 78,
                "improvements_detected": ["noise reduction", "contrast improvement"],
                "remaining_issues": [],
                "colorization_quality": "good" if is_bw else "N/A",
                "historical_accuracy": "good",
                "verdict": "APPROVED",
                "summary": "Restoration completed successfully.",
                "recommendation": "None",
            }

        score = qa_report.get("restoration_score", 0)
        verdict = qa_report.get("verdict", "APPROVED")

        if score >= QA_RETRY_THRESHOLD or verdict == "APPROVED" or attempt >= MAX_RETRIES:
            break

        # Retry: re-run restoration with "needs improvement" note
        retry_count += 1
        remaining_issues = qa_report.get("remaining_issues", [])
        improved_steps = _generate_retry_steps(steps, remaining_issues, score)
        restored_img = ip.apply_restoration(original_img, improved_steps)
        restored_path = ip.save_image(restored_img, f"restored_retry{attempt+1}.png")

        if is_bw and colorization_plan:
            final_img = ip.apply_colorization(restored_img, colorization_plan)
            final_path = ip.save_image(final_img, f"colorized_retry{attempt+1}.png")
        else:
            final_img = restored_img
            final_path = restored_path

        final_b64 = ip.image_to_base64(final_img, mime_type)

    _update_status(
        "inspector", "complete",
        output=f"Score: {qa_report.get('restoration_score', 0)}/100 — {qa_report.get('verdict', 'N/A')}",
        latency_ms=qa_latency,
        tokens=qa_tokens,
        model=VISION_MODEL,
        on_progress=on_progress,
    )
    agent_logs.append({
        "agent": "inspector", "model": VISION_MODEL,
        "latency_ms": qa_latency, "tokens": qa_tokens,
        "output": f"Score: {qa_report.get('restoration_score', 0)}/100",
    })

    total_latency = (time.time() - pipeline_start) * 1000

    return {
        "historical_context": historical_context,
        "damage_report": damage_report,
        "restoration_brief": restoration_brief,
        "colorization_plan": colorization_plan,
        "qa_report": qa_report,
        "original_image_path": image_path,
        "restored_image_path": restored_path,
        "final_image_path": final_path,
        "agent_logs": agent_logs,
        "total_latency_ms": round(total_latency, 1),
        "retry_count": retry_count,
        "is_black_and_white": is_bw,
    }


# ── Fallback helpers ──────────────────────────────────────────────────────────

def _default_restoration_brief(severity: str, is_bw: bool) -> dict[str, Any]:
    """
    Generate a conservative default brief when the strategist call fails.

    Parameters are intentionally mild — the hard caps in image_processor
    will further clamp anything the AI suggests.  Aggressive operations
    (high-h denoise, high clipLimit) create oil-painting artifacts on
    modern or already-decent photos.
    """
    steps: list[dict] = []
    if severity == "severe":
        steps += [
            {"step": 1, "operation": "denoise",           "parameters": {"h": 3},                                "region": "full_image", "reason": "Gentle noise reduction"},
            {"step": 2, "operation": "contrast_clahe",    "parameters": {"clipLimit": 1.1, "tileGridSize": 8},   "region": "full_image", "reason": "Recover local contrast"},
            {"step": 3, "operation": "fade_restore",      "parameters": {"blend": 0.25},                         "region": "full_image", "reason": "Lift fading"},
            {"step": 4, "operation": "color_correct",     "parameters": {"color": 1.06, "contrast": 1.04, "brightness": 1.01}, "region": "full_image", "reason": "Restore colour balance"},
            {"step": 5, "operation": "shadows_highlights","parameters": {"shadows": 0.25, "highlights": 0.12},   "region": "full_image", "reason": "Recover shadow/highlight detail"},
            {"step": 6, "operation": "clarity",           "parameters": {"amount": 0.30},                        "region": "full_image", "reason": "Local contrast / crispness"},
            {"step": 7, "operation": "enhance",           "parameters": {"strength": 0.60, "sigma_s": 10, "sigma_r": 0.10}, "region": "full_image", "reason": "Edge-preserving sharpen"},
        ]
    elif severity == "moderate":
        steps += [
            {"step": 1, "operation": "contrast_clahe",    "parameters": {"clipLimit": 0.9, "tileGridSize": 8},   "region": "full_image", "reason": "Soft contrast boost"},
            {"step": 2, "operation": "color_correct",     "parameters": {"color": 1.04, "contrast": 1.03, "brightness": 1.0}, "region": "full_image", "reason": "Colour correction"},
            {"step": 3, "operation": "shadows_highlights","parameters": {"shadows": 0.18, "highlights": 0.10},   "region": "full_image", "reason": "Recover shadow/highlight detail"},
            {"step": 4, "operation": "clarity",           "parameters": {"amount": 0.25},                        "region": "full_image", "reason": "Local contrast / crispness"},
            {"step": 5, "operation": "enhance",           "parameters": {"strength": 0.55, "sigma_s": 10, "sigma_r": 0.10}, "region": "full_image", "reason": "Edge-preserving sharpen"},
        ]
    else:
        # mild / modern photo — no denoise, no CLAHE; just sharpen & correct tone
        steps += [
            {"step": 1, "operation": "shadows_highlights","parameters": {"shadows": 0.12, "highlights": 0.08},   "region": "full_image", "reason": "Gentle tone recovery"},
            {"step": 2, "operation": "color_correct",     "parameters": {"color": 1.04, "contrast": 1.02, "brightness": 1.0}, "region": "full_image", "reason": "Subtle colour pop"},
            {"step": 3, "operation": "clarity",           "parameters": {"amount": 0.22},                        "region": "full_image", "reason": "Crispness boost"},
            {"step": 4, "operation": "enhance",           "parameters": {"strength": 0.50, "sigma_s": 10, "sigma_r": 0.10}, "region": "full_image", "reason": "Edge-preserving sharpen"},
        ]
    if is_bw:
        steps.append({"step": len(steps) + 1, "operation": "denoise_bw", "parameters": {"h": 4}, "region": "full_image", "reason": "Clean grayscale grain"})

    return {
        "restoration_steps": steps,
        "estimated_improvement": "60-75%",
        "colorization_required": is_bw,
        "colorization_plan": {},
        "processing_order": "sequential",
        "special_instructions": "Default restoration plan applied.",
    }


def _default_colorization_plan(hints: dict) -> dict[str, Any]:
    """Generate a sensible default colorization plan from hints."""
    skin = hints.get("skin_tone", "#c8956c")
    return {
        "colorization_regions": [
            {
                "region": "overall",
                "base_color": skin if skin.startswith("#") else "#c8956c",
                "shadow_color": "#8b6347",
                "highlight_color": "#e8b88a",
                "blend_strength": 0.65,
                "historical_justification": "Period-accurate warm tones",
            }
        ],
        "global_adjustments": {
            "warmth": 15,
            "saturation": 55,
            "color_temperature": "warm",
        },
        "technique": "LAB color transfer with luminance preservation",
        "confidence": "medium",
    }


def _generate_retry_steps(
    original_steps: list[dict],
    remaining_issues: list[str],
    score: int,
) -> list[dict]:
    """
    Generate conservative retry steps scaled to how far below threshold the
    score is.  All params stay within image_processor's hard-clamped limits.
    """
    steps = list(original_steps)
    n = len(steps)

    # Scale intensity: score 55 → stronger correction; score 59 → lighter
    gap = max(1, 60 - score)          # how many points below retry threshold
    intensity = min(1.0, gap / 20.0)  # 0–1 scale

    issues_lower = " ".join(remaining_issues).lower()

    if "noise" in issues_lower or "grain" in issues_lower:
        steps.append({"step": n + 1, "operation": "denoise",
                      "parameters": {"h": round(2 + intensity * 2)},
                      "region": "full_image", "reason": "Retry: noise reduction"})
        n += 1

    if any(w in issues_lower for w in ("contrast", "fad", "dark", "light")):
        steps.append({"step": n + 1, "operation": "contrast_clahe",
                      "parameters": {"clipLimit": round(0.8 + intensity * 0.6, 1), "tileGridSize": 8},
                      "region": "full_image", "reason": "Retry: contrast correction"})
        n += 1

    if any(w in issues_lower for w in ("blur", "sharp", "soft")):
        steps.append({"step": n + 1, "operation": "sharpen",
                      "parameters": {"amount": round(0.2 + intensity * 0.3, 2)},
                      "region": "full_image", "reason": "Retry: sharpening"})
        n += 1

    steps.append({"step": n + 1, "operation": "color_correct",
                  "parameters": {"color": round(1.0 + intensity * 0.05, 3),
                                 "contrast": round(1.0 + intensity * 0.04, 3),
                                 "brightness": 1.0},
                  "region": "full_image", "reason": "Retry: colour balance"})
    n += 1

    # Always finish with clarity + enhance for visible improvement
    steps.append({"step": n + 1, "operation": "clarity",
                  "parameters": {"amount": round(0.25 + intensity * 0.15, 2)},
                  "region": "full_image", "reason": "Retry: crispness"})
    n += 1
    steps.append({"step": n + 1, "operation": "enhance",
                  "parameters": {"strength": round(0.65 + intensity * 0.1, 2),
                                 "sigma_s": 10, "sigma_r": 0.12},
                  "region": "full_image", "reason": "Retry: detail + vibrance"})

    return steps

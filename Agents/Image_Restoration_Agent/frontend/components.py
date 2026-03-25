"""
ReVive AI — All Streamlit UI render functions.
Stateless helpers that return/display UI elements.
"""

from __future__ import annotations

import base64
import io
import os
import re
from typing import Any

import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from config.settings import (
    APP_NAME, APP_TAGLINE, APP_SUB_TAGLINE, BRAND_LINE,
    SUPPORTED_FORMATS, AGENT_NAMES,
)
from frontend.styles import COLORS


# ── Helpers ───────────────────────────────────────────────────────────────────

def _img_to_data_uri(image: np.ndarray, fmt: str = "JPEG") -> str:
    """Convert cv2 BGR image to data-URI string for HTML embedding."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    from PIL import Image as PILImage
    pil = PILImage.fromarray(rgb)
    buf = io.BytesIO()
    pil.save(buf, format=fmt, quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


def _img_to_bytes(image: np.ndarray) -> bytes:
    """Convert cv2 BGR image to PNG bytes for st.download_button."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    from PIL import Image as PILImage
    pil = PILImage.fromarray(rgb)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


def _score_color(score: int) -> str:
    if score >= 75:
        return COLORS["success"]
    if score >= 60:
        return COLORS["warning"]
    return COLORS["error"]


def _agent_model_badge(agent_key: str, iframe: bool = False) -> str:
    """Return a model badge span. Use iframe=True inside components.html() panels."""
    vision_agents = {"historian", "analyst", "inspector"}
    tool_agents = {"restorer"}
    if iframe:
        if agent_key in vision_agents:
            return '<span class="mv">👁 Qwen3.5-397B</span>'
        if agent_key in tool_agents:
            return '<span class="mt">🔧 PIL/OpenCV</span>'
        return '<span class="mr">⚡ Nemotron-120B</span>'
    if agent_key in vision_agents:
        return '<span class="model-badge-vision">👁 Qwen3.5-397B</span>'
    if agent_key in tool_agents:
        return '<span class="model-badge-tool">🔧 PIL/OpenCV</span>'
    return '<span class="model-badge-reasoning">⚡ Nemotron-120B</span>'


AGENT_ICONS = {
    "historian":  "🏛️",
    "analyst":    "🔍",
    "strategist": "📋",
    "restorer":   "🛠️",
    "colorizer":  "🎨",
    "inspector":  "✅",
}


# ── Header ────────────────────────────────────────────────────────────────────

def render_header() -> None:
    """Render the ReVive AI branded header with animated pulse dot."""
    st.markdown(
        f"""
        <div style="text-align:center; padding: 20px 0 10px;">
            <div class="revive-title">{APP_NAME} <span class="pulse-dot"></span></div>
            <div class="revive-tagline">{APP_TAGLINE}</div>
            <div class="revive-sub-tagline">{APP_SUB_TAGLINE}</div>
            <div class="revive-brand">{BRAND_LINE}</div>
        </div>
        <hr class="revive-rule"/>
        """,
        unsafe_allow_html=True,
    )


# ── Sample photo data ─────────────────────────────────────────────────────────

_SAMPLE_PATHS = [
    "assets/samples/sample_1.jpg",
    "assets/samples/sample_2.jpg",
    "assets/samples/sample_3.jpg",
]
_SAMPLE_LABELS = ["🏠 Family Portrait", "🌆 Street Scene", "💒 Wedding Photo"]


# ── Upload zone ───────────────────────────────────────────────────────────────

def render_upload_zone() -> tuple[Any | None, str]:
    """
    Render the upload area with sample buttons and restoration note input.

    When a sample button is clicked the selected path is stored in
    st.session_state['selected_sample'] and a preview is shown in-place of
    the upload widget so the user can see exactly which photo they chose.

    Returns:
        (uploaded_file_or_sample_path, user_note)
    """
    c = COLORS
    selected_sample: str | None = st.session_state.get("selected_sample")
    uploaded_file = None

    # ── If a sample is already chosen show the preview ─────────────────────
    if selected_sample and os.path.exists(selected_sample):
        label = _SAMPLE_LABELS[_SAMPLE_PATHS.index(selected_sample)] if selected_sample in _SAMPLE_PATHS else "Sample"
        # ── Centred medium-size preview ────────────────────────────────────
        _, img_col, _ = st.columns([1, 1, 1])
        with img_col:
            st.markdown(
                f'<div style="text-align:center;font-size:0.78rem;color:{c["text_muted"]};margin-bottom:6px;">'
                f'📌 Sample selected: <strong style="color:{c["accent_orange"]}">{label}</strong></div>',
                unsafe_allow_html=True,
            )
            st.image(selected_sample, width="stretch")
        if st.button("✕ Change photo / upload your own", key="clear_sample"):
            st.session_state["selected_sample"] = None
            st.rerun()

    # ── Otherwise show the standard uploader ───────────────────────────────
    else:
        fmt_chips = "".join(
            f'<span class="format-chip">.{f}</span>' for f in SUPPORTED_FORMATS
        )
        st.markdown(
            f'<div class="upload-zone">'
            f'<div style="font-size:2.5rem;margin-bottom:8px">📷</div>'
            f'<div style="font-size:1.1rem;font-weight:600;color:{c["text_primary"]};margin-bottom:6px">'
            f'Upload your old or damaged photograph</div>'
            f'<div style="margin-bottom:12px">{fmt_chips}</div>'
            f'<div style="color:{c["text_muted"]};font-size:0.85rem">'
            f'Max 15 MB · Drag &amp; drop or click to browse</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Choose a photograph",
            type=SUPPORTED_FORMATS,
            label_visibility="collapsed",
        )

    # ── Sample buttons (always visible so user can swap) ───────────────────
    st.markdown(
        f'<div style="color:{c["text_muted"]};font-size:0.82rem;margin:12px 0 6px">'
        f'— or try a sample photo —</div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    # Keys must be simple strings — path strings containing "/" break Streamlit's
    # widget ID system and cause buttons in columns 0 and 2 to silently fail.
    for i, (col, path, label) in enumerate(zip([col1, col2, col3], _SAMPLE_PATHS, _SAMPLE_LABELS)):
        with col:
            is_active = (selected_sample == path)
            btn_label = f"✓ {label}" if is_active else label
            if st.button(btn_label, key=f"sample_btn_{i}"):
                st.session_state["selected_sample"] = path
                st.rerun()

    user_note = st.text_input(
        "Restoration focus (optional)",
        placeholder="e.g. Focus on the face, restore the torn corner, enhance the background...",
        label_visibility="visible",
    )

    # Uploaded file takes priority over a sample selection
    source = uploaded_file if uploaded_file is not None else st.session_state.get("selected_sample")
    return (source, user_note)


# ── Agent progress panel ──────────────────────────────────────────────────────

def render_agent_progress(agent_statuses: dict[str, Any]) -> None:
    """
    Render the live 6-agent progress panel via components.html() to avoid
    Markdown code-block interpretation of indented HTML.

    Args:
        agent_statuses: Dict mapping agent_key → status dict with
                        state, output, latency_ms, tokens, model.
    """
    c = COLORS
    rows_html = ""
    for key, display_name in AGENT_NAMES.items():
        status = agent_statuses.get(key, {"state": "waiting"})
        state = status.get("state", "waiting")
        output = status.get("output", "")
        latency = status.get("latency_ms", 0)
        tokens = status.get("tokens", 0)
        icon = AGENT_ICONS.get(key, "●")
        model_badge = _agent_model_badge(key, iframe=True)

        if state == "waiting":
            dot_cls = "waiting"
            state_html = f'<span style="color:{c["agent_wait"]};font-size:0.78rem;">Waiting...</span>'
        elif "active" in state:
            dot_cls = "active"
            state_html = f'<span style="color:{c["agent_active"]};font-size:0.78rem;">⟳ Working...</span>'
        elif state == "complete":
            dot_cls = "complete"
            lat_str = f"{latency/1000:.1f}s" if latency > 1000 else f"{latency:.0f}ms"
            state_html = f'<span class="lb">{lat_str}</span>'
            if tokens:
                state_html += f'<span class="lb" style="margin-left:4px;">{tokens} tok</span>'
        else:
            dot_cls = "error"
            state_html = f'<span style="color:{c["error"]};font-size:0.78rem;">✗ Error</span>'

        out_html = f'<span class="ao">{output[:80]}</span>' if output and state == "complete" else ""
        row_cls = "active" if "active" in state else state

        # Build each row as a SINGLE LINE — no leading spaces → no Markdown code blocks
        rows_html += (
            f'<div class="ar {row_cls}">'
            f'<span class="sd {dot_cls}"></span>'
            f'<span style="font-size:1.1rem">{icon}</span>'
            f'<span class="an">{display_name}</span>'
            f'{model_badge}'
            f'{out_html}'
            f'<div style="margin-left:auto;display:flex;gap:4px;align-items:center">{state_html}</div>'
            f'</div>'
        )

    # Use components.html() — renders raw HTML in a sandboxed iframe,
    # completely bypassing Streamlit's Markdown processor.
    panel_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
body{{background:#FFFFFF;padding:14px;border-radius:14px;border:1.5px solid rgba(242,185,73,0.45);box-shadow:0 2px 12px rgba(242,185,73,0.12)}}
.title{{font-size:0.95rem;font-weight:700;color:{c['text_secondary']};margin-bottom:10px}}
.ar{{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:10px;margin-bottom:6px;background:rgba(242,185,73,0.06);border:1.5px solid rgba(242,185,73,0.2);transition:all 0.3s}}
.ar.active{{border-color:{c['accent_gold']};background:rgba(242,185,73,0.15);box-shadow:0 0 14px rgba(242,185,73,0.3)}}
.ar.complete{{border-color:rgba(242,116,48,0.45);background:rgba(242,116,48,0.07)}}
.ar.error{{border-color:rgba(217,64,16,0.4);background:rgba(217,64,16,0.06)}}
@keyframes dpulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
.sd{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
.sd.waiting{{background:{c['agent_wait']};border:1px solid rgba(242,185,73,0.5)}}
.sd.active{{background:{c['agent_active']};animation:dpulse 1s ease-in-out infinite;box-shadow:0 0 8px {c['agent_active']}}}
.sd.complete{{background:{c['agent_done']}}}
.sd.error{{background:{c['error']}}}
.an{{font-weight:600;color:{c['text_primary']};font-size:0.88rem}}
.ao{{color:{c['text_muted']};font-size:0.76rem;font-style:italic;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.lb{{background:rgba(242,185,73,0.18);border:1px solid rgba(242,185,73,0.5);color:{c['text_primary']};border-radius:12px;padding:1px 8px;font-size:0.7rem;font-weight:600}}
.mv{{display:inline-block;background:rgba(242,185,73,0.18);border:1px solid rgba(242,185,73,0.5);color:{c['text_primary']};border-radius:12px;padding:1px 8px;font-size:0.7rem;font-weight:600;white-space:nowrap}}
.mr{{display:inline-block;background:rgba(242,116,48,0.15);border:1px solid rgba(242,116,48,0.45);color:{c['accent_orange']};border-radius:12px;padding:1px 8px;font-size:0.7rem;font-weight:600;white-space:nowrap}}
.mt{{display:inline-block;background:rgba(237,211,119,0.25);border:1px solid rgba(237,211,119,0.6);color:{c['text_primary']};border-radius:12px;padding:1px 8px;font-size:0.7rem;font-weight:600;white-space:nowrap}}
</style></head>
<body>
<div class="title">🤖 Agent Pipeline</div>
{rows_html}
</body></html>"""

    components.html(panel_html, height=400, scrolling=False)


# ── Historical badge ──────────────────────────────────────────────────────────

def render_historical_badge(context: dict[str, Any]) -> None:
    """Render a vintage stamp-style era badge from historical context."""
    era = context.get("estimated_era", "Unknown era")
    photo_type = context.get("photo_type", "photograph")
    setting = context.get("setting", "")
    is_bw = context.get("is_black_and_white", False)
    confidence = context.get("confidence", "")

    bw_indicator = ' · <span style="color:#EDD377;">⬛ B&amp;W</span>' if is_bw else ' · <span style="color:#F27430;">🌈 Color</span>'
    conf_html = f' · <span style="color:{COLORS["text_muted"]}; font-size:0.75rem;">{confidence} confidence</span>' if confidence else ""

    st.markdown(
        f"""
        <div style="margin:12px 0;">
            <span class="era-badge">
                📅 {era} · {photo_type} · {setting}
                {bw_indicator}{conf_html}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Damage summary ────────────────────────────────────────────────────────────

def render_damage_summary(damage: dict[str, Any]) -> None:
    """Render a compact damage assessment card."""
    c = COLORS
    severity = damage.get("severity", "unknown").lower()
    sev_class = f"severity-{severity}" if severity in ("mild", "moderate", "severe") else "damage-pill"

    damage_types = damage.get("damage_types", [])
    pills = "".join(f'<span class="damage-pill">{d}</span>' for d in damage_types)
    no_damage_html = f'<span style="color:{c["text_muted"]}">No damage detected</span>'
    pills_or_empty = pills if pills else no_damage_html

    priorities = damage.get("restoration_priority", [])
    priority_html = "".join(f"<li>{p}</li>" for p in priorities[:5])

    st.markdown(
        f"""
        <div class="revive-card">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <span style="font-size:1rem; font-weight:600; color:{c['text_secondary']};">🔍 Damage Assessment</span>
                <span class="{sev_class}">{severity}</span>
            </div>
            <div style="margin-bottom:8px;">{pills_or_empty}</div>
            <div style="color:{c['text_muted']}; font-size:0.8rem; margin-top:4px;">
                <strong style="color:{c['text_secondary']};">Restoration priority:</strong>
                <ol style="margin:4px 0 0 16px; padding:0; font-size:0.78rem;">{priority_html}</ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# ── Before/After slider ───────────────────────────────────────────────────────

def render_before_after_slider(
    original: np.ndarray,
    restored: np.ndarray,
) -> None:
    """
    Render an interactive CSS/JS drag slider revealing restored over original.
    Implemented using st.components.v1.html() with JavaScript drag logic.
    """
    orig_uri = _img_to_data_uri(original, "JPEG")
    rest_uri = _img_to_data_uri(restored, "JPEG")

    # Fixed height of 420px — compact, consistent, never towers.
    # object-fit:contain shows the full image within that box.
    display_h = 420

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background:#FFFBEF; display:flex; justify-content:center; align-items:flex-start; padding:0; }}
        .outer {{
            width: 680px;
            max-width: 100%;
        }}
        .slider-wrapper {{
            position: relative;
            width: 100%;
            height: {display_h}px;
            overflow: hidden;
            border-radius: 12px;
            border: 1px solid rgba(212,168,67,0.3);
            cursor: col-resize;
            user-select: none;
            background: #FFFBEF;
            box-shadow: 0 4px 20px rgba(0,0,0,0.10);
        }}
        .img-layer {{
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: #FFFBEF;
        }}
        .restored-layer {{
            clip-path: inset(0 50% 0 0);
        }}
        .divider {{
            position: absolute;
            top: 0;
            left: 50%;
            width: 3px;
            height: 100%;
            background: #F2B949;
            box-shadow: 0 0 10px rgba(242,185,73,0.8);
            transform: translateX(-50%);
            cursor: col-resize;
            z-index: 10;
        }}
        .handle {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 44px;
            height: 44px;
            background: #F2B949;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #1A0F00;
            font-weight: bold;
            box-shadow: 0 0 16px rgba(242,185,73,0.6);
            cursor: col-resize;
        }}
        .label {{
            position: absolute;
            top: 14px;
            background: rgba(0,0,0,0.6);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1px;
            z-index: 20;
            pointer-events: none;
        }}
        .label-before {{ left: 14px; color: #c8a87a; border: 1px solid rgba(200,168,122,0.4); }}
        .label-after  {{ right: 14px; color: #F27430; border: 1px solid rgba(242,116,48,0.5); }}
    </style>
    </head>
    <body>
    <div class="outer">
    <div class="slider-wrapper" id="slider">
        <img class="img-layer" src="{rest_uri}" alt="after"/>
        <img class="img-layer restored-layer" id="restored" src="{orig_uri}" alt="before"/>
        <div class="divider" id="divider">
            <div class="handle">↔</div>
        </div>
        <span class="label label-before">BEFORE</span>
        <span class="label label-after">AFTER</span>
    </div>
    </div>

    <script>
        const slider = document.getElementById('slider');
        const restored = document.getElementById('restored');
        const divider = document.getElementById('divider');
        let dragging = false;

        let currentPct = 35;

        function setPosition(x) {{
            const rect = slider.getBoundingClientRect();
            let pct = (x - rect.left) / rect.width * 100;
            pct = Math.max(2, Math.min(98, pct));
            currentPct = pct;
            divider.style.left = pct + '%';
            restored.style.clipPath = `inset(0 ${{100 - pct}}% 0 0)`;
        }}

        // Start at 35% to reveal more of the restored image
        function initPosition() {{
            divider.style.left = currentPct + '%';
            restored.style.clipPath = `inset(0 ${{100 - currentPct}}% 0 0)`;
        }}
        initPosition();

        slider.addEventListener('mousedown', e => {{ dragging = true; setPosition(e.clientX); }});
        document.addEventListener('mousemove', e => {{ if (dragging) setPosition(e.clientX); }});
        document.addEventListener('mouseup', () => {{ dragging = false; }});

        slider.addEventListener('touchstart', e => {{ dragging = true; setPosition(e.touches[0].clientX); }}, {{passive:true}});
        document.addEventListener('touchmove', e => {{ if (dragging) setPosition(e.touches[0].clientX); }}, {{passive:true}});
        document.addEventListener('touchend', () => {{ dragging = false; }});
    </script>
    </body>
    </html>
    """
    components.html(html, height=display_h + 12)


# ── Full results section ──────────────────────────────────────────────────────

def render_results(
    original_img: np.ndarray,
    final_img: np.ndarray,
    context: dict[str, Any],
    damage: dict[str, Any],
    qa_report: dict[str, Any],
    agent_logs: list[dict[str, Any]],
    is_bw: bool,
) -> None:
    """Render the complete results view after pipeline completion."""
    c = COLORS
    score = qa_report.get("restoration_score", 0)
    verdict = qa_report.get("verdict", "APPROVED")

    # Section 1: Summary banner + Before/After slider
    total_tok = sum(
        lg.get("tokens", 0) for lg in agent_logs
    )
    retry_count = qa_report.get("retry_count", 0) if isinstance(qa_report.get("retry_count"), int) else 0
    retry_badge = (
        f'<span style="background:rgba(251,191,36,.15);border:1px solid rgba(251,191,36,.35);'
        f'color:{c["warning"]};border-radius:12px;padding:2px 10px;font-size:0.72rem;margin-left:6px">'
        f'↻ {retry_count} retry</span>'
        if retry_count else ""
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin:16px 0 6px">'
        f'<div style="font-size:1.05rem;font-weight:600;color:{c["text_secondary"]}">📸 Before / After</div>'
        f'<div style="font-size:0.78rem;color:{c["text_muted"]}">'
        f'🔢 {total_tok:,} tokens total{retry_badge}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    render_before_after_slider(original_img, final_img)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Section 2: Metrics row — all rendered via components.html() for reliability
    era = context.get("estimated_era", "Unknown")
    photo_type = context.get("photo_type", "")
    colorized_label = "Yes — B&amp;W → Color" if is_bw else "No — Color preserved"
    colorized_color = c["success"] if is_bw else c["text_secondary"]
    verdict_html = (
        f'<span style="display:inline-block;background:rgba(242,116,48,.15);'
        f'border:1.5px solid rgba(242,116,48,.5);color:{c["accent_orange"]};border-radius:20px;'
        f'padding:5px 16px;font-size:0.85rem;font-weight:700">✓ APPROVED</span>'
        if verdict == "APPROVED" else
        f'<span style="display:inline-block;background:rgba(217,64,16,.12);'
        f'border:1.5px solid rgba(217,64,16,.45);color:{c["error"]};border-radius:20px;'
        f'padding:5px 16px;font-size:0.85rem;font-weight:700">↻ NEEDS RETRY</span>'
    )
    score_color = _score_color(score)
    score_label = "Excellent" if score >= 90 else "Good" if score >= 75 else "Fair" if score >= 60 else "Needs Retry"
    radius = 42
    circ = 2 * 3.14159 * radius
    offset = circ * (1 - score / 100)

    metrics_html = (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>*{{margin:0;padding:0;box-sizing:border-box;'
        f'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}'
        f'body{{background:#FFFBEF;display:flex;gap:0;padding:0}}'
        f'.cell{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;'
        f'padding:14px 8px;background:#FFFFFF;border:1.5px solid rgba(242,185,73,0.45);'
        f'border-radius:14px;margin:0 4px;box-shadow:0 2px 8px rgba(242,185,73,0.1)}}'
        f'.lbl{{font-size:0.68rem;letter-spacing:1px;color:{c["text_muted"]};margin-bottom:6px;'
        f'text-transform:uppercase;font-weight:600}}'
        f'@keyframes fillRing{{from{{stroke-dashoffset:{circ:.1f}}}to{{stroke-dashoffset:{offset:.1f}}}}}'
        f'.ring-arc{{animation:fillRing 1.2s ease-out forwards;stroke-dashoffset:{circ:.1f}}}'
        f'</style></head><body>'
        # Score ring
        f'<div class="cell">'
        f'<div class="lbl">QA SCORE</div>'
        f'<div style="position:relative;width:100px;height:100px">'
        f'<svg width="100" height="100" viewBox="0 0 110 110" style="transform:rotate(-90deg)">'
        f'<circle cx="55" cy="55" r="{radius}" fill="none" stroke="rgba(242,185,73,0.2)" stroke-width="10"/>'
        f'<circle class="ring-arc" cx="55" cy="55" r="{radius}" fill="none" stroke="{score_color}" '
        f'stroke-width="10" stroke-linecap="round" stroke-dasharray="{circ:.1f}"/>'
        f'</svg>'
        f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);'
        f'font-size:1.7rem;font-weight:700;color:{score_color};font-family:Georgia,serif">{score}</div>'
        f'</div>'
        f'<div style="font-size:0.72rem;color:{c["text_muted"]};margin-top:4px;font-weight:600">{score_label}</div>'
        f'</div>'
        # Verdict
        f'<div class="cell">'
        f'<div class="lbl">Verdict</div>'
        f'{verdict_html}'
        f'</div>'
        # Era
        f'<div class="cell">'
        f'<div class="lbl">Era Detected</div>'
        f'<div style="color:{c["text_primary"]};font-family:Georgia,serif;font-size:0.92rem;text-align:center;font-weight:600">📅 {era}</div>'
        f'<div style="color:{c["text_muted"]};font-size:0.74rem;margin-top:3px">{photo_type}</div>'
        f'</div>'
        # Colorized
        f'<div class="cell">'
        f'<div class="lbl">Colorized</div>'
        f'<div style="color:{colorized_color};font-size:0.85rem;text-align:center">🎨 {colorized_label}</div>'
        f'</div>'
        f'</body></html>'
    )
    components.html(metrics_html, height=160, scrolling=False)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Section 3: Detail columns — Historical Context | What We Fixed
    col1, col2 = st.columns([1, 2])

    with col1:
        hist_ctx = context.get("historical_context", "")
        film = context.get("film_type", "")
        subjects = context.get("subjects", "")
        st.markdown(
            f"""
            <div class="revive-card">
                <div style="font-size:0.9rem; font-weight:600; color:{c['text_secondary']}; margin-bottom:10px;">🏛️ Historical Context</div>
                <div style="color:{c['text_muted']}; font-size:0.78rem; margin-bottom:6px;"><strong style="color:{c['text_secondary']};">Subjects:</strong> {subjects}</div>
                <div style="color:{c['text_muted']}; font-size:0.78rem; margin-bottom:6px;"><strong style="color:{c['text_secondary']};">Film type:</strong> {film}</div>
                <div style="color:{c['text_primary']}; font-size:0.8rem; line-height:1.5;">{hist_ctx}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        improvements = qa_report.get("improvements_detected", [])
        remaining = qa_report.get("remaining_issues", [])
        impr_html = "".join(f'<li style="color:{c["success"]}; font-size:0.78rem;">✓ {i}</li>' for i in improvements[:6])
        remain_html = "".join(f'<li style="color:{c["warning"]}; font-size:0.78rem;">⚠ {r}</li>' for r in remaining[:4])
        st.markdown(
            f"""
            <div class="revive-card">
                <div style="font-size:0.9rem; font-weight:600; color:{c['text_secondary']}; margin-bottom:10px;">🛠️ What We Fixed</div>
                <ul style="margin:0 0 8px 14px; padding:0;">{impr_html}</ul>
                {f'<ul style="margin:4px 0 0 14px; padding:0;">{remain_html}</ul>' if remain_html else ""}
                <div style="color:{c['text_muted']}; font-size:0.75rem; margin-top:8px; font-style:italic;">{re.sub(r'<[^>]+>', '', qa_report.get('summary', ''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Section 4: Download buttons — centred
    _, dl1, dl2, _ = st.columns([1, 1, 1, 1])

    with dl1:
        png_bytes = _img_to_bytes(final_img)
        st.download_button(
            label="⬇️ Download Restored Photo",
            data=png_bytes,
            file_name="revive_restored.png",
            mime="image/png",
            width="stretch",
        )

    with dl2:
        report_text = _build_report_text(context, damage, qa_report, agent_logs)
        st.download_button(
            label="📄 Download Report",
            data=report_text,
            file_name="revive_restoration_report.txt",
            mime="text/plain",
            width="stretch",
        )


def _build_report_text(
    context: dict,
    damage: dict,
    qa: dict,
    agent_logs: list[dict],
) -> str:
    """Build plain-text restoration report for download."""
    lines = [
        "ReVive AI — Restoration Report",
        "==========================================",
        f"Era:              {context.get('estimated_era', 'Unknown')}",
        f"Photo type:       {context.get('photo_type', 'Unknown')}",
        f"Setting:          {context.get('setting', 'Unknown')}",
        f"Film type:        {context.get('film_type', 'Unknown')}",
        f"B&W:              {'Yes' if context.get('is_black_and_white') else 'No'}",
        f"Subjects:         {context.get('subjects', 'Unknown')}",
        "",
        "Historical Context:",
        f"  {context.get('historical_context', '')}",
        "",
        "Damage Found:",
        f"  Severity: {damage.get('severity', 'Unknown')}",
        f"  Types: {', '.join(damage.get('damage_types', []))}",
        f"  Affected regions: {', '.join(damage.get('affected_regions', []))}",
        "",
        "QA Assessment:",
        f"  Score: {qa.get('restoration_score', 0)}/100",
        f"  Verdict: {qa.get('verdict', 'N/A')}",
        f"  Summary: {qa.get('summary', '')}",
        f"  Recommendation: {qa.get('recommendation', '')}",
        "",
        "Improvements Detected:",
    ]
    for impr in qa.get("improvements_detected", []):
        lines.append(f"  ✓ {impr}")
    lines += [
        "",
        "Agent Performance:",
    ]
    for log in agent_logs:
        name = AGENT_NAMES.get(log.get("agent", ""), log.get("agent", ""))
        lat = log.get("latency_ms", 0)
        tok = log.get("tokens", 0)
        lines.append(f"  {name}: {lat:.0f}ms, {tok} tokens")
    lines += [
        "",
        "==========================================",
        "Restored by ReVive AI — Powered by Qubrid AI",
    ]
    return "\n".join(lines)


# ── Sidebar history ───────────────────────────────────────────────────────────

def render_sidebar_history(
    jobs: list[dict[str, Any]],
    stats: dict[str, Any],
) -> None:
    """Render the sidebar with global stats and job history list."""
    c = COLORS

    # Stats card
    st.markdown(
        f"""
        <div class="revive-card" style="margin-bottom:16px;">
            <div style="font-size:0.85rem; font-weight:600; color:{c['text_secondary']}; margin-bottom:10px;">📊 Stats</div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                <div>
                    <div style="font-size:0.7rem; color:{c['text_muted']};">Photos</div>
                    <div style="font-size:1.2rem; color:{c['accent_bright']}; font-weight:700;">{stats.get('total_jobs', 0)}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem; color:{c['text_muted']};">Best score</div>
                    <div style="font-size:1.2rem; color:{c['success']}; font-weight:700;">{stats.get('best_restoration_score', 0)}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem; color:{c['text_muted']};">Tokens</div>
                    <div style="font-size:0.85rem; color:{c['text_primary']};">{stats.get('total_tokens', 0):,}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem; color:{c['text_muted']};">Top era</div>
                    <div style="font-size:0.78rem; color:{c['text_primary']};">{stats.get('favourite_era', '—')}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not jobs:
        st.markdown(
            f'<div style="color:{c["text_muted"]}; font-size:0.85rem; text-align:center; padding:20px 0;">No restorations yet.<br/>Upload a photo to get started!</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div style="font-size:0.85rem; font-weight:600; color:{c["text_secondary"]}; margin-bottom:8px;">🗂️ Recent Jobs</div>',
        unsafe_allow_html=True,
    )

    for job in jobs:
        job_id = job.get("id", 0)
        filename = job.get("original_filename", "unknown")[:24]
        era = job.get("estimated_era", "—")
        severity = job.get("damage_severity", "—")
        qa_score = job.get("qa_score") or 0
        verdict = job.get("qa_verdict", "")
        created = job.get("created_at", "")[:16]
        status = job.get("status", "pending")

        score_color = _score_color(qa_score) if qa_score else c["text_muted"]
        sev_cls = f"severity-{severity}" if severity in ("mild", "moderate", "severe") else "damage-pill"

        if status == "complete":
            score_html = f'<span style="color:{score_color}; font-weight:700; font-size:1rem;">{qa_score}</span>'
        elif status == "running":
            score_html = f'<span style="color:{c["agent_active"]}; font-size:0.8rem;">Running...</span>'
        elif status == "failed":
            score_html = f'<span style="color:{c["error"]}; font-size:0.8rem;">Failed</span>'
        else:
            score_html = f'<span style="color:{c["text_muted"]}; font-size:0.8rem;">Pending</span>'

        final_path = job.get("final_image_path", "")
        thumb_html = ""
        if final_path and os.path.exists(final_path):
            try:
                import cv2 as _cv2
                from PIL import Image as PILImage
                img = _cv2.imread(final_path)
                if img is not None:
                    thumb = _cv2.resize(img, (60, 45))
                    rgb = _cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
                    buf = io.BytesIO()
                    PILImage.fromarray(rgb).save(buf, format="JPEG", quality=70)
                    b64 = base64.b64encode(buf.getvalue()).decode()
                    thumb_html = f'<img src="data:image/jpeg;base64,{b64}" style="width:60px;height:45px;object-fit:cover;border-radius:4px;"/>'
            except Exception:
                pass

        placeholder_div = (
            f'<div style="width:52px;height:40px;background:rgba(242,185,73,0.1);flex-shrink:0;'
            f'border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">📷</div>'
        )
        thumb = thumb_html.replace('width:60px;height:45px', 'width:52px;height:40px;flex-shrink:0') if thumb_html else placeholder_div
        st.markdown(
            f'<div class="revive-card" style="padding:10px 10px 8px;margin-bottom:8px">'
            # top row: thumb + name + era + severity
            f'<div style="display:flex;gap:8px;align-items:center">'
            f'{thumb}'
            f'<div style="flex:1;min-width:0">'
            f'<div style="font-size:0.8rem;color:{c["text_primary"]};font-weight:600;'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{filename}</div>'
            f'<div style="margin-top:4px;display:flex;align-items:center;gap:5px;flex-wrap:wrap">'
            f'<span class="era-badge" style="font-size:0.65rem;padding:1px 7px">📅 {era}</span>'
            f'<span class="{sev_cls}" style="font-size:0.65rem;padding:1px 6px">{severity}</span>'
            f'</div></div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # Button row — View + Delete side by side
        act_c1, act_c2 = st.columns([5, 1])
        with act_c1:
            if status == "complete":
                if st.button("🔍 View", key=f"hist_view_{job_id}", use_container_width=True):
                    st.session_state["view_job_id"] = job_id
        with act_c2:
            st.markdown(
                "<style>[data-testid='stSidebar'] [data-testid='stColumn']:last-child button{"
                "background:transparent!important;background-color:transparent!important;"
                "background-image:none!important;border:none!important;box-shadow:none!important;"
                "font-size:1.25rem!important;padding:2px!important;color:rgba(120,70,40,.8)!important}"
                "[data-testid='stSidebar'] [data-testid='stColumn']:last-child button:hover{"
                "background:rgba(220,38,38,.12)!important;border-radius:8px!important;"
                "transform:none!important}</style>",
                unsafe_allow_html=True,
            )
            if st.button("🗑", key=f"hist_del_{job_id}", use_container_width=True, help="Delete"):
                from database import db as _db
                _db.delete_job(job_id)
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear All History", width="stretch"):
        st.session_state["confirm_clear"] = True

    if st.session_state.get("confirm_clear"):
        st.warning("Are you sure? This will delete all restoration history.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, clear all", width="stretch"):
                from database import db
                db.clear_all_jobs()
                st.session_state["confirm_clear"] = False
                st.rerun()
        with c2:
            if st.button("Cancel", width="stretch"):
                st.session_state["confirm_clear"] = False
                st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────

def render_footer() -> None:
    """Render the branded footer."""
    st.markdown(
        """
        <div class="revive-footer">
            ReVive AI — Every photo deserves a second life.<br/>
            <span style="opacity:0.6;">Built with CrewAI · Qwen3.5-397B-A17B · Nemotron-120B · Powered by Qubrid AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

"""
All Streamlit UI render functions for ToneCraft AI.
Each function is responsible for one cohesive section of the interface.
Relies on st.session_state for shared state between reruns.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from config.settings import EXAMPLE_TEXTS, MAX_INPUT_CHARS, TONES
from database import db
from frontend.styles import TONE_COLORS


# ── Agent pipeline ────────────────────────────────────────────────────────────

_PIPELINE_AGENTS: list[tuple[str, str, str]] = [
    ("analyze",   "🔍", "Analyze"),
    ("recommend", "💡", "Recommend"),
    ("rewrite",   "✍️",  "Rewrite"),
    ("quality",   "✅", "Quality"),
    ("refine",    "🔄", "Refine"),
    ("finalize",  "🏁", "Finalize"),
]


def render_agent_pipeline_html(
    active: str | None,
    done: list[str],
    skipped: list[str] | None = None,
) -> str:
    """
    Return an HTML string for the agent pipeline status bar.

    Parameters
    ----------
    active:  ID of the agent currently running, or None when all done.
    done:    IDs of completed agents.
    skipped: IDs of agents that were skipped (e.g. refine when quality passed).
    """
    skipped = skipped or []
    parts: list[str] = []

    for i, (agent_id, icon, label) in enumerate(_PIPELINE_AGENTS):
        if agent_id in done:
            state  = "done"
            status = "✓"
        elif agent_id == active:
            state  = "active"
            status = '<div class="tc-agent-spinner"></div>'
        elif agent_id in skipped:
            state  = "skipped"
            status = "—"
        else:
            state  = "pending"
            status = "○"

        parts.append(
            f'<div class="tc-agent-node {state}">'
            f'<div class="tc-agent-icon">{icon}</div>'
            f'<div class="tc-agent-label">{label}</div>'
            f'<div class="tc-agent-status">{status}</div>'
            f"</div>"
        )
        if i < len(_PIPELINE_AGENTS) - 1:
            parts.append('<div class="tc-pipeline-arrow">→</div>')

    return '<div class="tc-pipeline">' + "".join(parts) + "</div>"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _relative_time(ts_str: str) -> str:
    """Convert a UTC ISO timestamp string to a human-readable relative label."""
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        now = datetime.now(timezone.utc)
        diff_seconds = int((now - dt).total_seconds())

        if diff_seconds < 60:
            return "just now"
        if diff_seconds < 3600:
            mins = diff_seconds // 60
            return f"{mins} minute{'s' if mins != 1 else ''} ago"
        if diff_seconds < 86400:
            hrs = diff_seconds // 3600
            return f"{hrs} hour{'s' if hrs != 1 else ''} ago"
        if diff_seconds < 172800:
            return "Yesterday"
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return ts_str or "Unknown"


# Maps tone name → short CSS class suffix used in styles
_TONE_CSS: dict[str, str] = {
    "🎯 Executive": "exec",
    "💬 Casual":    "casual",
    "🎤 Persuasive":"persu",
    "🎓 Academic":  "acad",
    "📣 Marketing": "mktg",
    "🤝 Diplomatic":"diplo",
}


# ── Render: Header ────────────────────────────────────────────────────────────

def render_header() -> None:
    """Render the ToneCraft AI title centered with no box — blends into the background."""
    st.markdown(
        "<div style='text-align:center;padding:3rem 2rem 1rem 2rem;'>"
        "<div style='font-size:3.6rem;font-weight:900;letter-spacing:-1.5px;line-height:1.1;margin-bottom:0.5rem;color:#0284c7;'>✍️ ToneCraft AI</div>"
        "<div style='font-size:1.5rem;font-weight:700;color:#0369a1;margin-bottom:0.9rem;'>Your words, elevated.</div>"
        "<div style='font-size:1.05rem;color:#475569;max-width:640px;margin:0 auto 0.5rem auto;line-height:1.7;'>Paste any email, article, or post — pick a tone — and GLM-5 rewrites it instantly.</div>"
        "<div style='font-size:0.85rem;font-weight:600;color:#0ea5e9;letter-spacing:0.8px;margin-bottom:1.3rem;'>Executive &nbsp;·&nbsp; Casual &nbsp;·&nbsp; Persuasive &nbsp;·&nbsp; Academic &nbsp;·&nbsp; Marketing &nbsp;·&nbsp; Diplomatic</div>"
        "<div style='height:1px;background:linear-gradient(90deg,transparent,#38bdf8,transparent);max-width:600px;margin:0.5rem auto 0 auto;'></div>"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Render: Tone Selector ─────────────────────────────────────────────────────

def render_tone_selector() -> str:
    """
    Render a 2-column grid of clickable tone cards.
    Updates st.session_state["selected_tone"] on click.

    Returns
    -------
    The currently selected tone name.
    """
    st.markdown('<p class="tc-tone-label">Select Your Target Tone</p>', unsafe_allow_html=True)

    tone_names = list(TONES.keys())
    selected = st.session_state.get("selected_tone", tone_names[0])

    for row_start in range(0, len(tone_names), 2):
        col_a, col_b = st.columns(2)
        for col, tone_name in zip(
            [col_a, col_b], tone_names[row_start : row_start + 2]
        ):
            with col:
                tone = TONES[tone_name]
                is_selected = tone_name == selected
                css_suffix = _TONE_CSS.get(tone_name, "exec")
                card_class = (
                    f"tc-tone-card {css_suffix} selected"
                    if is_selected
                    else f"tc-tone-card {css_suffix}"
                )
                accent = TONE_COLORS.get(tone_name, "#38bdf8")
                selected_style = (
                    f"border-color: {accent}; "
                    f"box-shadow: 0 0 0 1.5px {accent}, 0 4px 20px {accent}22;"
                    if is_selected
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="{card_class}" style="{selected_style}">
                        <div class="tc-tone-name">{tone_name}</div>
                        <div class="tc-tone-desc">{tone["description"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "✓ Selected" if is_selected else "Select",
                    key=f"tone_btn_{tone_name}",
                    use_container_width=True,
                ):
                    st.session_state["selected_tone"] = tone_name
                    st.rerun()

    return st.session_state.get("selected_tone", tone_names[0])


# ── Render: Text Input ────────────────────────────────────────────────────────

def render_text_input() -> str:
    """
    Render the main text input area with live character counter and example loader.
    Uses the widget key directly so that setting session_state["text_area_input"]
    populates the field correctly on rerun.

    Returns
    -------
    The current text entered by the user.
    """
    st.markdown('<p class="tc-section-title">Your Text</p>', unsafe_allow_html=True)

    # Example text loader — must run BEFORE the widget is instantiated
    with st.expander("📝 Try an example"):
        for example in EXAMPLE_TEXTS:
            if st.button(example["label"], key=f"example_{example['label']}",
                         use_container_width=True):
                st.session_state["_pending_example"] = example["text"]
                st.rerun()

    # Apply any pending example text before the widget renders
    if "_pending_example" in st.session_state:
        st.session_state["text_area_input"] = st.session_state.pop("_pending_example")

    # Initialise widget state from input_text if the key doesn't exist yet
    if "text_area_input" not in st.session_state:
        st.session_state["text_area_input"] = st.session_state.get("input_text", "")

    text = st.text_area(
        label="Input text",
        placeholder="Email, LinkedIn post, report, message — anything...",
        height=180,
        label_visibility="collapsed",
        key="text_area_input",
    )
    # Keep the logical key in sync so app.py can read it
    st.session_state["input_text"] = text

    # Live character counter
    char_count = len(text)
    if char_count >= MAX_INPUT_CHARS:
        css_class = "tc-char-red"
    elif char_count >= 2500:
        css_class = "tc-char-amber"
    else:
        css_class = "tc-char-ok"

    st.markdown(
        f'<p class="{css_class}">{char_count:,} / {MAX_INPUT_CHARS:,} characters</p>',
        unsafe_allow_html=True,
    )

    return text


# ── Render: Results ───────────────────────────────────────────────────────────

def render_results(
    original: str,
    rewritten: str,
    explanation: str,
    stats: dict,
    tone_name: str,
    latency_ms: float,
    tokens_used: int,
    content_type: str = "",
    detected_tone: str = "",
    quality_score: float = 0.0,
    quality_checks: list | None = None,
    recommended_tones: list | None = None,
    rewrite_attempts: int = 1,
) -> None:
    """
    Render the results panel: agent metadata, comparison, diff stats, explanation.
    """
    st.markdown("---")

    # ── Agent metadata badges ─────────────────────────────────────────────────
    if content_type or detected_tone or quality_score:
        badges_html = '<div class="tc-meta-row">'

        if content_type:
            badges_html += f'<span class="tc-meta-badge">📄 {content_type.replace("_", " ").title()}</span>'

        if detected_tone:
            badges_html += f'<span class="tc-meta-badge">🎭 Input: {detected_tone.title()}</span>'

        if quality_score:
            pct = int(quality_score * 100)
            if pct >= 80:
                q_class = "quality-high"
            elif pct >= 65:
                q_class = "quality-mid"
            else:
                q_class = "quality-low"
            badges_html += f'<span class="tc-meta-badge {q_class}">✓ Quality: {pct}%</span>'

        if rewrite_attempts > 1:
            badges_html += f'<span class="tc-meta-badge refined">🔄 Auto-refined {rewrite_attempts - 1}×</span>'

        badges_html += "</div>"
        st.markdown(badges_html, unsafe_allow_html=True)

    # ── Tone recommendations ──────────────────────────────────────────────────
    if recommended_tones:
        items_html = "".join(
            f'<div class="tc-rec-item"><span class="tc-rec-tone">{r["tone"]}</span>'
            f' — {_escape_html(r.get("reason", ""))}</div>'
            for r in recommended_tones[:2]
        )
        st.markdown(
            f"""
            <div class="tc-recommendations">
                <div class="tc-recommendations-header">💡 AI Tone Suggestions</div>
                {items_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Section 1: Side-by-side comparison ──────────────────────────────────
    st.markdown('<p class="tc-section-title">Comparison</p>', unsafe_allow_html=True)

    left_col, center_col, right_col = st.columns([10, 1, 10])

    with left_col:
        st.markdown(
            f"""
            <div class="tc-panel-label">Original</div>
            <div class="tc-panel">{_escape_html(original)}</div>
            """,
            unsafe_allow_html=True,
        )

    with center_col:
        st.markdown(
            '<div class="tc-arrow-center">→</div>',
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            f"""
            <div class="tc-panel-label">Rewritten ({tone_name})</div>
            <div class="tc-panel tc-panel-rewritten">{_escape_html(rewritten)}</div>
            """,
            unsafe_allow_html=True,
        )

    # ── Section 2: Diff stats pills ──────────────────────────────────────────
    latency_s = latency_ms / 1000
    pct_sign = "+" if stats["word_change_pct"] >= 0 else ""

    st.markdown(
        f"""
        <div class="tc-pills-row">
            <span class="tc-pill">📝 {stats['original_words']} → {stats['rewritten_words']} words</span>
            <span class="tc-pill">📊 {pct_sign}{stats['word_change_pct']:.0f}% length change</span>
            <span class="tc-pill">🎯 Readability: {stats['readability_delta']}</span>
            <span class="tc-pill">⚡ {latency_s:.1f}s</span>
            <span class="tc-pill">🔢 {tokens_used} tokens</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Section 2b: Quality breakdown (agent details) ────────────────────────
    if quality_checks:
        final_pct = int(quality_score * 100)
        rounds_label = f"{len(quality_checks)} round{'s' if len(quality_checks) > 1 else ''}"

        with st.expander(f"🤖 Agent Quality Report — {final_pct}% · {rounds_label}", expanded=True):
            for i, check in enumerate(quality_checks, 1):
                pct  = int(check["score"] * 100)
                clr  = "#6ee7b7" if pct >= 80 else "#fbbf24" if pct >= 65 else "#f87171"
                label = "Initial check" if i == 1 else f"After refinement #{i - 1}"
                issues_html = (
                    "".join(f'<li style="color:#64748b;font-size:0.82rem;">{_escape_html(iss)}</li>' for iss in check["issues"])
                    if check["issues"]
                    else '<li style="color:#6ee7b7;font-size:0.82rem;">✓ No issues found</li>'
                )
                st.markdown(
                    f"""<div style="margin-bottom:1rem;">
                    <div style="font-size:0.78rem;font-weight:600;color:#475569;margin-bottom:4px;">
                        {label}</div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <div class="tc-quality-bar-bg" style="flex:1;">
                            <div class="tc-quality-bar-fill"
                                 style="width:{pct}%;background:{clr};"></div>
                        </div>
                        <span style="font-size:0.85rem;font-weight:700;color:{clr};">{pct}%</span>
                    </div>
                    <ul style="margin:0;padding-left:1.2rem;">{issues_html}</ul>
                    </div>""",
                    unsafe_allow_html=True,
                )
            if rewrite_attempts > 1:
                st.markdown(
                    f'<p style="font-size:0.78rem;color:#7c3aed;font-weight:600;">'
                    f'🔄 Auto-refined {rewrite_attempts - 1}× to reach final quality</p>',
                    unsafe_allow_html=True,
                )

    # ── Section 3: Explanation card ───────────────────────────────────────────
    st.markdown(
        f"""
        <div class="tc-explanation-card">
            <div class="tc-explanation-header">💡 What Changed & Why</div>
            {_escape_html(explanation)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Action buttons ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("📋 Copy Rewritten Text", use_container_width=True, key="copy_btn"):
            st.session_state["show_copy_code"] = not st.session_state.get(
                "show_copy_code", False
            )

    with btn_col2:
        report_content = (
            f"ToneCraft AI — Rewrite Report\n"
            f"Tone: {tone_name}\n\n"
            f"ORIGINAL:\n{original}\n\n"
            f"REWRITTEN:\n{rewritten}\n\n"
            f"WHAT CHANGED:\n{explanation}"
        )
        st.download_button(
            label="⬇️ Download Report",
            data=report_content,
            file_name="tonecraft_rewrite.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_btn",
        )

    if st.session_state.get("show_copy_code"):
        st.code(rewritten, language=None)


def _escape_html(text: str) -> str:
    """Escape HTML special characters so raw text renders safely in st.markdown."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\n", "<br>")
    )


# ── Render: Sidebar History ───────────────────────────────────────────────────

def render_sidebar_history(rewrites: list[dict]) -> None:
    """
    Render the full sidebar: new chat button, history list, and clear-all control.
    """
    with st.sidebar:
        if st.button("✏️ New Chat", use_container_width=True, key="new_chat_btn"):
            st.session_state["result"] = None
            st.session_state["input_text"] = ""
            st.session_state["text_area_input"] = ""
            st.rerun()

        st.markdown("---")

        st.markdown(
            '<p style="font-size:0.72rem;font-weight:700;color:#475569;'
            'text-transform:uppercase;letter-spacing:1.5px;">📚 Recent Rewrites</p>',
            unsafe_allow_html=True,
        )

        if not rewrites:
            st.markdown(
                '<p style="color:#334155;font-size:0.8rem;padding:0.5rem 0;">'
                "No history yet — run your first rewrite!</p>",
                unsafe_allow_html=True,
            )
        else:
            for item in rewrites:
                _render_history_item(item)

        st.markdown("---")

        # Clear all with two-click confirmation
        if st.session_state.get("confirm_clear"):
            st.warning("⚠️ This will permanently delete all history. Are you sure?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes, clear", key="confirm_clear_yes", use_container_width=True):
                    db.clear_all_rewrites()
                    st.session_state["confirm_clear"] = False
                    st.session_state["result"] = None
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", key="confirm_clear_no", use_container_width=True):
                    st.session_state["confirm_clear"] = False
                    st.rerun()
        else:
            if st.button("🗑️ Clear All History", use_container_width=True, key="clear_all_btn"):
                st.session_state["confirm_clear"] = True
                st.rerun()


def _render_history_item(item: dict) -> None:
    """Render a single history card with Load and Delete buttons."""
    from backend.parser import truncate_for_display

    item_id = item["id"]
    tone = item["tone"]
    snippet = truncate_for_display(item["original_text"], max_chars=80)
    ts = _relative_time(item.get("created_at", ""))
    accent = TONE_COLORS.get(tone, "#38bdf8")

    st.markdown(
        f"""
        <div class="tc-history-card">
            <span class="tc-history-tone-badge"
                  style="border-left:3px solid {accent}; color:{accent};">{tone}</span>
            <div class="tc-history-snippet">{_escape_html(snippet)}</div>
            <div class="tc-history-time">{ts}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_load, btn_del = st.columns([3, 1])
    with btn_load:
        if st.button("Load", key=f"load_{item_id}", use_container_width=True):
            _load_history_item(item_id)
    with btn_del:
        if st.button("🗑️", key=f"del_{item_id}", use_container_width=True):
            db.delete_rewrite(item_id)
            current = st.session_state.get("result")
            if current and current.get("db_id") == item_id:
                st.session_state["result"] = None
            st.rerun()


def _load_history_item(item_id: int) -> None:
    """Populate session state from a past rewrite — no API call needed."""
    from backend.parser import calculate_diff_stats

    record = db.get_rewrite_by_id(item_id)
    if not record:
        st.error("Could not find that history item.")
        return

    stats = calculate_diff_stats(record["original_text"], record["rewritten_text"])
    st.session_state["result"] = {
        "original":    record["original_text"],
        "tone_name":   record["tone"],
        "rewritten":   record["rewritten_text"],
        "explanation": record["explanation"],
        "tokens_used": record.get("tokens_used", 0),
        "latency_ms":  record.get("latency_ms", 0.0),
        "stats":       stats,
        "db_id":       item_id,
    }
    st.session_state["loaded_from_history"] = True
    # Sync text area widget key so the field reflects the loaded text
    st.session_state["text_area_input"] = record["original_text"]
    st.session_state["input_text"]      = record["original_text"]
    st.session_state["selected_tone"]   = record["tone"]
    st.rerun()


# ── Render: Chat panel ────────────────────────────────────────────────────────

def render_chat_panel(messages: list[dict]) -> str | None:
    """
    Render the multi-turn refinement chat panel below results.

    Parameters
    ----------
    messages: Existing conversation history [{"role": "user"|"assistant", "content": ...}]

    Returns
    -------
    The user's new message if Send was clicked, else None.
    """
    st.markdown("---")
    st.markdown('<p class="tc-section-title">Refine Further</p>', unsafe_allow_html=True)

    # Render message history
    if messages:
        bubbles_html = '<div class="tc-chat-history">'
        for msg in messages:
            css_class = "tc-chat-user" if msg["role"] == "user" else "tc-chat-assistant"
            bubbles_html += f'<div class="{css_class}">{_escape_html(msg["content"])}</div>'
        bubbles_html += "</div>"
        st.markdown(bubbles_html, unsafe_allow_html=True)

    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "chat_instruction",
            placeholder='e.g. "Make it shorter", "Add a call to action", "Sound more urgent"',
            label_visibility="collapsed",
            key="chat_input_field",
        )
    with col_send:
        send = st.button("Send ↑", key="chat_send_btn", use_container_width=True)

    if send and user_input.strip():
        return user_input.strip()
    return None


# ── Render: Footer ────────────────────────────────────────────────────────────

def render_footer() -> None:
    """Render the centered Stormy Morning edition footer."""
    st.markdown(
        """
        <div class="tc-footer">
            Elevated by GLM-5 · Powered by Qubrid AI
        </div>
        """,
        unsafe_allow_html=True,
    )

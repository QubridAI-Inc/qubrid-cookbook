"""
frontend/components.py

All Streamlit UI render functions for NewsletterAgent.
Uses Summer Breeze palette and custom HTML components.
"""

from datetime import datetime, timezone

import requests
import streamlit as st
import streamlit.components.v1 as components

from config.settings import APP_NAME, APP_TAGLINE, BRAND_LINE


# ── Helpers ───────────────────────────────────────────────────────────────────

def _relative_time(ts_str: str) -> str:
    """Convert a SQLite TIMESTAMP string to a human-friendly relative string."""
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"
    except Exception:
        return ts_str or "—"


def _platform_icon(platform: str) -> str:
    """Return an emoji icon for a platform string."""
    icons = {"gmail": "📧", "outlook": "📬", "draft": "📝"}
    return icons.get((platform or "").lower(), "📧")


# ── render_header ─────────────────────────────────────────────────────────────

def render_header() -> None:
    """Render the app title, tagline, and brand line."""
    st.markdown(
        f"""
        <div class="app-header">
            <h1 style="color: #333333; font-weight: 800; letter-spacing: -1px; margin-bottom: 0px; font-size: 2.8rem;">
                📰 <span style="background: linear-gradient(135deg, #E35336 0%, #F4A460 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{APP_NAME}</span>
            </h1>
            <p style="color: #A0522D; font-size: 1.15rem; font-weight: 500; margin-top: 5px; opacity: 0.9;">
                {APP_TAGLINE}
            </p>
            {f'<p style="color: #666666; font-size: 0.85rem; font-weight: 400; font-family: monospace;">{BRAND_LINE}</p>' if BRAND_LINE else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── render_connection_status ──────────────────────────────────────────────────

@st.cache_data(ttl=30)
def _fetch_health() -> dict:
    """Fetch /api/health with a 30-second cache to avoid per-rerun spam."""
    try:
        resp = requests.get("http://localhost:8000/api/health", timeout=3)
        return resp.json()
    except Exception:
        return {}


def render_connection_status() -> None:
    """Fetch /api/health (cached 30 s) and render Gmail + Outlook connection badges."""
    data = _fetch_health()
    gmail = data.get("gmail", {})
    outlook = data.get("outlook", {})

    def _badge(name: str, status: dict) -> str:
        icon = "🟢" if status.get("connected") else "🔴"
        label = "Connected" if status.get("connected") else "Not connected"
        cls = "status-connected" if status.get("connected") else "status-disconnected"
        return (
            f'<span class="status-badge {cls}">'
            f"{icon} {name}: {label}"
            f"</span>"
        )

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:1rem;">
            {_badge("Gmail", gmail)}
            {_badge("Outlook", outlook)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── render_input_panel ────────────────────────────────────────────────────────

def render_input_panel() -> dict:
    """Render the newsletter configuration form and return user inputs.

    Returns:
        dict with keys: topic, tone, length, platform, submitted.
    """
    with st.container():
        st.markdown('<div class="custom-input-panel"></div>', unsafe_allow_html=True)
        
        topic = st.text_input(
            "What topic should your newsletter cover?",
            placeholder="e.g. AI in healthcare, climate tech, crypto markets...",
            key="input_topic",
        )

        col1, col2 = st.columns(2)
        with col1:
            tone = st.radio(
                "Tone",
                options=["Professional", "Casual", "Bold", "Analytical"],
                horizontal=True,
                key="input_tone",
            )
        with col2:
            length = st.radio(
                "Length",
                options=["short", "medium", "long"],
                format_func=lambda x: {"short": "Short (3 stories)", "medium": "Medium (5 stories)", "long": "Long (7 stories)"}[x],
                index=1,
                key="input_length",
                horizontal=True,
            )

        st.markdown("<br/>", unsafe_allow_html=True)
        submitted = st.button(
            "✨ Generate Newsletter",
            type="primary",
            use_container_width=True,
            key="btn_generate",
        )

    return {
        "topic": topic,
        "tone": tone,
        "length": length,
        "submitted": submitted,
    }


# ── render_agent_stepper ──────────────────────────────────────────────────────

STEP_DEFS = [
    ("research_team",       "🔍 Research"),
    ("content_filter",      "🎯 Filter"),
    ("newsletter_writer",   "✍️ Write"),
    ("html_formatter",      "🎨 Format"),
    ("email_delivery",      "📮 Ready"),
    ("done",                "✅ Done"),
]


def render_agent_stepper(agent_statuses: dict) -> None:
    """Render a 6-step horizontal pipeline stepper.

    Args:
        agent_statuses: Maps agent_name → 'waiting' | 'running' | 'done' | 'error'.
    """
    items_html = ""
    for idx, (name, label) in enumerate(STEP_DEFS):
        status = agent_statuses.get(name, "waiting")

        if status == "done":
            dot_cls = "done"
            symbol = "✓"
        elif status == "running":
            dot_cls = "running"
            symbol = "●"
        elif status == "error":
            dot_cls = "error"
            symbol = "✕"
        else:
            dot_cls = "waiting"
            symbol = str(idx + 1)

        connector_cls = "done" if status == "done" else ("running" if status == "running" else "")
        connector = (
            f'<div class="step-connector {connector_cls}"></div>'
            if idx < len(STEP_DEFS) - 1
            else ""
        )

        items_html += (
            f'<div class="step-item">'
            f'<div class="step-dot {dot_cls}">{symbol}</div>'
            f'<div class="step-label">{label}</div>'
            f'</div>'
            f'{connector}'
        )

    st.markdown(
        f'<div class="stepper-container">{items_html}</div>',
        unsafe_allow_html=True,
    )


# ── render_chat_interface ─────────────────────────────────────────────────────

def render_chat_interface(messages: list[dict]) -> None:
    """Render chat history with styled bubbles.

    Args:
        messages: List of dicts with keys: role ('user'|'agent'|'system'),
                  content (str), agent_name (str, optional).
    """
    for msg in messages:
        role = msg.get("role", "system")
        content = msg.get("content", "")
        agent_name = msg.get("agent_name", "")

        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        elif role == "agent":
            with st.chat_message("assistant"):
                if agent_name:
                    st.markdown(
                        f'<span class="agent-badge">{agent_name}</span>',
                        unsafe_allow_html=True,
                    )
                
                # Hide raw HTML if it is a formatted newsletter block
                if "<html" in content.lower() or "<!doctype" in content.lower():
                    with st.expander("View generated HTML code"):
                        st.code(content, language="html")
                else:
                    if msg.get("is_new"):
                        import time
                        captured = content  # avoid closure over loop var
                        def _make_stream(text):
                            def _stream():
                                for chunk in text.split(" "):
                                    yield chunk + " "
                                    time.sleep(0.025)
                            return _stream
                        st.write_stream(_make_stream(captured))
                        msg["is_new"] = False
                    else:
                        st.write(content)
        else:
            st.markdown(
                f'<div style="text-align:center;">'
                f'<span class="chat-system">{content}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )


# ── render_newsletter_preview ─────────────────────────────────────────────────

def render_newsletter_preview(html_content: str, topic: str = "") -> None:
    """Render the generated newsletter in a preview box with action buttons.

    Args:
        html_content: Full HTML string of the newsletter.
        topic: Current newsletter topic (shown as a badge).
    """
    badge = (
        f'<span class="topic-badge">{topic}</span>' if topic else ""
    )
    st.markdown(
        f"""
        <div class="preview-header">
            <span class="preview-title">📰 Your Newsletter</span>
            {badge}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    components.html(html_content, height=600, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br/><b>Send to</b>", unsafe_allow_html=True)
    recipient = st.text_input("Send to", label_visibility="collapsed", placeholder="recipient@example.com", key="input_send_to")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        action_type = st.radio(
            "Action",
            options=["send", "draft"],
            format_func=lambda x: "📤 Send Email" if x == "send" else "📝 Create Draft",
            horizontal=True,
            key="input_action_type",
        )
    with col_b:
        platform = st.radio(
            "Platform",
            options=["gmail", "outlook"],
            format_func=lambda x: "📧 Gmail" if x == "gmail" else "📬 Outlook",
            horizontal=True,
            key="input_send_platform",
        )

    st.session_state["recipient"] = recipient
    st.session_state["action_type"] = action_type
    st.session_state["platform"] = platform
    # Tight action row
    col_dl, col_copy, col_send = st.columns(3)

    with col_dl:
        st.download_button(
            label="⬇️ Download HTML",
            data=html_content,
            file_name=f"newsletter_{topic.replace(' ', '_')[:30]}.html",
            mime="text/html",
            use_container_width=True,
            key="btn_download",
        )

    with col_copy:
        if st.button("📋 Copy HTML", use_container_width=True, key="btn_copy_toggle"):
            st.session_state["show_html_code"] = not st.session_state.get(
                "show_html_code", False
            )

    with col_send:
        btn_label = "📤 Send Now" if st.session_state.get('action_type', 'send') == "send" else "📝 Create Draft"
        if st.button(
            btn_label,
            use_container_width=True,
            key="btn_send_now",
            type="primary",
        ):
            st.session_state["confirm_send"] = True

    if st.session_state.get("show_html_code", False):
        st.code(html_content, language="html")

    # Confirmation dialog before sending
    if st.session_state.get("confirm_send", False):
        act_text = "send this newsletter to" if st.session_state.get('action_type', 'send') == 'send' else "create a draft for"
        plat_val = st.session_state.get('platform', 'gmail').title()
        recip_val = st.session_state.get('recipient', '—')
        st.warning(
            f"You are about to {act_text} "
            f"**{recip_val}** "
            f"via **{plat_val}**. "
            "Proceed?"
        )
        col_yes, col_no, col_pad = st.columns([1, 1, 2])
        with col_yes:
            yes_lbl = "✅ Send it!" if st.session_state.get('action_type', 'send') == 'send' else "✅ Create draft!"
            if st.button(yes_lbl, key="confirm_yes", type="primary", use_container_width=True):
                _trigger_send()
                st.session_state["confirm_send"] = False
        with col_no:
            if st.button("❌ Cancel", key="confirm_no", use_container_width=True):
                st.session_state["confirm_send"] = False
                st.rerun()


def _trigger_send() -> None:
    """POST to /api/send/{session_id} and show the result."""
    session_id = st.session_state.get("session_id")
    platform = st.session_state.get("platform", "gmail")
    recipient = st.session_state.get("recipient", "")
    action_type = st.session_state.get("action_type", "send")

    if not session_id:
        st.error("No active session found.")
        return

    try:
        resp = requests.post(
            f"http://localhost:8000/api/send/{session_id}",
            json={"platform": platform, "recipient": recipient, "action_type": action_type},
            timeout=30,
        )
        result = resp.json()
        if result.get("success"):
            act_word = "delivered to" if action_type == "send" else "drafted for"
            st.success(
                f"Newsletter {act_word} **{recipient}** via **{platform.title()}**!"
            )
        else:
            st.error(f"{action_type.title()} failed: {result.get('error', 'Unknown error')}")
    except Exception as exc:
        st.error(f"Could not reach API: {exc}")


# ── render_sidebar_history ────────────────────────────────────────────────────

def render_sidebar_history(sessions: list[dict], stats: dict) -> None:
    """Render the full sidebar: stats card, new session button, history list.

    Args:
        sessions: List of recent session dicts from the database.
        stats: Global stats dict from db.get_global_stats().
    """
    with st.sidebar:
        # ── Stats card ────────────────────────────────────────────────────
        st.markdown(
            f"""
            <div class="stats-card">
                <div class="stats-row">
                    <span>📰 Newsletters created</span>
                    <span class="stats-value">{stats.get("total_newsletters", 0)}</span>
                </div>
                <div class="stats-row">
                    <span>📤 Emails sent</span>
                    <span class="stats-value">{stats.get("total_sent", 0)}</span>
                </div>
                <div class="stats-row">
                    <span>🔥 Favourite topic</span>
                    <span class="stats-value"
                          style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        {stats.get("favourite_topic", "—")}
                    </span>
                </div>
                <div class="stats-row">
                    <span>📖 Avg stories</span>
                    <span class="stats-value">{stats.get("avg_stories", 0)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── New session button ─────────────────────────────────────────────
        if st.button(
            "➕ New Newsletter",
            use_container_width=True,
            type="primary",
            key="btn_new_session",
        ):
            for key in [
                "session_id", "messages", "agent_statuses",
                "newsletter_html", "is_generating", "topic",
                "tone", "recipient", "platform", "confirm_send",
                "confirm_clear", "show_html_code",
            ]:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("---")
        st.markdown("**Recent Newsletters**")

        # ── History cards ──────────────────────────────────────────────────
        if not sessions:
            st.caption("No newsletters yet. Generate one above!")
        else:
            for session in sessions:
                _render_history_card(session)

        st.markdown("---")

        # ── Clear all ──────────────────────────────────────────────────────
        if st.button(
            "🗑️ Clear All History",
            use_container_width=True,
            key="btn_clear_all",
        ):
            st.session_state["confirm_clear"] = True

        if st.session_state.get("confirm_clear", False):
            st.warning("This will permanently delete all newsletter history.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, clear", key="clear_yes", type="primary"):
                    from database.db import clear_all_sessions
                    clear_all_sessions()
                    st.session_state["confirm_clear"] = False
                    st.rerun()
            with col_no:
                if st.button("Cancel", key="clear_no"):
                    st.session_state["confirm_clear"] = False
                    st.rerun()


def _render_history_card(session: dict) -> None:
    """Render a single history card for a past session."""
    topic = session.get("topic", "—")
    status = session.get("status", "running")
    platform = session.get("platform", "gmail")
    created_at = session.get("created_at", "")
    session_id = session.get("id")

    status_cls = {
        "complete": "status-complete",
        "running": "status-running",
        "failed": "status-failed",
    }.get(status, "status-running")

    st.markdown(
        f"""
        <div class="history-card">
            <span class="history-topic">{topic[:30]}</span>
            <div class="history-meta">
                <span>{_platform_icon(platform)} {platform.title()}</span>
                <span class="status-pill {status_cls}">{status.title()}</span>
                <span>{_relative_time(created_at)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_load, col_del = st.columns(2)
    with col_load:
        if st.button("👁️ Load", key=f"load_{session_id}", use_container_width=True):
            _load_session(session_id)
    with col_del:
        if st.button("🗑️", key=f"del_{session_id}", use_container_width=True):
            from database.db import delete_session
            delete_session(session_id)
            st.rerun()


def _load_session(session_id: int) -> None:
    """Restore a past session's newsletter into the preview panel."""
    try:
        status_resp = requests.get(
            f"http://localhost:8000/api/status/{session_id}", timeout=5
        )
        status_resp.raise_for_status()
        status_data = status_resp.json()
        sess = status_data.get("session", {})
        status = sess.get("status", "running")

        st.session_state["session_id"] = session_id
        st.session_state["topic"] = sess.get("topic", "")
        st.session_state["recipient"] = sess.get("recipient", "")
        st.session_state["platform"] = sess.get("platform", "gmail")
        st.session_state["newsletter_html"] = None

        if status == "running":
            st.session_state["is_generating"] = True
            st.rerun()
            return

        if status == "failed":
            logs = status_data.get("agent_logs", [])
            error_logs: list[str] = []
            seen_errors: set[str] = set()
            for log in logs:
                if log.get("status") == "error" and log.get("output_summary"):
                    summary = log["output_summary"].strip()
                    if summary not in seen_errors:
                        seen_errors.add(summary)
                        error_logs.append(summary)
            
            detail = "\\n".join(error_logs) if error_logs else "No detailed logs found."
            st.sidebar.error(f"Cannot load a failed session.\\n\\n**Error:** {detail}")
            return

        # Status must be complete
        resp = requests.get(
            f"http://localhost:8000/api/newsletter/{session_id}", timeout=5
        )
        if resp.status_code == 404:
            st.sidebar.warning("Session is marked complete, but no newsletter HTML was found. It may have been deleted.")
            return

        resp.raise_for_status()
        data = resp.json()
        newsletter = data.get("newsletter", {})
        if newsletter and newsletter.get("html_content"):
            st.session_state["newsletter_html"] = newsletter["html_content"]
            st.session_state["is_generating"] = False
            st.rerun()
            
    except Exception as exc:
        st.sidebar.error(f"Could not load session: {exc}")


# ── render_footer ─────────────────────────────────────────────────────────────

def render_footer() -> None:
    """Render the centered app footer."""
    st.markdown(
        f"""
        <div class="app-footer">
            <p><strong>NewsletterAgent</strong> — Multi-agent intelligence · Real inbox delivery · Powered by Qubrid</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

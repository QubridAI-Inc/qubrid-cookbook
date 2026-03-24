"""Reusable Streamlit render helpers for the Recall AI interface."""

from __future__ import annotations

from html import escape
from textwrap import dedent
from typing import Any

import streamlit as st

from config import settings


def _render_html(markup: str) -> None:
    """Render dedented HTML safely through Streamlit markdown."""
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)


def _persona_parts(persona_key: str) -> tuple[str, str]:
    """Split a persona label into emoji and display name."""
    parts = persona_key.split(" ", 1)
    if len(parts) == 1:
        return "", parts[0]
    return parts[0], parts[1]


def _persona_badge(persona_key: str) -> str:
    """Render a compact persona badge label."""
    emoji, name = _persona_parts(persona_key)
    return f"{emoji} {name}"


def render_header() -> None:
    """Render the application hero header."""
    _render_html(
        f"""
        <section class="recall-hero">
            <div class="recall-hero-copy">
                <h1 class="recall-title">{settings.APP_NAME}</h1>
                <div class="recall-kicker">LONG-CONTEXT CONVERSATION DESIGN</div>
                <div class="recall-hero-copy-block">
                    <p class="recall-hero-lead">The AI that remembers your full conversation, so every reply feels informed, personal, and continuous.</p>
                </div>
            </div>
        </section>
        """
    )


def render_locked_persona_badge(persona: str) -> None:
    """Render the locked persona indicator after conversation start."""
    _render_html(
        f"""
        <div class="recall-locked-badge">
            <span>🔒 {_persona_badge(persona)}</span>
            <span class="recall-soft-label">Start a new session to change persona</span>
        </div>
        """
    )


def render_persona_selector(selected_persona: str) -> str:
    """Render a simple persona dropdown and return the selected persona key."""
    _render_html(
        """
        <div class="recall-section-head">
            <div class="recall-section-title">Choose your assistant type</div>
            <div class="recall-section-copy">Pick a mode now. The persona locks after the first user message.</div>
        </div>
        """
    )

    persona_keys = list(settings.PERSONAS.keys())
    selected_index = persona_keys.index(selected_persona) if selected_persona in persona_keys else 0
    chosen_persona = st.selectbox(
        "Assistant type",
        persona_keys,
        index=selected_index,
        label_visibility="collapsed",
    )
    description = settings.PERSONAS[chosen_persona]["description"]
    _render_html(
        f"""
        <div class="recall-persona-summary">
            <span class="recall-persona-summary-label">Selected mode</span>
            <span class="recall-persona-summary-text">{escape(chosen_persona)}: {escape(description)}</span>
        </div>
        """
    )
    return chosen_persona


def render_starter_prompts(persona: str) -> str | None:
    """Render starter prompt buttons for the current persona."""
    _render_html(
        """
        <div class="recall-section-head recall-section-head-tight">
            <div class="recall-section-title">Try a first prompt</div>
        </div>
        """
    )
    selected_prompt: str | None = None
    for index, prompt in enumerate(settings.STARTER_PROMPTS[persona]):
        if st.button(
            prompt,
            key=f"starter-{persona}-{index}",
            use_container_width=True,
            type="secondary",
        ):
            selected_prompt = prompt
    return selected_prompt


def render_prompt_draft(prompt_text: str) -> str | None:
    """Render the staged starter prompt panel and return the chosen action."""
    _render_html(
        f"""
        <div class="recall-prompt-draft">
            <div class="recall-kicker">STARTER PROMPT READY</div>
            <div class="recall-prompt-draft-text">{escape(prompt_text)}</div>
        </div>
        """
    )
    send_col, discard_col = st.columns([2.2, 1], gap="small")
    with send_col:
        if st.button(
            "Send starter prompt",
            key="send-starter-prompt",
            use_container_width=True,
            type="primary",
        ):
            return "send"
    with discard_col:
        if st.button(
            "Discard",
            key="discard-starter-prompt",
            use_container_width=True,
            type="secondary",
        ):
            return "discard"
    return None


def render_memory_bar(turn_count: int) -> None:
    """Render the thin memory depth bar above the chat area."""
    progress = max(0.0, min(turn_count / settings.MAX_HISTORY_MESSAGES, 1.0))
    percentage = progress * 100
    if turn_count < 70:
        color = settings.SUCCESS_COLOR
    elif turn_count < 90:
        color = settings.WARNING_COLOR
    else:
        color = settings.ERROR_COLOR

    badge = ""
    if turn_count >= settings.CONTEXT_WARNING_TURNS:
        badge = '<span class="recall-context-badge">Deep Memory Territory</span>'

    _render_html(
        f"""
        <section class="recall-memory-shell">
            <div class="recall-memory-bar-head">
                <span class="recall-section-title">Memory Depth</span>
                <span class="recall-memory-count">{turn_count}/{settings.MAX_HISTORY_MESSAGES} turns</span>
            </div>
            <div class="recall-memory-bar">
                <div class="recall-memory-bar-fill" style="width: {percentage:.1f}%; background: {color};"></div>
            </div>
            {f'<div class="recall-memory-bar-foot">{badge}</div>' if badge else ''}
        </section>
        """
    )


def render_chat_messages(messages: list[dict[str, Any]]) -> None:
    """Render the chat history using Streamlit chat message containers."""
    if not messages:
        return

    for message in messages:
        render_chat_message(message)


def render_chat_message(message: dict[str, Any]) -> None:
    """Render one chat message with proper markdown support."""
    role = str(message.get("role", "assistant"))
    is_assistant = role == "assistant"
    meta_label = "Recall AI" if is_assistant else "You"

    meta_class = "recall-message-meta assistant" if is_assistant else "recall-message-meta user"
    avatar = settings.QUBRID_LOGO_URL if is_assistant else "👤"
    with st.chat_message(role, avatar=avatar):
        _render_html(f'<div class="{meta_class}">{escape(meta_label)}</div>')
        st.markdown(str(message.get("content", "")))


def render_sidebar_sessions(
    sessions: list[dict[str, Any]],
    stats: dict[str, Any],
) -> dict[str, Any] | None:
    """Render the sidebar history controls and return the selected action."""
    action: dict[str, Any] | None = None

    _render_html(
        f"""
        <section class="recall-sidebar-card">
            <div class="recall-section-title">Memory Ledger</div>
            <div class="recall-stats-row"><span class="recall-stats-label">🗣️ Total sessions</span><strong>{stats["total_sessions"]}</strong></div>
            <div class="recall-stats-row"><span class="recall-stats-label">🔄 Total turns</span><strong>{stats["total_turns"]}</strong></div>
            <div class="recall-stats-row"><span class="recall-stats-label">🏆 Longest</span><strong>{stats["longest_session_turns"]} turns</strong></div>
            <div class="recall-stats-row"><span class="recall-stats-label">⭐ Favourite</span><strong>{escape(str(stats["favourite_persona"]))}</strong></div>
        </section>
        """
    )

    if st.button(
        "➕ New Session",
        key="sidebar-new-session",
        use_container_width=True,
        type="primary",
    ):
        action = {"type": "new_session"}

    has_messages = bool(st.session_state.get("messages"))
    if st.button(
        "📋 Summarize Conversation",
        key="sidebar-summarize",
        use_container_width=True,
        type="secondary",
        disabled=not has_messages,
    ):
        action = {"type": "summarize"}

    st.markdown("### Session History")
    if not sessions:
        st.caption("No sessions stored yet.")
    for session in sessions:
        title = session.get("title") or "Untitled session"
        truncated_title = title[:50] + ("..." if len(title) > 50 else "")
        _render_html(
            f"""
            <article class="recall-session-card">
                <div class="recall-session-persona">{escape(_persona_badge(str(session["persona"])))}</div>
                <div class="recall-session-title">{escape(truncated_title)}</div>
                <div class="recall-session-meta">
                    <span>{int(session.get("total_turns", 0))} turns</span>
                </div>
            </article>
            """
        )
        load_col, delete_col = st.columns(2, gap="small")
        with load_col:
            if st.button(
                "Load",
                key=f"load-session-{session['id']}",
                use_container_width=True,
                type="secondary",
            ):
                action = {"type": "load", "session_id": int(session["id"])}
        with delete_col:
            if st.button(
                "Delete",
                key=f"delete-session-{session['id']}",
                use_container_width=True,
                type="secondary",
            ):
                action = {"type": "delete", "session_id": int(session["id"])}

    st.markdown("---")
    if not st.session_state.get("clear_all_pending", False):
        if st.button(
            "Clear All Sessions",
            key="clear-all-sessions",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state["clear_all_pending"] = True
            st.rerun()
    else:
        st.warning("This deletes every stored session and message.")
        confirm_col, cancel_col = st.columns(2, gap="small")
        with confirm_col:
            if st.button(
                "Confirm",
                key="confirm-clear-all",
                use_container_width=True,
                type="primary",
            ):
                st.session_state["clear_all_pending"] = False
                action = {"type": "clear_all_confirmed"}
        with cancel_col:
            if st.button(
                "Cancel",
                key="cancel-clear-all",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state["clear_all_pending"] = False
                st.rerun()

    return action


def render_typing_indicator() -> None:
    """Render the assistant typing indicator."""
    with st.chat_message("assistant", avatar=settings.QUBRID_LOGO_URL):
        _render_html(
            """
            <div class="recall-typing">
                <span class="recall-avatar">R</span>
                <span class="recall-dot"></span>
                <span class="recall-dot"></span>
                <span class="recall-dot"></span>
            </div>
            """
        )


def render_followup_suggestions(suggestions: list[str]) -> str | None:
    """Render clickable follow-up question chips. Returns the clicked question or None."""
    _render_html(
        """
        <div class="recall-followup-head">
            <span class="recall-kicker">💡 SUGGESTED FOLLOW-UPS</span>
        </div>
        """
    )
    for i, question in enumerate(suggestions):
        if st.button(
            question,
            key=f"followup-{i}",
            use_container_width=True,
            type="secondary",
        ):
            return question
    return None


def render_summary_card(summary: str) -> dict[str, str] | None:
    """Render the AI-generated conversation summary and return any follow-up action."""
    with st.container(border=True):
        st.caption("📋 CONVERSATION SUMMARY")
        st.markdown(summary)
        if st.button("Dismiss", key="dismiss-summary", type="secondary"):
            return {"type": "dismiss_summary"}
    return None


def render_footer() -> None:
    """Render the footer caption."""
    _render_html(
        """
        <footer class="recall-footer">
            <div>Never forgets. MiniMax M2.5 · Powered by Qubrid AI</div>
        </footer>
        """
    )

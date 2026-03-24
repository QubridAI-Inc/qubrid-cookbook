"""Streamlit entry point for the Recall AI application."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from backend import api_client, attachments, memory
from config import settings
from database import db
from frontend import components, styles

st.set_page_config(
    page_title="Recall AI — Every word, remembered.",
    page_icon=settings.QUBRID_LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded",
)


def _reset_session_state(keep_persona: bool = True) -> None:
    """Reset the in-memory conversation state for a fresh session."""
    persona = st.session_state.get("persona", next(iter(settings.PERSONAS)))
    st.session_state["session_id"] = None
    st.session_state["messages"] = []
    st.session_state["persona_locked"] = False
    st.session_state["turn_count"] = 0
    st.session_state["total_tokens_session"] = 0
    st.session_state["result"] = None
    st.session_state["prompt_draft"] = ""
    st.session_state["clear_all_pending"] = False
    st.session_state["pending_assistant"] = False
    st.session_state["followup_suggestions"] = []
    st.session_state["conversation_summary"] = ""
    if keep_persona:
        st.session_state["persona"] = persona
    else:
        st.session_state["persona"] = next(iter(settings.PERSONAS))


def _ensure_session_state() -> None:
    """Seed Streamlit session-state defaults used across the app."""
    defaults: dict[str, Any] = {
        "session_id": None,
        "messages": [],
        "persona": next(iter(settings.PERSONAS)),
        "persona_locked": False,
        "turn_count": 0,
        "total_tokens_session": 0,
        "result": None,
        "prompt_draft": "",
        "clear_all_pending": False,
        "pending_assistant": False,
        "followup_suggestions": [],
        "conversation_summary": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _load_session(session_id: int) -> None:
    """Load a persisted conversation into the active session state."""
    session = db.get_session_by_id(session_id)
    if session is None:
        st.sidebar.error("That session no longer exists.")
        return

    messages = db.get_session_messages(session_id)
    st.session_state["session_id"] = session_id
    st.session_state["messages"] = messages
    st.session_state["persona"] = session["persona"]
    st.session_state["persona_locked"] = True
    st.session_state["turn_count"] = memory.get_turn_count(messages)
    st.session_state["total_tokens_session"] = session.get("total_tokens", 0) or 0
    st.session_state["result"] = None
    st.session_state["prompt_draft"] = ""
    st.session_state["clear_all_pending"] = False
    st.session_state["pending_assistant"] = False
    st.session_state["followup_suggestions"] = []
    st.session_state["conversation_summary"] = ""


def _handle_sidebar_action(action: dict[str, Any] | None) -> None:
    """Execute the sidebar action chosen by the user."""
    if not action:
        return

    action_type = action.get("type")
    if action_type == "new_session":
        _reset_session_state(keep_persona=True)
        st.rerun()

    if action_type == "load":
        _load_session(int(action["session_id"]))
        st.rerun()

    if action_type == "delete":
        session_id = int(action["session_id"])
        db.delete_session(session_id)
        if st.session_state.get("session_id") == session_id:
            _reset_session_state(keep_persona=True)
        st.rerun()

    if action_type == "clear_all_confirmed":
        db.clear_all_sessions()
        _reset_session_state(keep_persona=False)
        st.rerun()

    if action_type == "dismiss_summary":
        st.session_state["conversation_summary"] = ""
        st.rerun()

    if action_type == "summarize":
        with st.spinner("Summarizing conversation..."):
            st.session_state["conversation_summary"] = api_client.summarize_conversation(
                st.session_state["messages"]
            )
        st.rerun()


def _submit_message(
    user_text: str,
    uploaded_files: list[Any] | None = None,
) -> None:
    """Persist a user message and queue the assistant response."""
    prepared = attachments.prepare_submission(user_text, uploaded_files or [])
    display_content = prepared["display_content"]
    api_content = prepared["api_content"]
    title_seed = prepared["title_seed"]
    if not display_content or not api_content:
        return

    if st.session_state["session_id"] is None:
        session_id = db.create_session(st.session_state["persona"], title_seed)
        st.session_state["session_id"] = session_id
        st.session_state["persona_locked"] = True

    user_record = {
        "role": "user",
        "content": display_content,
        "api_content": api_content,
        "created_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tokens_used": None,
        "latency_ms": None,
    }
    st.session_state["messages"].append(user_record)
    db.save_message(
        st.session_state["session_id"],
        "user",
        display_content,
        None,
        None,
        api_content=api_content,
    )
    st.session_state["turn_count"] = memory.get_turn_count(st.session_state["messages"])
    st.session_state["prompt_draft"] = ""
    st.session_state["pending_assistant"] = True
    st.session_state["followup_suggestions"] = []
    st.session_state["conversation_summary"] = ""
    st.rerun()


def _stream_assistant_response() -> None:
    """Stream the assistant response, then run post-response agents."""
    import time as _time

    context_messages = memory.build_context_window(st.session_state["messages"])
    persona_system = settings.PERSONAS[st.session_state["persona"]]["system"]

    start = _time.time()
    with st.chat_message("assistant", avatar=settings.QUBRID_LOGO_URL):
        full_content = st.write_stream(
            api_client.chat_agent(context_messages, persona_system)
        )
    latency_ms = round((_time.time() - start) * 1000, 2)

    assistant_content = str(full_content or "")
    assistant_record = {
        "role": "assistant",
        "content": assistant_content,
        "created_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tokens_used": 0,
        "latency_ms": latency_ms,
    }
    st.session_state["messages"].append(assistant_record)
    db.save_message(
        st.session_state["session_id"],
        "assistant",
        assistant_content,
        0,
        latency_ms,
        api_content=assistant_content,
    )
    st.session_state["turn_count"] = memory.get_turn_count(st.session_state["messages"])
    st.session_state["pending_assistant"] = False

    # --- Agent: generate follow-up suggestions ---
    st.session_state["followup_suggestions"] = api_client.generate_followups(
        st.session_state["messages"]
    )

    # --- Agent: auto-title after the first exchange ---
    if st.session_state["turn_count"] == 1 and st.session_state.get("session_id"):
        title = api_client.generate_session_title(st.session_state["messages"])
        if title:
            db.update_session_title(st.session_state["session_id"], title)

    st.rerun()


def main() -> None:
    """Render the full Recall AI Streamlit application."""
    db.init_db()
    _ensure_session_state()
    styles.inject_styles()

    with st.sidebar:
        sidebar_sessions = db.get_all_sessions(settings.MAX_SESSIONS_SIDEBAR)
        global_stats = db.get_global_stats()
        sidebar_action = components.render_sidebar_sessions(sidebar_sessions, global_stats)
    _handle_sidebar_action(sidebar_action)

    components.render_header()

    if not st.session_state["persona_locked"]:
        selected_persona = components.render_persona_selector(st.session_state["persona"])
        st.session_state["persona"] = selected_persona
    else:
        components.render_locked_persona_badge(st.session_state["persona"])

    # One placeholder owns everything below the persona badge.
    # Calling .empty() on it instantly wipes the memory bar, starter prompts,
    # and chat input from the DOM *before* streaming begins.
    page_body = st.empty()

    if st.session_state["pending_assistant"]:
        page_body.empty()   # ← clears ALL previous UI in one shot
        components.render_chat_messages(st.session_state["messages"])
        _stream_assistant_response()
        return

    with page_body.container():
        components.render_memory_bar(st.session_state["turn_count"])
        if st.session_state.get("conversation_summary"):
            summary_action = components.render_summary_card(
                st.session_state["conversation_summary"]
            )
            _handle_sidebar_action(summary_action)

        pending_prompt = ""
        with st.container():
            components.render_chat_messages(st.session_state["messages"])

            if not st.session_state["messages"]:
                selected_prompt = components.render_starter_prompts(st.session_state["persona"])
                if selected_prompt:
                    st.session_state["prompt_draft"] = selected_prompt

            if st.session_state["prompt_draft"] and not st.session_state["messages"]:
                prompt_action = components.render_prompt_draft(st.session_state["prompt_draft"])
                if prompt_action == "send":
                    pending_prompt = st.session_state["prompt_draft"]
                elif prompt_action == "discard":
                    st.session_state["prompt_draft"] = ""
                    st.rerun()

            if st.session_state.get("followup_suggestions"):
                selected_followup = components.render_followup_suggestions(
                    st.session_state["followup_suggestions"]
                )
                if selected_followup:
                    st.session_state["followup_suggestions"] = []
                    _submit_message(selected_followup)

            user_input = st.chat_input(
                "Message Recall AI or upload PDFs, docs, and images...",
                accept_file="multiple",
                file_type=settings.CHAT_UPLOAD_FILE_TYPES,
            )

    submission_text = ""
    submission_files: list[Any] = []
    if pending_prompt:
        submission_text = pending_prompt
    elif user_input:
        if isinstance(user_input, str):
            submission_text = user_input
        else:
            submission_text = user_input.text
            submission_files = list(user_input.files)

    if (submission_text.strip() or submission_files) and not st.session_state["pending_assistant"]:
        _submit_message(submission_text, submission_files)

    components.render_footer()


if __name__ == "__main__":
    main()

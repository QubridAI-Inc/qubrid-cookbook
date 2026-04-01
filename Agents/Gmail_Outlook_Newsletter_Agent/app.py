"""
app.py

Main Streamlit entry point for NewsletterAgent.
Manages session state, API communication, live polling, and UI layout.

Run with:
    streamlit run app.py
"""

import os
import time
import re

import requests
import streamlit as st

from config.settings import APP_NAME, APP_TAGLINE, OUTPUTS_DIR
from database import db
from frontend.styles import inject_styles
from frontend.components import (
    render_header,
    render_connection_status,
    render_input_panel,
    render_agent_stepper,
    render_chat_interface,
    render_newsletter_preview,
    render_sidebar_history,
    render_footer,
    STEP_DEFS,
)

# ── Page configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="frontend/assets/qubrid_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown(inject_styles(), unsafe_allow_html=True)

# ── Session state initialisation ──────────────────────────────────────────────

DEFAULTS: dict = {
    "session_id": None,
    "messages": [],
    "agent_statuses": {name: "waiting" for name, _ in STEP_DEFS},
    "newsletter_html": None,
    "is_generating": False,
    "topic": "",
    "tone": "Professional",
    "recipient": "",
    "platform": "gmail",
    "confirm_send": False,
    "confirm_clear": False,
    "show_html_code": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── On startup: ensure DB and outputs dir exist ───────────────────────────────

db.init_db()
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ── Helper: validate email ────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email.strip()))


# ── Helper: fetch and merge agent statuses from API ───────────────────────────

def _sync_agent_statuses(session_id: int) -> tuple[dict, str, list[dict]]:
    """Poll /api/status and return (agent_statuses, session_status, logs)."""
    try:
        resp = requests.get(
            f"http://localhost:8000/api/status/{session_id}", timeout=5
        )
        data = resp.json()
        session = data.get("session", {})
        logs = data.get("agent_logs", [])

        statuses: dict = {name: "waiting" for name, _ in STEP_DEFS}
        for log in logs:
            name = log.get("agent_name", "")
            status = log.get("status", "running")
            if name in statuses:
                if status == "done":
                    statuses[name] = "done"
                elif status == "error":
                    statuses[name] = "error"
                else:
                    statuses[name] = "running"

        session_status = session.get("status", "running")
        if session_status == "complete":
            statuses["done"] = "done"

        return statuses, session_status, logs
    except Exception:
        return st.session_state["agent_statuses"], "running", []


# ── Helper: append unique chat messages from agent logs ───────────────────────

def _append_log_messages(logs: list[dict]) -> None:
    existing_ids = {m.get("log_id") for m in st.session_state["messages"]}
    for log in logs:
        log_id = log.get("id")
        if log_id in existing_ids:
            continue
        if log.get("output_summary"):
            st.session_state["messages"].append({
                "role": "agent",
                "content": log["output_summary"],
                "agent_name": log.get("agent_name", "agent"),
                "log_id": log_id,
                "is_new": True,
            })
            existing_ids.add(log_id)


def _unique_error_summaries(logs: list[dict]) -> list[str]:
    summaries: list[str] = []
    seen: set[str] = set()
    for log in logs:
        if log.get("status") != "error" or not log.get("output_summary"):
            continue
        summary = log["output_summary"].strip()
        if summary in seen:
            continue
        seen.add(summary)
        summaries.append(summary)
    return summaries


# ── Sidebar ───────────────────────────────────────────────────────────────────

sessions = db.get_recent_sessions(limit=20)
stats = db.get_global_stats()
render_sidebar_history(sessions, stats)

# ── Main area ─────────────────────────────────────────────────────────────────

render_header()
render_connection_status()

# ── Input panel (only when idle) ──────────────────────────────────────────────

if not st.session_state["is_generating"] and st.session_state["newsletter_html"] is None:
    inputs = render_input_panel()

    if inputs["submitted"]:
        topic = inputs["topic"].strip()
        tone = inputs["tone"]
        length = inputs["length"]

        # Validation
        if not topic:
            st.error("Please enter a topic for your newsletter.")
            st.stop()

        # Create session via API
        try:
            resp = requests.post(
                "http://localhost:8000/api/generate",
                json={
                    "topic": topic,
                    "tone": tone,
                    "recipient": "",
                    "platform": "gmail",
                    "length": length,
                },
                timeout=30,
            )
            if not resp.ok:
                # Show the exact error from the API (e.g. missing API keys)
                detail = resp.json().get("detail", resp.text)
                st.error(f"API error: {detail}")
                st.stop()
            result = resp.json()
        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot reach the API. Make sure this is running in Terminal 1:\n\n"
                "```\nuvicorn main:app --reload --port 8000\n```"
            )
            st.stop()
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
            st.stop()

        session_id = result["session_id"]

        # Update session state
        st.session_state["session_id"] = session_id
        st.session_state["topic"] = topic
        st.session_state["tone"] = tone
        st.session_state["recipient"] = ""
        st.session_state["platform"] = "gmail"
        st.session_state["is_generating"] = True
        st.session_state["agent_statuses"] = {name: "waiting" for name, _ in STEP_DEFS}
        st.session_state["messages"] = [
            {
                "role": "user",
                "content": (
                    f"Generate a {tone} newsletter about **{topic}**."
                ),
            }
        ]

        st.rerun()

# ── Live pipeline progress ─────────────────────────────────────────────────────

if st.session_state["is_generating"]:
    session_id = st.session_state["session_id"]
    topic = st.session_state["topic"]

    st.markdown(f"### Generating your newsletter about **{topic}**…")

    stepper_placeholder = st.empty()
    with stepper_placeholder.container():
        render_agent_stepper(st.session_state["agent_statuses"])

    # Show the user prompt bubble
    for msg in st.session_state["messages"]:
        if msg.get("role") == "user":
            with st.chat_message("user"):
                st.write(msg["content"])

    # ── Live SSE streaming ────────────────────────────────────────────────
    agent_placeholders: dict[str, st.delta_generator.DeltaGenerator] = {}
    agent_buffers: dict[str, str] = {}

    session_status = "running"
    try:
        with requests.get(
            f"http://localhost:8000/api/stream/{session_id}",
            stream=True,
            timeout=360,
        ) as resp:
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data: "):
                    continue
                payload = line[6:]  # strip "data: "

                if payload == "[DONE]":
                    break

                if "|||" not in payload:
                    continue
                agent_raw, token = payload.split("|||", 1)
                token = token.replace("\\n", "\n")

                # Map raw author → display name
                display = {
                    "news_searcher_1": "RESEARCH_TEAM",
                    "news_searcher_2": "RESEARCH_TEAM",
                    "research_team": "RESEARCH_TEAM",
                    "content_filter": "CONTENT_FILTER",
                    "newsletter_writer": "NEWSLETTER_WRITER",
                    "html_formatter": "HTML_FORMATTER",
                    "email_delivery": "EMAIL_DELIVERY",
                }.get(agent_raw, agent_raw.upper())

                if display not in agent_placeholders:
                    # New agent container with badge
                    with st.chat_message("assistant"):
                        st.markdown(
                            f'<span class="agent-badge">{display}</span>',
                            unsafe_allow_html=True,
                        )
                        agent_placeholders[display] = st.empty()
                    agent_buffers[display] = ""

                agent_buffers[display] += token
                agent_placeholders[display].markdown(agent_buffers[display])

        session_status = "complete"
    except Exception as exc:
        session_status = "failed"
        st.error(f"Streaming error: {exc}")

    # Update stepper to all done
    agent_statuses, session_status_db, logs = _sync_agent_statuses(session_id)
    st.session_state["agent_statuses"] = agent_statuses
    with stepper_placeholder.container():
        render_agent_stepper(agent_statuses)

    # Persist streamed messages into session for history
    for display, text in agent_buffers.items():
        st.session_state["messages"].append({
            "role": "agent",
            "content": text,
            "agent_name": display,
            "is_new": False,
        })

    # Fetch final newsletter HTML
    if session_status_db == "complete" or session_status == "complete":
        try:
            resp2 = requests.get(
                f"http://localhost:8000/api/newsletter/{session_id}", timeout=10
            )
            newsletter = resp2.json().get("newsletter", {})
            html = newsletter.get("html_content", "")
            if html:
                st.session_state["newsletter_html"] = html
                st.session_state["messages"].append({
                    "role": "system",
                    "content": "Newsletter generated successfully!",
                })
        except Exception as exc:
            st.session_state["messages"].append({
                "role": "system",
                "content": f"Warning: could not fetch newsletter HTML — {exc}",
            })
    else:
        # Collect error summaries from agent logs
        error_logs = _unique_error_summaries(logs)
        error_detail = "\n".join(error_logs) if error_logs else "Unknown error — check uvicorn terminal for the full traceback."
        st.session_state["messages"].append({
            "role": "system",
            "content": f"Pipeline failed: {error_detail}",
        })

    st.session_state["is_generating"] = False
    st.rerun()

# ── Newsletter preview ────────────────────────────────────────────────────────

if st.session_state["newsletter_html"] is not None:
    render_agent_stepper(st.session_state.get("agent_statuses", {}))
    render_newsletter_preview(
        st.session_state["newsletter_html"],
        topic=st.session_state.get("topic", ""),
    )

# ── Footer ────────────────────────────────────────────────────────────────────

render_footer()

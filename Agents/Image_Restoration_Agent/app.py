"""
ReVive AI — Main Streamlit entry point.
6-agent CrewAI photo restoration pipeline powered by Qubrid AI.
"""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

# Load .env before anything that reads env vars
load_dotenv()

from config.settings import OUTPUTS_DIR, APP_NAME
from database import db
from backend import image_processor as ip
from crew import pipeline as pipe
from frontend import components as ui
from frontend.styles import get_css

# ── Page config ───────────────────────────────────────────────────────────────
from PIL import Image as _PILImage
_QUBRID_LOGO = _PILImage.open("frontend/assets/qubrid_logo.png")

st.set_page_config(
    page_title=f"{APP_NAME} — From Faded to Vivid",
    page_icon=_QUBRID_LOGO,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown(get_css(), unsafe_allow_html=True)

# ── Startup init ──────────────────────────────────────────────────────────────
db.init_db()
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs("assets/samples", exist_ok=True)

# Generate sample images if missing
_samples_script = os.path.join("assets", "samples", "_generated")
if not os.path.exists(_samples_script):
    from frontend.assets.generate_samples import generate_all
    generate_all()
    open(_samples_script, "w").close()

# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS: dict[str, Any] = {
    "job_id":           None,
    "pipeline_result":  None,
    "agent_statuses":   {k: {"state": "waiting"} for k in
                         ["historian", "analyst", "strategist",
                          "restorer", "colorizer", "inspector"]},
    "original_image":   None,
    "final_image":      None,
    "is_processing":    False,
    "user_note":        "",
    "confirm_clear":    False,
    "error_message":    None,
    "selected_sample":  None,   # path of the currently-selected demo photo
    "view_job_id":      None,   # job ID of a history entry the user wants to review
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Progress callback ─────────────────────────────────────────────────────────
def _on_progress(
    agent_key: str,
    state: str,
    output: str,
    latency_ms: float,
) -> None:
    """Update session_state agent_statuses for live display."""
    st.session_state["agent_statuses"][agent_key] = {
        "state": state,
        "output": output[:120],
        "latency_ms": latency_ms,
        "tokens": pipe.get_pipeline_status().get(agent_key, {}).get("tokens", 0),
        "model": pipe.get_pipeline_status().get(agent_key, {}).get("model", ""),
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # ✨ Revive More — always visible at the top
    if st.button("✨ Revive More", width="stretch"):
        for key, val in _DEFAULTS.items():
            st.session_state[key] = val
        st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    jobs = db.get_recent_jobs(limit=15)
    stats = db.get_global_stats()
    ui.render_sidebar_history(jobs, stats)


# ── Main area ─────────────────────────────────────────────────────────────────
ui.render_header()

# ── Error display ─────────────────────────────────────────────────────────────
if st.session_state["error_message"]:
    st.error(st.session_state["error_message"])
    if st.button("Dismiss"):
        st.session_state["error_message"] = None
        st.rerun()

# ── Upload / Restore flow ─────────────────────────────────────────────────────
if not st.session_state["is_processing"] and st.session_state["pipeline_result"] is None:
    uploaded_source, user_note = ui.render_upload_zone()
    st.session_state["user_note"] = user_note

    # Check API key warning
    if not os.getenv("QUBRID_API_KEY"):
        st.warning(
            "⚠️ **QUBRID_API_KEY** not set. "
            "Add it to your `.env` file before restoring. "
            "Demo processing uses fallback values without a key."
        )

    if st.button("✨ ReVive My Photo", type="primary"):
        if uploaded_source is None:
            st.session_state["error_message"] = "Please upload a photo or select a sample."
            st.rerun()
        else:
            # ── Validate & load image ─────────────────────────────────────
            try:
                if isinstance(uploaded_source, str):
                    # Sample file path
                    if not os.path.exists(uploaded_source):
                        st.session_state["error_message"] = f"Sample file not found: {uploaded_source}"
                        st.rerun()
                    original_img, mime_type = ip.load_image_from_path(uploaded_source)
                    original_filename = os.path.basename(uploaded_source)
                else:
                    original_img, mime_type = ip.load_image(uploaded_source)
                    original_filename = uploaded_source.name

                # Save original
                original_path = ip.save_image(original_img, f"original_{original_filename}")
                image_base64 = ip.image_to_base64(original_img, mime_type)

                # Create DB record
                job_id = db.create_job(original_filename, original_path)
                db.update_job_status(job_id, "running")

                # Store in session
                st.session_state["job_id"] = job_id
                st.session_state["original_image"] = original_img
                st.session_state["is_processing"] = True
                st.session_state["agent_statuses"] = {
                    k: {"state": "waiting"} for k in
                    ["historian", "analyst", "strategist",
                     "restorer", "colorizer", "inspector"]
                }
                st.session_state["pipeline_result"] = None
                st.session_state["error_message"] = None

                st.rerun()

            except ValueError as exc:
                st.session_state["error_message"] = str(exc)
                st.rerun()


# ── Processing state ──────────────────────────────────────────────────────────
if st.session_state["is_processing"]:
    # Determine which agent is currently active for the subtitle
    _active_agent = next(
        (v for k, v in ui.AGENT_NAMES.items()
         if st.session_state["agent_statuses"].get(k, {}).get("state", "") == "active"),
        "Initialising…",
    )
    st.markdown(
        f'<div style="text-align:center;color:#D4A843;font-size:1.1rem;'
        f'font-family:Georgia,serif;margin:16px 0 4px">⟳ Restoration in progress…</div>'
        f'<div style="text-align:center;color:#6B4F2A;font-size:0.82rem;margin-bottom:16px">'
        f'Running: {_active_agent}</div>',
        unsafe_allow_html=True,
    )

    # Live-updatable placeholder — ALL renders go through this one slot
    progress_placeholder = st.empty()
    with progress_placeholder.container():
        ui.render_agent_progress(st.session_state["agent_statuses"])

    # Closure re-renders only the placeholder on each agent completion
    def _on_progress_live(
        agent_key: str,
        state: str,
        output: str,
        latency_ms: float,
    ) -> None:
        """Update session_state then redraw the progress panel in-place."""
        _on_progress(agent_key, state, output, latency_ms)
        # Empty MUST be called before refilling — otherwise Streamlit accumulates
        # additional elements inside the placeholder rather than replacing them.
        progress_placeholder.empty()
        with progress_placeholder.container():
            ui.render_agent_progress(st.session_state["agent_statuses"])

    # Retrieve stored inputs from session
    original_img = st.session_state["original_image"]
    job_id = st.session_state["job_id"]
    mime_type = "image/jpeg"

    # Re-encode original from the saved path
    original_path = db.get_job_by_id(job_id).get("original_image_path", "") if job_id else ""
    if original_path and os.path.exists(original_path):
        original_img, mime_type = ip.load_image_from_path(original_path)
        image_base64 = ip.image_to_base64(original_img, mime_type)
    else:
        image_base64 = ip.image_to_base64(original_img, mime_type)

    try:
        result = pipe.run_restoration_pipeline(
            image_path=original_path or ip.save_image(original_img, "original_temp.png"),
            image_base64=image_base64,
            mime_type=mime_type,
            user_note=st.session_state.get("user_note", ""),
            on_progress=_on_progress_live,
            job_id=job_id,
        )

        # Update agent statuses from pipeline status
        final_statuses = pipe.get_pipeline_status()
        for k, v in final_statuses.items():
            if k in st.session_state["agent_statuses"]:
                st.session_state["agent_statuses"][k] = v

        # Load final image
        final_path = result.get("final_image_path", "")
        if final_path and os.path.exists(final_path):
            final_img, _ = ip.load_image_from_path(final_path)
        else:
            final_img = original_img

        st.session_state["final_image"] = final_img
        st.session_state["pipeline_result"] = result
        st.session_state["is_processing"] = False

        # Persist to DB
        if job_id:
            db.complete_job(job_id, result)
            for log in result.get("agent_logs", []):
                db.save_agent_log(
                    job_id=job_id,
                    agent_name=log.get("agent", ""),
                    model=log.get("model", ""),
                    tokens=log.get("tokens", 0),
                    latency=log.get("latency_ms", 0),
                    output_summary=log.get("output", ""),
                )

        st.rerun()

    except Exception as exc:
        st.session_state["is_processing"] = False
        st.session_state["error_message"] = f"Pipeline error: {exc}"
        if job_id:
            db.update_job_status(job_id, "failed")
        st.rerun()


# ── History view ──────────────────────────────────────────────────────────────
if st.session_state.get("view_job_id") and not st.session_state["is_processing"]:
    vjid = st.session_state["view_job_id"]
    vresult = db.get_job_result(vjid)
    vjob = db.get_job_by_id(vjid)

    if vresult and vjob:
        orig_path  = vjob.get("original_image_path", "")
        final_path = vjob.get("final_image_path", "")

        if orig_path and os.path.exists(orig_path) and final_path and os.path.exists(final_path):
            vorig, _  = ip.load_image_from_path(orig_path)
            vfinal, _ = ip.load_image_from_path(final_path)

            st.markdown(
                f'<div style="display:inline-flex;align-items:center;gap:8px;'
                f'background:rgba(242,185,73,0.12);border:1.5px solid rgba(242,185,73,0.4);'
                f'border-radius:20px;padding:5px 14px;font-size:0.82rem;color:#F27430;margin-bottom:12px">'
                f'📂 Viewing history: <strong>{vjob.get("original_filename","")}</strong></div>',
                unsafe_allow_html=True,
            )

            vcontext   = vresult.get("historical_context", {})
            vdamage    = vresult.get("damage_report", {})
            vqa        = vresult.get("qa_report", {})
            vlogs      = vresult.get("agent_logs", [])
            vis_bw     = vresult.get("is_black_and_white", False)

            # Reconstruct agent_statuses from stored logs
            vstatus: dict[str, Any] = {}
            for lg in vlogs:
                akey = lg.get("agent", "")
                vstatus[akey] = {
                    "state": "complete",
                    "output": lg.get("output", ""),
                    "latency_ms": lg.get("latency_ms", 0),
                    "tokens": lg.get("tokens", 0),
                    "model": lg.get("model", ""),
                }

            ui.render_historical_badge(vcontext)
            ui.render_agent_progress(vstatus)
            ui.render_damage_summary(vdamage)
            ui.render_results(
                original_img=vorig,
                final_img=vfinal,
                context=vcontext,
                damage=vdamage,
                qa_report=vqa,
                agent_logs=vlogs,
                is_bw=vis_bw,
            )
        else:
            st.warning("Image files for this job are no longer on disk.")
    else:
        st.warning("Could not load result data for this job.")


# ── Results display ───────────────────────────────────────────────────────────
elif st.session_state["pipeline_result"] is not None and not st.session_state["is_processing"]:
    result = st.session_state["pipeline_result"]
    original_img = st.session_state["original_image"]
    final_img = st.session_state["final_image"]

    context = result.get("historical_context", {})
    damage = result.get("damage_report", {})
    qa_report = result.get("qa_report", {})
    agent_logs = result.get("agent_logs", [])
    is_bw = result.get("is_black_and_white", False)

    # Historical badge
    ui.render_historical_badge(context)

    # Agent progress (all complete)
    ui.render_agent_progress(st.session_state["agent_statuses"])

    # Damage summary
    ui.render_damage_summary(damage)

    # Full results
    ui.render_results(
        original_img=original_img,
        final_img=final_img,
        context=context,
        damage=damage,
        qa_report=qa_report,
        agent_logs=agent_logs,
        is_bw=is_bw,
    )


# ── Footer ────────────────────────────────────────────────────────────────────
ui.render_footer()

"""
ToneCraft AI — Main Streamlit entry point.
Orchestrates page layout, session state, LangGraph agent pipeline, DB persistence,
and rendering. Uses live token streaming for the rewrite step.
"""

import streamlit as st

from agents.graph import analysis_graph, chat_graph
from agents.nodes import check_quality, explain, refine, stream_rewrite_tokens
from backend.parser import calculate_diff_stats, extract_streaming_rewrite, parse_glm_response
from config.settings import MAX_INPUT_CHARS, TONES
from database import db
from frontend.components import (
    render_agent_pipeline_html,
    render_chat_panel,
    render_footer,
    render_header,
    render_results,
    render_sidebar_history,
    render_text_input,
    render_tone_selector,
)
from frontend.styles import inject_css

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ToneCraft AI — Your words, elevated.",
    page_icon="frontend/assets/qubrid_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
db.init_db()

# ── Session state ─────────────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "selected_tone": "🎯 Executive",
    "input_text": "",
    "result": None,
    "loaded_from_history": False,
    "confirm_clear": False,
    "show_copy_code": False,
}
for key, default in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar_history(db.get_recent_rewrites(limit=20))

# ── Main area ─────────────────────────────────────────────────────────────────
render_header()
selected_tone = render_tone_selector()
input_text = render_text_input()

st.markdown("<br>", unsafe_allow_html=True)
rewrite_clicked = st.button(
    "✨ Rewrite with AI Agents",
    use_container_width=True,
    type="primary",
    key="rewrite_btn",
)

# ── Rewrite pipeline ──────────────────────────────────────────────────────────
if rewrite_clicked:
    if not input_text.strip():
        st.error("Please paste some text before rewriting.")
    elif len(input_text) > MAX_INPUT_CHARS:
        st.error(
            f"Text exceeds the {MAX_INPUT_CHARS:,}-character limit "
            f"({len(input_text):,} characters). Please trim it down."
        )
    elif not selected_tone or selected_tone not in TONES:
        st.error("Please select a tone before rewriting.")
    else:
        error_msg = None
        analysis_result = {}
        stream_stats = {}
        draft_state = {}
        done_agents: set[str] = set()
        refine_triggered = False

        # ── Pipeline tracker (persistent placeholder above status blocks) ──────
        pipeline_ph = st.empty()

        def upd(active: str | None, skipped: list[str] | None = None) -> None:
            pipeline_ph.markdown(
                render_agent_pipeline_html(active, list(done_agents), skipped),
                unsafe_allow_html=True,
            )

        # ── Phase 1: Analysis (streamed node-by-node) ─────────────────────────
        upd("analyze")
        with st.status("📊 Analyzing your text…", expanded=True) as status:
            accumulated: dict = {
                "original_text": input_text,
                "target_tone": selected_tone,
                "total_tokens": 0,
                "total_latency_ms": 0.0,
                "agent_trace": [],
            }
            for event in analysis_graph.stream(accumulated):
                node_name, update = next(iter(event.items()))
                accumulated.update(update)
                if node_name == "analyze_intent":
                    done_agents.add("analyze")
                    upd("recommend")
                    ct = update.get("content_type", "")
                    dt = update.get("detected_tone", "")
                    if ct or dt:
                        status.write(f"  → {ct.replace('_',' ').title()} · {dt.title()} tone")
                elif node_name == "recommend_tones":
                    done_agents.add("recommend")
                    recs = update.get("recommended_tones", [])
                    if recs:
                        status.write("  💡 Suggested: " + " · ".join(r["tone"] for r in recs[:2]))

            analysis_result = accumulated
            content_type  = analysis_result.get("content_type", "")
            detected_tone = analysis_result.get("detected_tone", "")
            recommended   = analysis_result.get("recommended_tones", [])
            status.update(label="📊 Analysis complete", state="complete")

        # ── Phase 2: Live streaming rewrite ───────────────────────────────────
        upd("rewrite")
        with st.status("✍️ Rewriting…", expanded=True) as wr_status:
            streaming_placeholder = st.empty()
            full_content = ""
            for token in stream_rewrite_tokens(
                {**analysis_result, "original_text": input_text, "target_tone": selected_tone},
                stream_stats,
            ):
                full_content += token
                partial = extract_streaming_rewrite(full_content)
                if partial:
                    streaming_placeholder.markdown(
                        f"""<div class="tc-streaming">
                        <div class="tc-streaming-label">✍️ Writing…</div>
                        {partial.replace(chr(10), "<br>")}<span class="tc-cursor">▌</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            if stream_stats.get("error"):
                error_msg = stream_stats["error"]
                wr_status.update(label="⚠️ Error", state="error")
            else:
                try:
                    parsed = parse_glm_response(full_content)
                    draft_rewrite = parsed["rewritten"]
                    draft_explanation = parsed["explanation"]
                    done_agents.add("rewrite")
                    streaming_placeholder.empty()
                    wr_status.update(label="✍️ Rewrite complete", state="complete")
                except ValueError as exc:
                    error_msg = f"Could not parse model response: {exc}"
                    wr_status.update(label="⚠️ Parse error", state="error")

        # ── Phase 3: Quality check + optional refinement ──────────────────────
        if not error_msg:
            draft_state = {
                "original_text":     input_text,
                "target_tone":       selected_tone,
                "content_type":      content_type,
                "detected_tone":     detected_tone,
                "recommended_tones": recommended,
                "draft_rewrite":     draft_rewrite,
                "explanation":       draft_explanation,
                "rewrite_attempt":   1,
                "total_tokens":      analysis_result.get("total_tokens", 0) + stream_stats.get("tokens_used", 0),
                "total_latency_ms":  analysis_result.get("total_latency_ms", 0.0) + stream_stats.get("latency_ms", 0.0),
                "agent_trace":       analysis_result.get("agent_trace", []) + ["rewritten"],
                "quality_score":     0.0,
                "quality_issues":    [],
            }

            all_quality_checks: list[dict] = []
            upd("quality")

            with st.status("🔍 Checking quality…", expanded=True) as q_status:
                while True:
                    quality_update = check_quality(draft_state)
                    draft_state.update(quality_update)
                    score   = draft_state["quality_score"]
                    issues  = draft_state.get("quality_issues", [])
                    attempt = draft_state.get("rewrite_attempt", 1)
                    all_quality_checks.append({"score": score, "issues": list(issues)})

                    pct = int(score * 100)
                    q_status.write(
                        f"**Quality: {pct}%** — "
                        + (", ".join(issues[:2]) if issues else "✓ No issues found")
                    )

                    if score >= 0.75 or attempt >= 3:
                        done_agents.add("quality")
                        break

                    # Trigger refine
                    done_agents.add("quality")
                    refine_triggered = True
                    upd("refine")
                    q_status.write(f"🔄 Refining (attempt {attempt + 1})…")
                    refine_update = refine(draft_state)
                    draft_state.update(refine_update)
                    done_agents.add("refine")
                    upd("quality")

                final_score = draft_state["quality_score"]
                final_pct   = int(final_score * 100)
                q_status.update(
                    label=f"🔍 Quality: {final_pct}% — {'✓ Passed' if final_score >= 0.75 else '⚠ Best effort'}",
                    state="complete",
                )

            # Finalize
            upd("finalize")
            draft_state.update(explain(draft_state))
            done_agents.add("finalize")
            skipped = [] if refine_triggered else ["refine"]
            upd(active=None, skipped=skipped)

        # ── Persist + update session state ────────────────────────────────────
        if error_msg:
            st.error(f"⚠️ {error_msg}")
        else:
            diff_stats = calculate_diff_stats(input_text, draft_state["final_rewrite"])
            row_id = db.save_rewrite(
                original=input_text,
                tone=selected_tone,
                rewritten=draft_state["final_rewrite"],
                explanation=draft_state["explanation"],
                tokens=draft_state.get("total_tokens", 0),
                latency=draft_state.get("total_latency_ms", 0.0),
                word_change_pct=diff_stats["word_change_pct"],
                quality_score=draft_state.get("quality_score", 0.0),
                content_type=content_type,
                detected_tone=detected_tone,
                rewrite_attempts=draft_state.get("rewrite_attempt", 1),
            )
            st.session_state["result"] = {
                "original":           input_text,
                "tone_name":          selected_tone,
                "rewritten":          draft_state["final_rewrite"],
                "explanation":        draft_state["explanation"],
                "tokens_used":        draft_state.get("total_tokens", 0),
                "latency_ms":         draft_state.get("total_latency_ms", 0.0),
                "stats":              diff_stats,
                "db_id":              row_id,
                "content_type":       content_type,
                "detected_tone":      detected_tone,
                "quality_score":      draft_state.get("quality_score", 0.0),
                "quality_checks":     all_quality_checks,
                "recommended_tones":  recommended,
                "rewrite_attempts":   draft_state.get("rewrite_attempt", 1),
                "messages":           [],
            }
            st.session_state["loaded_from_history"] = False
            st.session_state["show_copy_code"] = False
            st.rerun()

# ── Results panel ─────────────────────────────────────────────────────────────
if st.session_state["result"] is not None:
    res = st.session_state["result"]
    render_results(
        original=res["original"],
        rewritten=res["rewritten"],
        explanation=res["explanation"],
        stats=res["stats"],
        tone_name=res["tone_name"],
        latency_ms=res["latency_ms"],
        tokens_used=res["tokens_used"],
        content_type=res.get("content_type", ""),
        detected_tone=res.get("detected_tone", ""),
        quality_score=res.get("quality_score", 0.0),
        quality_checks=res.get("quality_checks"),
        recommended_tones=res.get("recommended_tones"),
        rewrite_attempts=res.get("rewrite_attempts", 1),
    )

    # ── Chat refinement panel ──────────────────────────────────────────────────
    messages = (
        db.get_messages_for_rewrite(res["db_id"])
        if st.session_state.get("loaded_from_history")
        else res.get("messages", [])
    )

    chat_msg = render_chat_panel(messages)

    if chat_msg:
        updated_messages = messages + [{"role": "user", "content": chat_msg}]
        chat_state = {
            "original_text":    res["original"],
            "target_tone":      res["tone_name"],
            "final_rewrite":    res["rewritten"],
            "messages":         updated_messages,
            "total_tokens":     0,
            "total_latency_ms": 0.0,
        }
        with st.spinner("Refining…"):
            chat_result = chat_graph.invoke(chat_state)

        db.save_message(res["db_id"], "user", chat_msg)
        assistant_reply = (chat_result.get("messages") or [{}])[-1].get("content", "")
        if assistant_reply:
            db.save_message(res["db_id"], "assistant", assistant_reply)

        new_rewritten = chat_result.get("final_rewrite", res["rewritten"])
        st.session_state["result"] = {
            **res,
            "rewritten":   new_rewritten,
            "explanation": chat_result.get("explanation", res["explanation"]),
            "stats":       calculate_diff_stats(res["original"], new_rewritten),
            "tokens_used": res.get("tokens_used", 0) + chat_result.get("total_tokens", 0),
            "latency_ms":  res.get("latency_ms", 0.0) + chat_result.get("total_latency_ms", 0.0),
            "messages":    chat_result.get("messages", updated_messages),
        }
        st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
render_footer()

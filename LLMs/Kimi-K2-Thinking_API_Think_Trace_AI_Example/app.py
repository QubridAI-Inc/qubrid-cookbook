"""
Main application entry point for ThinkTrace AI.
"""
import streamlit as st

from frontend.styles import apply_custom_styles
from frontend.components import (
    render_header,
    render_category_tags,
    render_question_input,
    render_thinking_panel,
    render_answer_card,
    render_footer,
    render_history_sidebar
)
from backend.api_client import stream_problem


from backend.parser import clean_reasoning, clean_answer
from backend.db import init_db, save_session

# Initialize local DB
init_db()

# Page config
st.set_page_config(
    page_title="ThinkTrace AI — Watch AI Think",
    page_icon="frontend/assets/qubrid_logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
apply_custom_styles()

# Initialize Session State
if "answer" not in st.session_state:
    st.session_state["answer"] = None
if "reasoning" not in st.session_state:
    st.session_state["reasoning"] = None
if "tokens_used" not in st.session_state:
    st.session_state["tokens_used"] = 0
if "latency" not in st.session_state:
    st.session_state["latency"] = 0.0
if "show_reasoning" not in st.session_state:
    st.session_state["show_reasoning"] = True
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 0
if "total_tokens" not in st.session_state:
    st.session_state["total_tokens"] = 0
if "history_stats" not in st.session_state:
    st.session_state["history_stats"] = []
if "current_question" not in st.session_state:
    st.session_state["current_question"] = ""

# Single centered column (max width via columns)
c1, center_col, c3 = st.columns([1, 4, 1])

with center_col:
    # Render the title centered inside this column
    render_header()

    render_category_tags()
    question = render_question_input()

    start_btn = st.button("🧠 Start Thinking", use_container_width=True)

    if start_btn:
        if not st.session_state["current_question"].strip():
            st.warning("Please enter a question to start thinking.")
        else:
            # Clear previous results
            st.session_state["answer"] = None
            st.session_state["reasoning"] = None

            reasoning_buf = ""
            answer_buf = ""

            st.markdown("#### 🔍 Thinking Process")
            reasoning_box = st.empty()
            st.markdown("#### ✅ Final Answer")
            answer_box = st.empty()

            error_occurred = None

            for chunk_type, chunk_data in stream_problem(st.session_state["current_question"]):
                if chunk_type == "error":
                    error_occurred = chunk_data
                    break
                elif chunk_type == "reasoning":
                    reasoning_buf += chunk_data
                    reasoning_box.markdown(
                        f'<div style="background:#f5f0e8;border-left:3px solid #8B7355;'
                        f'padding:12px 16px;border-radius:6px;font-size:0.88rem;'
                        f'color:#4a4a4a;white-space:pre-wrap;max-height:400px;overflow-y:auto;">'
                        f'{reasoning_buf}</div>',
                        unsafe_allow_html=True
                    )
                elif chunk_type == "answer":
                    answer_buf += chunk_data
                    answer_box.markdown(answer_buf)
                elif chunk_type == "done":
                    tokens = chunk_data.get("tokens_used", 0)
                    lat_sec = chunk_data.get("latency_ms", 0) / 1000.0

                    cleaned_reasoning = clean_reasoning(reasoning_buf)
                    cleaned_answer = clean_answer(answer_buf)

                    st.session_state["answer"] = cleaned_answer
                    st.session_state["reasoning"] = cleaned_reasoning
                    st.session_state["tokens_used"] = tokens
                    st.session_state["latency"] = lat_sec
                    st.session_state["show_reasoning"] = True
                    st.session_state["question_count"] += 1
                    st.session_state["total_tokens"] += tokens
                    st.session_state["history_stats"].append({
                        "reason_len": len(cleaned_reasoning),
                        "latency": lat_sec
                    })

                    save_session(
                        question=st.session_state["current_question"],
                        category="",
                        reasoning=cleaned_reasoning,
                        answer=cleaned_answer,
                        tokens=tokens,
                        latency=lat_sec
                    )
                    st.rerun()

            if error_occurred:
                st.error(error_occurred)

st.markdown("<br><br>", unsafe_allow_html=True)

# Results Section
if st.session_state["answer"] is not None:
    with center_col:
        # Show the reasoning trace expander before the actual answer
        with st.expander("🔍 View Thinking Process (Reasoning Trace)", expanded=False):
            render_thinking_panel(st.session_state["reasoning"], is_loading=False)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display Final Answer below the reasoning
        render_answer_card(
            st.session_state["answer"], 
            st.session_state["tokens_used"], 
            st.session_state["latency"]
        )

# Sidebar and Footer
render_history_sidebar()
with center_col:
    render_footer()
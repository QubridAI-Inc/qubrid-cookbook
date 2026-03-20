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
from backend.api_client import solve_problem


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

            with st.spinner("Kimi K2 is loading its reasoning engine..."):
                # Call API
                res = solve_problem(st.session_state["current_question"], "")
                
            if "error" in res:
                st.error(res["error"])
            else:
                # Store text results, extracting cleanly
                raw_reasoning = res.get("reasoning", "")
                raw_answer = res.get("answer", "")
                
                cleaned_reasoning = clean_reasoning(raw_reasoning)
                cleaned_answer = clean_answer(raw_answer)
                
                # Update session state metrics
                tokens = res.get("tokens_used", 0)
                lat_sec = res.get("latency_ms", 0) / 1000.0  # ms to seconds
                
                st.session_state["answer"] = cleaned_answer
                st.session_state["reasoning"] = cleaned_reasoning
                st.session_state["tokens_used"] = tokens
                st.session_state["latency"] = lat_sec
                st.session_state["show_reasoning"] = True
                
                # Update aggregate stats
                st.session_state["question_count"] += 1
                st.session_state["total_tokens"] += tokens
                
                # History stat for longest trace tracking
                st.session_state["history_stats"].append({
                    "reason_len": len(cleaned_reasoning),
                    "latency": lat_sec
                })
                
                # Persist to SQLite History
                save_session(
                    question=st.session_state["current_question"],
                    category="",
                    reasoning=cleaned_reasoning,
                    answer=cleaned_answer,
                    tokens=tokens,
                    latency=lat_sec
                )

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

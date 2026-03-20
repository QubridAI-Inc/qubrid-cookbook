"""
Streamlit UI components for ThinkTrace AI.
"""
import streamlit as st
from backend.parser import count_reasoning_steps, estimate_reading_time
from config.settings import QUESTION_CATEGORIES, EXAMPLE_QUESTIONS

def render_header():
    st.markdown('<div class="brain-pulse-header">ThinkTrace AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Watch AI Think.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center; color:#7a6a4f; font-size:0.97rem; margin-top:6px; margin-bottom:18px; line-height:1.6;">'
        'Ask any hard question — ThinkTrace shows you every step of the reasoning, not just the answer.<br>'
        'Math, science, logic, coding — get transparent, step-by-step AI thinking in seconds.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('<hr style="border-top: 1px solid rgba(210, 138, 71, 0.3); margin-top: 0px; margin-bottom: 30px;">', unsafe_allow_html=True)

def render_category_tags():
    tags = "".join(
        f'<span style="margin: 0 14px; white-space:nowrap;">{cat}</span>'
        for cat in QUESTION_CATEGORIES
    )
    st.markdown(
        f'<div style="text-align:center; color:#5E6C3A; font-size:0.95rem; margin-bottom:22px; line-height:2.2;">{tags}</div>',
        unsafe_allow_html=True
    )

def apply_example(question: str):
    st.session_state["current_question"] = question
    st.session_state["question_input"] = question

def render_question_input():
    # Large text area for input
    if "question_input" not in st.session_state:
        st.session_state["question_input"] = st.session_state.get("current_question", "")
    question = st.text_area(
        "Ask anything complex",
        height=100,
        placeholder="Try a math proof, logic puzzle, science question...",
        key="question_input"
    )
    
    with st.expander("✨ Try an example"):
        for eq in EXAMPLE_QUESTIONS:
            st.button(eq, on_click=apply_example, args=(eq,), key=f"ex_{hash(eq)}")
            
    # Need to update session state if user types manually before clicking submit
    st.session_state["current_question"] = question
    return question

def format_math_for_streamlit(text: str) -> str:
    if not text:
        return ""
    # Streamlit LaTeX rendering sometimes struggles with escaped brackets from LLMs
    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
    text = text.replace(r'\(', '$').replace(r'\)', '$')
    return text

def render_thinking_panel(reasoning: str, is_loading: bool):
    if is_loading:
        st.markdown(
            """
            <div class="thinking-loading-container">
                <span style="color: #D28A47; font-weight: bold; font-size: 1.1rem;">🔍 Reasoning Trace</span>
                <br><br>
                <div class="blinking-cursor" style="font-family: monospace; color: #5E6C3A;">
                    ⟳ Kimi K2 is formulating its thoughts...
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        return

    if not reasoning:
        st.info("Reasoning trace not available for this response")
        return

    formatted_reasoning = format_math_for_streamlit(reasoning)
    steps = count_reasoning_steps(reasoning)
    read_time = estimate_reading_time(reasoning)
    
    st.markdown(f"**~{steps} steps** &nbsp;|&nbsp; **{read_time}**")
    
    # Render with markdown so LaTeX gets beautifully typeset instead of raw text
    st.markdown(formatted_reasoning)
    
def render_answer_card(answer: str, tokens: int, latency: float):
    st.markdown('<h3 class="answer-highlight">✅ Final Answer</h3>', unsafe_allow_html=True)
    st.markdown(f"**🎯 Tokens used:** {tokens} &nbsp;|&nbsp; **⚡ Latency:** {latency:.1f}s &nbsp;|&nbsp; **🧠 Model:** Kimi K2 Thinking")
    st.markdown("---")
    
    # Format the content normally using Streamlit's markdown feature
    formatted_answer = format_math_for_streamlit(answer)
    st.markdown(formatted_answer)
    
    st.markdown("---")
    
    # Formulate report string
    reasoning = st.session_state.get("reasoning", "")
    question = st.session_state.get("current_question", "")
    report_text = f"ThinkTrace Report\nQuestion: {question}\n\nReasoning:\n{reasoning}\n\nAnswer:\n{answer}"
    
    st.download_button(
        label="📥 Download Report",
        data=report_text,
        file_name="thinktrace_report.txt",
        mime="text/plain"
    )

def render_toggle_controls():
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.button("🔍 Show Full Reasoning", use_container_width=True):
            st.session_state["show_reasoning"] = True
    with col2:
        if st.button("💡 Answer Only", use_container_width=True):
            st.session_state["show_reasoning"] = False

def render_footer():
    st.markdown(
        """
        <div style="text-align: center; color: #9CA3AF; font-size: 0.82rem; margin-top: 60px; margin-bottom: 24px; letter-spacing: 0.02em;">
            Driven by Kimi K2 Thinking, powered by Qubrid AI
        </div>
        """, unsafe_allow_html=True
    )

from backend.db import get_all_sessions, delete_session

def render_history_sidebar():
    if st.sidebar.button("✏️ New Chat", use_container_width=True, key="new_chat_btn"):
        for key in ["current_question", "answer", "reasoning", "tokens_used", "latency", "show_reasoning", "question_input"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("📜 Past Sessions")

    sessions = get_all_sessions()

    if not sessions:
        st.sidebar.info("No past sessions yet.")
        return

    session_options = {s["id"]: s["title"] for s in sessions}

    selected_id = st.sidebar.selectbox(
        "Select a session",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x],
        key="selected_session_id_sb",
        label_visibility="collapsed"
    )

    if selected_id:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Load Chat", key="load_chat_btn", use_container_width=True):
                session_data = next((s for s in sessions if s["id"] == selected_id), None)
                if session_data:
                    st.session_state["current_question"] = session_data["question"]
                    st.session_state["answer"] = session_data["answer"]
                    st.session_state["reasoning"] = session_data["reasoning"]
                    st.session_state["tokens_used"] = session_data["tokens_used"]
                    st.session_state["latency"] = session_data["latency_ms"] / 1000.0 if session_data["latency_ms"] else 0.0
                    st.session_state["show_reasoning"] = True
                    st.rerun()
        with col2:
            if st.button("Delete", key=f"btn_delete_{selected_id}", use_container_width=True):
                delete_session(selected_id)
                st.rerun()

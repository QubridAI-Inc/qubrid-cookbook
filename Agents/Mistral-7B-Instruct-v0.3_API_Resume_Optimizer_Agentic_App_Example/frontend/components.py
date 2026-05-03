"""Reusable UI components for Resume-Optimizer-AI."""

import streamlit as st
from datetime import datetime
import os
import json


def render_header(theme: str = "dark"):
    """Render application header."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 3em; margin-bottom: 0;">Resume-Optimizer-AI</h1>
            <p style="font-size: 1.2em; {'color: #b0b0b0' if theme == 'dark' else 'color: #6b7280'}; margin-top: 10px;">
                AI-Powered Resume Optimization with Mistral 7B
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_theme_toggle() -> str:
    """Render theme toggle and return current theme."""
    st.sidebar.markdown("### ⚙️ Settings")

    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    theme_options = {"🌙 Dark Mode": "dark", "☀️ Light Mode": "light"}
    selected = st.sidebar.radio(
        "Theme",
        options=list(theme_options.keys()),
        index=0 if st.session_state.theme == "dark" else 1,
        label_visibility="collapsed"
    )

    st.session_state.theme = theme_options[selected]
    return st.session_state.theme


def render_file_uploader(label: str, accepted_types: list, key: str, help_text: str = None):
    """Render a file uploader."""
    return st.file_uploader(label, type=accepted_types, key=key, help=help_text)


def render_critique_feedback(critique: dict):
    """Render resume evaluation scores with colored cards."""
    st.markdown("### 📋 Resume Evaluation")

    # Overall score
    overall_score = critique.get("overall_score", 0)
    score_color = "#10b981" if overall_score >= 8 else "#f59e0b" if overall_score >= 6 else "#ef4444"

    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px; 
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1)); 
                    border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(139, 92, 246, 0.3);">
            <h2 style="color: {score_color}; margin: 0; font-size: 3em;">{overall_score:.1f}/10</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.8;">Overall Score</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Individual scores in colored cards
    col1, col2 = st.columns(2)

    scores = [
        ("Keyword Optimization", critique.get('keyword_score', 0)),
        ("Experience Relevance", critique.get('experience_score', 0)),
        ("ATS-Friendliness", critique.get('ats_score', 0)),
        ("Professional Formatting", critique.get('formatting_score', 0))
    ]

    colors = ["#8B5CF6", "#EC4899", "#3B82F6", "#10B981"]

    for i, (label, score) in enumerate(scores):
        col = col1 if i < 2 else col2
        
        with col:
            st.markdown(
                f"""
                <div style="padding: 16px; background-color: rgba(139, 92, 246, 0.05); 
                            border-left: 4px solid {colors[i]}; border-radius: 8px; margin-bottom: 12px;">
                    <p style="margin: 0; opacity: 0.7; font-size: 0.9em;">{label}</p>
                    <h3 style="margin: 5px 0 0 0; color: {colors[i]};">{score}/10</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Detailed feedback
    if critique.get("feedback"):
        with st.expander("📝 Detailed Feedback", expanded=True):
            st.write(critique["feedback"])

    # Improvements
    if critique.get("improvements_needed"):
        with st.expander("🎯 AI Suggestions for Further Improvement"):
            st.caption("*Optional suggestions to make your resume even stronger*")
            for improvement in critique["improvements_needed"]:
                st.markdown(f"- {improvement}")

    # Approval status
    if critique.get("approved"):
        st.success("✅ Resume approved for finalization!")
    else:
        st.warning("⚠️ Resume needs improvement - generating new iteration...")


def render_resume_preview(markdown_content: str):
    """Render resume preview."""
    st.markdown("---")
    st.markdown("## 📄 Your AI-Generated Tailored Resume")
    st.info("👇 **This is your NEW resume** - optimized for the job description you provided.")

    with st.container():
        st.markdown(markdown_content)


def render_download_buttons(markdown_content: str, pdf_path: str, filename_prefix: str = "resume"):
    """Render download buttons for Markdown and PDF."""
    st.markdown("### 📥 Download Resume")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📝 Download Markdown",
            data=markdown_content,
            file_name=f"{filename_prefix}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name=f"{filename_prefix}.pdf",
                mime="application/pdf",
                use_container_width=True
            )


def render_history_sidebar(history: list):
    """Render previous generations in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Previous Generations")

    if not history:
        st.sidebar.info("No previous generations yet.")
        return

    for entry in history[:10]:  # Show last 10
        timestamp = datetime.fromisoformat(entry["timestamp"])
        formatted_time = timestamp.strftime("%b %d, %I:%M %p")

        with st.sidebar.expander(f"**{entry.get('job_title', 'Unknown')}** • {formatted_time}", expanded=False):
            st.markdown(f"🏢 **{entry.get('company', 'N/A')}**")
            st.markdown(f"⭐ **Score:** {entry.get('final_score', 0):.1f}/10")
            
            st.markdown("---")
            
            # Restore button
            if st.button("📂 Open This Chat", key=f"open_{entry['id']}", use_container_width=True):
                restore_generation(entry['id'])

            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Markdown download
                md_path = entry.get("markdown_path")
                if md_path and os.path.exists(md_path):
                    try:
                        with open(md_path, "r", encoding="utf-8") as f:
                            md_content = f.read()
                        st.download_button(
                            "📝 MD",
                            data=md_content,
                            file_name=f"resume_{entry['id']}.md",
                            mime="text/markdown",
                            key=f"md_{entry['id']}",
                            use_container_width=True
                        )
                    except:
                        st.caption("MD unavailable")
                else:
                    st.caption("MD unavailable")

            with col2:
                # PDF download
                pdf_path = entry.get("pdf_path")
                if pdf_path and os.path.exists(pdf_path):
                    try:
                        with open(pdf_path, "rb") as f:
                            pdf_content = f.read()
                        st.download_button(
                            "📄 PDF",
                            data=pdf_content,
                            file_name=f"resume_{entry['id']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{entry['id']}",
                            use_container_width=True
                        )
                    except:
                        st.caption("PDF unavailable")
                else:
                    st.caption("PDF unavailable")


def restore_generation(generation_id: int):
    """Restore a previous generation to current state."""
    from backend.database import get_generation_by_id
    
    gen = get_generation_by_id(generation_id)
    if not gen:
        st.error("Generation not found")
        return
    
    # Restore to session state
    st.session_state.final_state = {
        "original_resume": gen["original_resume"],
        "job_description": gen["job_description"],
        "jd_analysis": json.loads(gen["jd_analysis"]),
        "final_resume": gen["final_resume"],
        "critique": json.loads(gen["final_critique"]),
        "iteration": gen["iterations"],
        "output_pdf_path": gen["pdf_path"]
    }
    
    st.session_state.initial_critique = json.loads(gen["initial_critique"])
    st.session_state.suggestions = json.loads(gen["suggestions"])
    st.session_state.evaluation_done = False
    
    st.rerun()


def render_error_message(error: str):
    """Render user-friendly error message."""
    st.error(f"❌ **Error:** {error}")

    with st.expander("🔧 Troubleshooting Tips"):
        st.markdown("""
        **Common issues:**

        1. **API Key Error:** Check `QUBRID_API_KEY` in `.env` file
        2. **File Upload Error:** Ensure file is a valid PDF or Markdown
        3. **Processing Timeout:** Try with shorter resume or job description
        4. **Network Error:** Check internet connection

        If problem persists, check logs or contact support.
        """)
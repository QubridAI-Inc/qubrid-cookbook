import streamlit as st
from frontend.components import render_hero, render_uploader, render_results
from frontend.sidebar import render_sidebar_col
from backend.database import get_by_id
import base64

def render_footer():
    import os
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "qubrid_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    else:
        logo_b64 = ""
    st.markdown(f'''
    <div id="qubrid-footer" style="
        position:fixed;bottom:18px;left:0;right:0;
        width:fit-content;margin:0 auto;
        background:rgba(7,26,26,0.95);
        border:1px solid rgba(20,184,166,0.4);
        color:#94a3b8;font-size:0.65rem;font-weight:600;
        letter-spacing:0.12em;text-transform:uppercase;
        padding:6px 20px;border-radius:20px;
        backdrop-filter:blur(12px);
        z-index:999999;
        white-space:nowrap;display:flex;align-items:center;gap:8px;
        pointer-events:none;
        font-family:Inter,sans-serif;
    ">
        <img src="data:image/png;base64,{logo_b64}" style="height:13px;width:13px;object-fit:contain;border-radius:2px;">
        POWERED BY QUBRID AI
    </div>
    ''', unsafe_allow_html=True)

def render_main_view():
    is_open = st.session_state.get("sidebar_open", True)

    if is_open:
        sidebar_col, main_col = st.columns([1, 3.2], gap="medium")
    else:
        sidebar_col, main_col = st.columns([0.10, 5], gap="small")

    with sidebar_col:
        render_sidebar_col()

    with main_col:
        render_hero()

        if "active_view" not in st.session_state:
            st.session_state["active_view"] = "new"

        view = st.session_state["active_view"]

        if view == "new":
            render_uploader()
        elif view == "result":
            render_results()
        elif view == "history":
            data = get_by_id(st.session_state.get("history_id"))
            if data:
                render_results(result=data["result"], filename=data["filename"])
            else:
                st.warning("Transcript not found.")
                st.session_state["active_view"] = "new"
                st.rerun()

    render_footer()

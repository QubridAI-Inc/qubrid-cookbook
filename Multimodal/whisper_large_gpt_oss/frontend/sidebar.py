import streamlit as st
from backend.database import get_history, delete_by_id

def render_sidebar_col():
    is_open = st.session_state.get("sidebar_open", True)

    if is_open:
        toggle_col, title_col = st.columns([2, 8], gap="small")
        with toggle_col:
            if st.button("◀", key="sidebar_toggle", help="Collapse", use_container_width=True):
                st.session_state["sidebar_open"] = False
                st.rerun()
        with title_col:
            st.markdown('<div style="font-size:1.05rem;font-weight:800;color:#2dd4bf;margin-top:7px;letter-spacing:-0.01em;">AudioSnap</div>', unsafe_allow_html=True)
    else:
        if st.button("▶", key="sidebar_toggle", help="Expand", use_container_width=True):
            st.session_state["sidebar_open"] = True
            st.rerun()
        return

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    if st.button("✨ New Upload", use_container_width=True, type="primary", key="nav_new"):
        st.session_state["active_view"] = "new"
        st.session_state.pop("history_id", None)
        st.rerun()

    st.markdown("""
    <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                color:#1a4040;margin:22px 0 8px 2px;">🕘 Recent</div>
    """, unsafe_allow_html=True)

    history = get_history()

    if not history:
        st.markdown('<div style="font-size:0.8rem;color:#1a4040;padding:4px 0 0 2px;">No transcripts yet.</div>', unsafe_allow_html=True)
    else:
        for row_id, filename, created_at in history:
            display   = filename[:18] + "…" if len(filename) > 18 else filename
            is_active = st.session_state.get("history_id") == row_id

            col1, col2 = st.columns([5, 1.5], gap="small")
            with col1:
                label = f"{'▶ ' if is_active else '📄 '}{display}"
                if st.button(label, key=f"h_{row_id}", use_container_width=True):
                    st.session_state["active_view"] = "history"
                    st.session_state["history_id"]  = row_id
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"d_{row_id}", help="Delete"):
                    delete_by_id(row_id)
                    if st.session_state.get("history_id") == row_id:
                        st.session_state["active_view"] = "new"
                        st.session_state.pop("history_id", None)
                    st.rerun()

            st.markdown(
                f'<div style="font-size:0.65rem;color:#1a4040;margin:-4px 0 10px 2px;">{created_at}</div>',
                unsafe_allow_html=True
            )

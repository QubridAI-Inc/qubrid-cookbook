import streamlit as st
from database.db import get_sessions, delete_session

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🪐 Studio History")
        
        if st.button("✨ New Creation", type="primary", use_container_width=True):
            st.session_state["current_session_id"] = None
            st.rerun()
            
        st.markdown("---")
            
        sessions = get_sessions()
        for s in sessions:
            col1, col2 = st.columns([0.85, 0.15])
            
            title = s['title'][:20] + "..." if len(s['title']) > 22 else s['title']
            is_active = st.session_state.get("current_session_id") == s['id']
            
            with col1:
                if st.button(f"{'💠' if is_active else '📄'} {title}", key=f"sess_{s['id']}", use_container_width=True):
                    st.session_state["current_session_id"] = s['id']
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"del_{s['id']}", help="Delete this chat"):
                    delete_session(s['id'])
                    if st.session_state.get("current_session_id") == s['id']:
                        st.session_state["current_session_id"] = None
                    st.rerun()
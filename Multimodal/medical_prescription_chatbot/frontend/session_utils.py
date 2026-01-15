import streamlit as st
from typing import Dict, Any, List

def load_into_session(p_id, img_hash, image, analysis, history):
    """
    Shared helper to populate Streamlit session state with prescription data.
    Ensures that VisionChain and memory are correctly synchronized.
    """
    st.session_state.prescription_id = p_id
    st.session_state.active_img_hash = img_hash
    st.session_state.active_image = image
    st.session_state.active_analysis = analysis
    st.session_state.chat_history = history
    
    # Update VisionChain with new context
    if "vision_chain" in st.session_state:
        st.session_state.vision_chain.prescription_id = p_id
        st.session_state.vision_chain.clear_memory()
        for msg in history:
            if msg.type == "human":
                st.session_state.vision_chain.memory.add_user_message(msg.content)
            else:
                st.session_state.vision_chain.memory.add_ai_message(msg.content)
        
    # Reset page-specific flags
    if "schedule_generated" in st.session_state:
        st.session_state.schedule_generated = False

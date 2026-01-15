"""
Medical Vision AI - Main Application Router
Handles session initialization and page routing.
"""
import streamlit as st
from backend.chain import VisionChain
from langchain_core.chat_history import InMemoryChatMessageHistory
from frontend.pages.page_prescription import render_prescription_page

# Page configuration
st.set_page_config(
    page_title="Medical Vision AI",
    page_icon="frontend/assets/qubrid_logo.png",
    layout="wide"
)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = InMemoryChatMessageHistory()
    
    if "vision_chain" not in st.session_state:
        # Initialize with session memory, but prescription_id will be set dynamically
        st.session_state.vision_chain = VisionChain(st.session_state.chat_memory)
    
    # Track the active state
    if "prescription_id" not in st.session_state:
        st.session_state.prescription_id = None
    if "active_img_hash" not in st.session_state:
        st.session_state.active_img_hash = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Analyzer"

def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Render sidebar once at the top level
    from frontend.ui_components import render_sidebar
    model_config = render_sidebar()
    uploaded_file = model_config.get("uploaded_file")
    chat_mode = model_config.get("chat_mode", "Explain Prescription")
    
    # Route based on chat_mode (consistent with "Focused Medical Chat" UI)
    if chat_mode == "Create Schedule":
        try:
            from frontend.pages.page_schedule import render_schedule_page
            render_schedule_page(model_config, uploaded_file)
        except ImportError:
            st.error("Smart Scheduler module error. Please check logs.")
    else:
        # Default to Analyzer for "Explain Prescription", "Safety Check", etc.
        render_prescription_page(model_config, uploaded_file)

if __name__ == "__main__":
    main()

"""
Main entry point for the SnapCode AI application.
Weaves together frontend components and backend logic.
"""
import streamlit as st
from config.settings import APP_NAME

# Must be the first Streamlit command
st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.styles import apply_custom_styles
from frontend.components import (
    render_header,
    render_upload_zone,
    render_image_preview,
    render_code_output,
    render_footer
)
from backend.image_utils import (
    validate_image,
    load_and_encode,
    get_image_dimensions
)
from backend.api_client import generate_code_from_image
from backend.db_utils import init_db, save_generation, get_history, rename_history_item

def init_session_state():
    """Initializes standard session states needed for the app."""
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = None
    if "last_tokens" not in st.session_state:
        st.session_state.last_tokens = 0
    if "last_latency" not in st.session_state:
        st.session_state.last_latency = 0.0
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

def main():
    # 1. Apply styles and init state
    apply_custom_styles()
    init_session_state()
    init_db()
    
    # Render Sidebar History
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        # New Chat Button
        if st.button("➕ New UI Generation", width="stretch"):
            st.session_state.generated_code = None
            st.session_state.uploader_key += 1
            st.rerun()
            
        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 1rem; font-size: 1.1rem; color: #cbd5e1;'>📜 History</h3>", unsafe_allow_html=True)
        history_items = get_history()
        
        if not history_items:
            st.info("No past generations yet. Your designs will appear here!")
        else:
            for item in history_items:
                # Use custom title if available, otherwise timestamp
                display_title = item.get('title') or item['timestamp']
                
                # Truncate and format note for label
                note_snippet = f" | {item['user_note'][:15]}..." if not item.get('title') and item.get('user_note') else ""
                label = f"{display_title}{note_snippet}"
                
                col1, col2 = st.columns([0.82, 0.18])
                
                with col1:
                    # Clicking a history button instantly restores its code to the viewer
                    if st.button(label, key=f"hist_{item['id']}", width="stretch"):
                        st.session_state.generated_code = item['html_code']
                        st.session_state.last_tokens = 0
                        st.session_state.last_latency = 0.0
                        st.session_state.uploader_key += 1
                        
                with col2:
                    with st.popover("✏️"):
                        st.markdown("<div style='font-size:0.9rem; font-weight:600; margin-bottom:10px;'>Rename Session</div>", unsafe_allow_html=True)
                        new_name = st.text_input("New Name", value=display_title, key=f"rename_input_{item['id']}", label_visibility="collapsed")
                        if st.button("Save", key=f"save_name_{item['id']}", width="stretch", type="primary"):
                            if new_name.strip():
                                rename_history_item(item['id'], new_name.strip())
                                st.rerun()
    
    # 2. Render Header
    render_header()
    
    # 3. Stacked Centered Layout (Vertical Layout via Columns to protect Wide Mode)
    st.markdown("<h2 style='text-align: center; margin-top: 2rem; margin-bottom: 1.5rem; font-size: 2.2rem; color: #ffffff;'>Input Design</h2>", unsafe_allow_html=True)
    
    in_c1, in_c2, in_c3 = st.columns([1, 2.5, 1])
    
    with in_c2:
        uploaded_file = render_upload_zone(upload_key=f"file_uploader_{st.session_state.uploader_key}")
        
        user_note = ""
        generate_clicked = False
        
        if uploaded_file is not None:
            width, height = get_image_dimensions(uploaded_file)
            render_image_preview(uploaded_file, width, height)
            
            st.markdown("<div style='text-align: center; margin-top: 2rem; margin-bottom: 0.5rem; font-weight: 600; color: #e2e8f0;'>Add a note for the AI (optional)</div>", unsafe_allow_html=True)
            user_note = st.text_input(
                "Note",
                placeholder="e.g. Make it mobile-first, use dark theme...",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            generate_clicked = st.button("✨ Generate Code", type="primary", width="stretch")
        
        # 10vh spacer to beautifully transition the Result section downward
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 3rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem;'>Result</h3>", unsafe_allow_html=True)
    
    # Action handler
    if generate_clicked and uploaded_file is not None:
        # Clear previous results internally before showing new layout
        st.session_state.generated_code = None
        
        is_valid, error_msg = validate_image(uploaded_file)
        if not is_valid:
            st.error(error_msg)
        else:
            try:
                base_64, mime_type = load_and_encode(uploaded_file)
                with st.spinner("Kimi K2.5 is analyzing your design..."):
                    response = generate_code_from_image(base_64, mime_type, user_note)
                    
                if "error" in response:
                    st.error(response["error"])
                else:
                    st.session_state.generated_code = response["code"]
                    st.session_state.last_tokens = response["tokens_used"]
                    st.session_state.last_latency = response["latency_ms"]
                    
                    # Save successful generation to DB
                    save_generation("UI Element", response["code"], user_note)
                    
                    st.success("Analysis complete and saved into sidebar history!")
            except Exception as e:
                st.error(f"Failed to process image: {str(e)}")
    
    # Display Results or Placeholder
    if st.session_state.generated_code:
        render_code_output(
            st.session_state.generated_code,
            st.session_state.last_tokens,
            st.session_state.last_latency
        )
    else:
        # Placeholder card
        placeholder_html = """
        <div style='background: rgba(26, 26, 46, 0.4); border: 1px solid rgba(79, 142, 247, 0.2); border-radius: 16px; padding: 4rem 2rem; text-align: center; color: #64748b; margin-top: 1rem; display: flex; flex-direction: column; justify-content: center; min-height: 400px;'>
            <div style='font-size: 3rem; margin-bottom: 1rem; opacity: 0.8;'>⚡</div>
            <h4 style='color: #8892b0; margin-bottom: 0.5rem;'>Awaiting Input</h4>
            <p>Upload a design and hit Generate Code. Your results will appear here.</p>
        </div>
        """
        st.markdown(placeholder_html, unsafe_allow_html=True)

    # 4. Render Footer
    render_footer()

if __name__ == "__main__":
    main()

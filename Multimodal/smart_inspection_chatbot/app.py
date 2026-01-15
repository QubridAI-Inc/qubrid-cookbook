import streamlit as st  # Main web framework for building the UI
import uuid  # Library for generating unique Session IDs (e.g., 550e8400-e29b...)
import os  # Standard library for file system operations (creating folders, paths)
import sys  # Standard library to modify the python path

# Ensure Python can find our local modules by adding the current working directory
sys.path.append(os.getcwd())

# --- CUSTOM MODULE IMPORTS ---
# Importing styling logic to switch between Light and Dark themes
from frontend.styles import apply_custom_styles
# Importing the Sidebar logic that returns user configurations
from frontend.sidebar import render_sidebar
# Importing the backend function that actually calls the AI API
from backend.api_client import chat_with_industrial_ai
# Importing the utility to convert chat history into a downloadable PDF
from backend.utils import generate_pdf_report
# Importing all necessary database functions for saving/loading sessions
from backend.database import init_db, create_session, add_message, get_session_history, update_session_image, get_session_meta
# Importing the strict Guardrail prompt that defines the AI's identity and boundaries
from backend.schemas import GUARDRAIL_PROMPT

# --- PAGE CONFIGURATION ---
# Sets up the browser tab title to "DiagnostiQ", uses the full width of the screen, and sets the icon
st.set_page_config(page_title="DiagnostiQ", layout="wide", page_icon="🔍")

# --- ASSET DIRECTORY SETUP ---
# Defines where uploaded images are temporarily stored locally
ASSETS_DIR = os.path.join("frontend", "assets")
# Creates the folder if it doesn't exist to prevent "File Not Found" errors
os.makedirs(ASSETS_DIR, exist_ok=True)

def render_metrics(u):
    """
    Helper function to display the 3 performance metrics (Tokens, Time, Speed)
    in a neat row under each AI response.
    
    It handles two data types:
    1. Dictionary (when loading old history from the database)
    2. Pydantic Object (when receiving a fresh response from the API)
    """
    # 1. Extract values based on data type
    if isinstance(u, dict):
        tokens = u.get('total_tokens', 0)
        latency = u.get('latency', 0.0)
        speed = u.get('throughput', 0.0)
    else:
        tokens = getattr(u, 'total_tokens', 0)
        latency = getattr(u, 'latency', 0.0)
        speed = getattr(u, 'throughput', 0.0)
    
    # 2. Render the HTML "Pills" (Visual badges)
    # The CSS class 'tech-pill' is defined in frontend/styles.py
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <div class='tech-pill'>🪙 {tokens} TOKENS</div>
        <div class='tech-pill'>⏱ {latency}s</div>
        <div class='tech-pill'>⚡ {speed} T/s</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """
    The main execution function of the application.
    This runs every time the user interacts with the page.
    """
    
    # 1. Initialize Database
    # Creates the 'sessions' and 'messages' tables if they don't exist yet
    init_db()
    
    # 2. Session Management (Persistence)
    # If the user opens the app for the first time, generate a Session ID
    if "active_session_id" not in st.session_state:
        st.session_state.active_session_id = str(uuid.uuid4())
        create_session(st.session_state.active_session_id)
        
    # If the user clicked "New Inspection" in the sidebar, generate a new Session ID
    if st.session_state.get("trigger_new_chat"):
        st.session_state.active_session_id = str(uuid.uuid4())
        create_session(st.session_state.active_session_id)
        st.session_state.trigger_new_chat = False  # Reset flag

    # 3. Load Chat History
    # Fetch messages from the database for the active session
    current_messages = get_session_history(st.session_state.active_session_id)
    # Sync database history with Streamlit's session state (UI memory)
    if "messages" not in st.session_state or st.session_state.messages != current_messages:
        st.session_state.messages = current_messages

    # Fetch metadata (like the saved image path) for the current session
    session_meta = get_session_meta(st.session_state.active_session_id)

    # 4. Render Sidebar Controls
    # Displays the sidebar and returns the user's selected configuration
    base_instruction, user_requirements, selected_theme = render_sidebar()
    
    # Apply the CSS theme (Light/Dark) based on sidebar selection
    apply_custom_styles(mode=selected_theme)

    # 5. Render Main Header
    # Using HTML for precise centering and typography
    st.markdown("<br>", unsafe_allow_html=True)  # Spacer
    st.markdown("<h1>DiagnostiQ</h1>", unsafe_allow_html=True)  # <-- BRANDING UPDATE
    st.markdown("<h3>INDUSTRIAL COMPONENT DIAGNOSTICS</h3>", unsafe_allow_html=True) 
    st.markdown("<br>", unsafe_allow_html=True)  # Spacer

    # 6. Layout: Two Columns
    # Left (1 part) for Image | Right (2 parts) for Chat
    col_visual, col_chat = st.columns([1, 2], gap="large")

    # === LEFT COLUMN: VISUAL INPUT ===
    with col_visual:
        # CLEAN HEADER: Removed the "1." prefix
        st.markdown("#### COMPONENT SCAN")
        
        # Check if an image is already saved in the database for this session
        saved_image_path = session_meta.get('image_path') if session_meta else None
        
        # Render File Uploader Widget
        uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        active_image = None
        
        # Logic: User just uploaded a NEW file
        if uploaded_file:
            # Save the file to the 'assets' folder with the Session ID as the name
            file_path = os.path.join(ASSETS_DIR, f"{st.session_state.active_session_id}.png")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Update the database to link this image to the current session
            update_session_image(st.session_state.active_session_id, file_path)
            active_image = uploaded_file
            st.success("✔ IMAGE SAVED")
            
        # Logic: No new upload, but we have a saved file from before
        elif saved_image_path and os.path.exists(saved_image_path):
            active_image = saved_image_path
            st.info("📂 LOADED FROM ARCHIVE")

        # Display the active image or a placeholder box
        if active_image:
            st.image(active_image, width="stretch")
        else:
            st.markdown(
                """<div style="text-align:center; padding: 40px; border: 2px dashed var(--border-color); color: var(--text-secondary);">
                No visual data source.<br>Upload image to begin.
                </div>""", 
                unsafe_allow_html=True
            )

    # === RIGHT COLUMN: CHAT INTERFACE ===
    with col_chat:
        # Mini-header row for "Analysis Log" and the "Export PDF" button
        c1, c2 = st.columns([3, 1])
        with c1: 
            # CLEAN HEADER: Removed the "3." prefix
            st.markdown("#### ANALYSIS LOG")
        with c2:
            # Show download button only if there is chat history
            if st.session_state.messages:
                pdf_bytes = generate_pdf_report(st.session_state.messages)
                st.download_button("📥 EXPORT PDF", data=pdf_bytes, file_name=f"Report.pdf", mime="application/pdf", width="stretch")

        # Container for chat messages (Scrollable area)
        chat_container = st.container(height=600, border=True)
        with chat_container:
            # Empty State
            if not st.session_state.messages:
                st.markdown("<div style='text-align: center; color: var(--text-secondary); padding-top: 50px;'>SYSTEM STANDBY.</div>", unsafe_allow_html=True)
            
            # Loop through and display all messages (User + AI)
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    # If metrics exist for this message, render the pills
                    if msg.get("usage"):
                        render_metrics(msg["usage"])

        # 7. User Input Handling
        if prompt := st.chat_input("Enter diagnostic command..."):
            # Validation: Prevent chatting without an image
            if not active_image:
                st.toast("⚠️ ERR: NO VISUAL INPUT DETECTED", icon="🚫")
            else:
                # 1. Append User Message to State & Database
                st.session_state.messages.append({"role": "user", "content": prompt})
                add_message(st.session_state.active_session_id, "user", prompt)
                
                # Render user message immediately
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                # 2. Construct the "Super Prompt"
                # Combine: Sidebar Persona + Global Guardrails + User Instructions
                final_system_prompt = f"{base_instruction}\n\n{GUARDRAIL_PROMPT}"
                if user_requirements:
                    final_system_prompt += f"\n\nADDITIONAL OPERATOR INSTRUCTIONS:\n{user_requirements}"

                # 3. Call AI Backend
                with chat_container:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        with st.spinner("PROCESSING..."):
                            try:
                                # Prepare image data (Bytes) for API
                                if isinstance(active_image, str):
                                    img_for_api = open(active_image, "rb")
                                    import io
                                    img_bytes = io.BytesIO(img_for_api.read())
                                    img_for_api.close()
                                else:
                                    img_bytes = active_image
                                
                                # Send request to Qubrid AI
                                response = chat_with_industrial_ai(
                                    current_question=prompt,
                                    image_file=img_bytes,
                                    chat_history=st.session_state.messages[:-1], # Context
                                    system_prompt=final_system_prompt
                                )
                                
                                # Render AI Text Response
                                message_placeholder.markdown(response.content)
                                
                                # Convert usage object to dict for storage
                                usage_dict = response.usage.model_dump()
                                
                                # Render Metrics Pills
                                render_metrics(response.usage)

                                # 4. Save AI Response to Database
                                add_message(st.session_state.active_session_id, "assistant", response.content, usage_dict)
                                st.session_state.messages.append({"role": "assistant", "content": response.content, "usage": usage_dict})

                            except Exception as e:
                                st.error(f"SYSTEM FAILURE: {str(e)}")

# Standard Python Entry Point
if __name__ == "__main__":
    main()
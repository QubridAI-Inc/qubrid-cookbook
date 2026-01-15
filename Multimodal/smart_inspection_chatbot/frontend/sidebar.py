import streamlit as st  # Main library for the web interface components
from backend.schemas import PROMPTS  # Imports the dictionary of AI Personas (General, Defect, Safety)
# Import database functions to handle session management (CRUD operations)
from backend.database import get_all_sessions, update_session_title, get_session_meta, delete_session, update_session_mode

def render_sidebar():
    """
    Renders the sidebar UI and returns the user's configuration choices.
    
    This function handles:
    1. Creating new inspections
    2. Renaming/Deleting the current session
    3. Selecting the AI Protocol (and syncing it to the DB)
    4. Navigation history (Archives)
    5. Theme selection
    
    Returns:
        base_instruction (str): The System Prompt text for the selected mode.
        user_requirements (str): Custom user instructions (e.g., "Check for rust").
        selected_theme (str): 'Light' or 'Dark'.
    """
    
    # Create the sidebar container
    with st.sidebar:
        st.markdown("## ⚙️ CONTROLS")
        st.markdown("---")
        
        # 1. NEW INSPECTION BUTTON
        # A primary button to reset the state and start fresh.
        if st.button("➕ NEW INSPECTION", type="primary", width="stretch"):
            # Set a flag in session_state that app.py will detect to generate a new UUID
            st.session_state.trigger_new_chat = True
            # Force a page reload to process the new session immediately
            st.rerun()

        # 2. MANAGE SESSION (Rename / Delete)
        # Initialize default mode
        current_mode = "General Analysis" 
        
        # Only show these options if there is an active session
        if "active_session_id" in st.session_state:
            active_id = st.session_state.active_session_id
            
            # Fetch metadata (Title, Mode) from the database
            meta = get_session_meta(active_id)
            if meta:
                current_title = meta['title']
                
                # Check if this session has a saved protocol (e.g., Defect Inspection)
                # This ensures that if you load an old chat, the dropdown switches to the correct mode automatically.
                saved_mode = meta.get('mode')
                if saved_mode in PROMPTS:
                    current_mode = saved_mode

                # Expandable menu to keep the UI clean
                with st.expander("⚙️ Session Options", expanded=False):
                    
                    # --- RENAME SECTION ---
                    st.caption("Rename")
                    # Input box pre-filled with the current title
                    new_name = st.text_input("Name", value=current_title, label_visibility="collapsed")
                    
                    if st.button("💾 Save", width="stretch"):
                        # Only update DB if the name actually changed
                        if new_name and new_name != current_title:
                            update_session_title(active_id, new_name)
                            st.rerun() # Refresh to update the Sidebar History list
                    
                    # --- DELETE SECTION ---
                    st.caption("Delete")
                    if st.button("🗑 Delete", width="stretch"):
                        # Delete from DB and remove image file from disk
                        delete_session(active_id)
                        # Remove from Session State so the app doesn't try to load a dead session
                        del st.session_state.active_session_id
                        st.rerun() # Refresh to load a new blank session

        st.markdown("---")

        # 3. PROTOCOL SELECTOR (Synced with Database)
        # This controls the "AI Persona" (Engineer vs Safety Officer vs Forensic Analyst)
        st.markdown("### 1. PROTOCOL")
        
        # Calculate the index of the dropdown based on the loaded DB mode.
        # Example: If current_mode is 'Safety Audit', this finds its position in the list (e.g., index 2).
        mode_options = list(PROMPTS.keys())
        try:
            default_index = mode_options.index(current_mode)
        except ValueError:
            default_index = 0

        # Render the dropdown
        selected_mode = st.selectbox(
            "Persona", 
            mode_options, 
            index=default_index, 
            label_visibility="collapsed"
        )
        
        # Logic: If user manually changes the dropdown, save it to DB immediately.
        # This "locks" the choice so it persists even if they reload the page.
        if "active_session_id" in st.session_state and selected_mode != current_mode:
            update_session_mode(st.session_state.active_session_id, selected_mode)
            st.rerun() # Refresh to confirm the lock

        # Retrieve the actual system prompt text associated with the chosen name
        base_instruction = PROMPTS[selected_mode]

        # 4. CUSTOM FOCUS (User Instructions)
        st.markdown("### 2. FOCUS")
        # A text area for users to add specific context (e.g., "Ignore the dirt, look for cracks")
        user_requirements = st.text_area(
            "Instructions", 
            height=80, 
            placeholder="Check for cracks...", 
            label_visibility="collapsed"
        )
        
        # 5. ARCHIVES (History Navigation)
        st.markdown("### 3. ARCHIVES")
        # Fetch all valid sessions from the database
        sessions = get_all_sessions()
        
        if not sessions:
            st.caption("No history.")
        
        # Loop through past sessions and create a navigation button for each
        for s in sessions:
            # Check if this button corresponds to the currently open chat
            is_active = s['id'] == st.session_state.get("active_session_id")
            
            # Use a Green Circle for active, Paper icon for inactive
            icon = "🟢" if is_active else "📄"
            
            # Format date to show just Month-Day (e.g., 01-15)
            date_short = s['created_at'][5:10]
            
            # Create the button label
            btn_label = f"{icon} {date_short} | {s['title']}"
            
            # If clicked, switch the global session ID and reload the main chat window
            if st.button(btn_label, key=s['id'], width="stretch"):
                st.session_state.active_session_id = s['id']
                st.rerun()

        st.markdown("---")
        
        # 6. THEME SWITCHER
        # Allows toggling between Light and Dark CSS modes
        st.caption("INTERFACE THEME")
        selected_theme = st.selectbox(
            "Theme", 
            ["Light", "Dark"], 
            index=0, 
            label_visibility="collapsed"
        )

        # Return the 3 critical configuration values to app.py
        return base_instruction, user_requirements, selected_theme
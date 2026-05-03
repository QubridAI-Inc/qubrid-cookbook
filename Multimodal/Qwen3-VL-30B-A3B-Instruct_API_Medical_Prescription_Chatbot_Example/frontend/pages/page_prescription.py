import streamlit as st
from typing import Dict, Any
from PIL import Image
import time
from services.utils import calculate_image_hash
from services.image_validation import validate_prescription
from services.extraction_service import perform_extraction
from services.conversation_restore import restore_conversation_by_hash
from db.prescriptions import delete_prescription, get_all_prescriptions
from db.chat import get_chat_history
from frontend.ui_components import (
    render_sidebar, 
    render_welcome_screen, 
    render_medicine_cards, 
    render_transparency_panel,
    render_ambiguity_resolver,
    render_unresolvable_card
)
from frontend.session_utils import load_into_session

def render_prescription_page(model_config: Dict[str, Any], uploaded_file: Any):
    """Main Prescription Analyzer page logic."""
    chat_mode = model_config.get("chat_mode", "Explain Prescription")
    
    # Handle conversation switching from sidebar
    if st.session_state.get("switch_to_prescription_id"):
        _switch_to_prescription(st.session_state.switch_to_prescription_id)
        del st.session_state.switch_to_prescription_id
    
    # UI Header
    head_col1, head_col2 = st.columns([0.6, 0.4])
    with head_col1:
        st.title("Medical Prescription Analyzer 🩺", anchor=False)
    with head_col2:
        # Align image vertically with title by using a container or padding if needed, 
        # but for now standard st.image should work.
        st.image("frontend/assets/qubrid_banner.png", width="stretch")
    
    st.markdown("### **Structured Medical Intelligence Platform | Powered by Qubrid AI**")
    st.divider()

    # 1. Handle New Upload
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_hash = calculate_image_hash(image)
        
        # Check if already processed
        if st.session_state.get("active_img_hash") != img_hash:
            with st.status("🔍 Checking for existing record...", expanded=True) as status:
                restored = restore_conversation_by_hash(img_hash)
                
                if restored:
                    st.write("✅ Existing prescription found. Restoring history...")
                    load_into_session(*restored)
                    status.update(label="Restoration Complete!", state="complete", expanded=False)
                else:
                    st.write("🧐 Verifying new image...")
                    is_valid, validation = validate_prescription(image)
                    
                    if not is_valid:
                        st.error(f"❌ This image does not appear to be a medical prescription.\n\nReason: {validation.get('reason', 'Unknown')}")
                        status.update(label="Access Blocked", state="error", expanded=False)
                        st.stop()
                    
                    st.write("🪄 Extraction in progress...")
                    p_id, analysis = perform_extraction(image, st.session_state.vision_chain)
                    load_into_session(p_id, img_hash, image, analysis, [])
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            st.rerun()

    # 2. Main content area
    if st.session_state.get("prescription_id"):
        _render_active_prescription(chat_mode, model_config)
    else:
        render_welcome_screen()

def _switch_to_prescription(p_id):
    """Switch to a specific prescription by ID."""
    from db.prescriptions import get_all_prescriptions
    all_p = get_all_prescriptions()
    target = next((p for p in all_p if p["id"] == p_id), None)
    if target:
        from services.conversation_restore import restore_conversation_by_hash
        restored = restore_conversation_by_hash(target["image_hash"])
        if restored:
            load_into_session(*restored)

def _render_active_prescription(chat_mode, model_config):
    """Render the active prescription work area."""
    # Get ambiguity state
    audit_data = st.session_state.active_analysis["audit"]
    ambiguity_state = audit_data.get("ambiguity_state", "CLEAR")

    col1, col2 = st.columns([2, 1])
    with col1:
        render_medicine_cards(st.session_state.active_analysis["extraction"])
    with col2:
        with st.expander("🖼️ View Original Prescription", expanded=False):
            st.image(st.session_state.active_image, width="stretch")
        render_transparency_panel(
            audit_data, 
            st.session_state.vision_chain.qubrid_client.model_name
        )

    st.divider()
    
    # Branching based on Ambiguity State
    if ambiguity_state == "UNRESOLVABLE":
        render_unresolvable_card(st.session_state.active_analysis["extraction"], audit_data)
    else:
        render_ambiguity_resolver(audit_data, st.session_state.active_analysis["extraction"])
    
    # Chat Area
    for message in st.session_state.chat_history:
        avatar = "👤" if message.type == "human" else "🤖"
        with st.chat_message("user" if message.type == "human" else "assistant", avatar=avatar):
            st.markdown(message.content)

    user_query = st.chat_input(f"Ask about this prescription...")
    if user_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
        
        # Stream response
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""
            response = st.session_state.vision_chain.stream_with_mode(
                image=st.session_state.active_image,
                user_query=user_query,
                mode=chat_mode,
                extraction_context=st.session_state.active_analysis["extraction"],
                ambiguity_state=ambiguity_state,
                **model_config
            )
            for chunk in response:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        # Persist - VisionChain already handled DB saving, we just need to refresh UI
        st.session_state.chat_history.append(st.session_state.vision_chain.memory.messages[-2]) # User
        st.session_state.chat_history.append(st.session_state.vision_chain.memory.messages[-1]) # AI
        st.rerun()

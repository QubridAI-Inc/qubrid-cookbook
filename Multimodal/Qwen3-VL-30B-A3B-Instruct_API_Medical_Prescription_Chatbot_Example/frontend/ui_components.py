"""
Streamlit UI components - Sidebar, Cards, Panels.
"""
import streamlit as st
import time
from typing import Dict, Any, List
from db.prescriptions import get_all_prescriptions, delete_prescription, update_prescription_data


def render_welcome_screen():
    """Render welcome screen when no conversation is active."""
    
    # UI Header for Welcome
    st.title("Welcome to Medical Prescription Analyzer", anchor=False)
    
    st.markdown("Upload a prescription image to extract structured intelligence and start a focused medical chat.")
    
    with st.expander("🛡️ Safety First - How it works", expanded=True):
        st.markdown("""
        1. **Upload Prescription**: Our Vision AI performs a 4-step analysis of the handwriting.
        2. **Review Cards**: Medicines are extracted into structured cards with confidence markers.
        3. **Resolve Ambiguity**: If the AI is unsure, it will ask you to clarify specific words.
        4. **Focused Chat**: Switch between 'Explain' or 'Schedule' modes for specific insights.
        
        *Note: This tool is for informational purposes and does not replace professional medical advice.*
        """)


def render_medicine_cards(extraction: Dict[str, Any]):
    """Render extracted medicines as cards with confidence indicators."""
    if not extraction or "medicines" not in extraction:
        return

    st.subheader("Extracted Medications")
    
    # Overall Confidence Meter
    conf = extraction.get("overall_confidence", 0)
    conf_color = "green" if conf >= 0.8 else "orange" if conf >= 0.6 else "red"
    st.progress(conf, text=f"Overall Extraction Confidence: {int(conf*100)}%")

    cols = st.columns(2)
    for i, med in enumerate(extraction["medicines"]):
        with cols[i % 2]:
            # Determine card border color based on confidence
            m_conf = med.get("confidence", 1.0)
            border_color = "#28a745" if m_conf >= 0.8 else "#ffc107" if m_conf >= 0.6 else "#dc3545"
            warning_icon = "⚠️ " if m_conf < 0.6 else ""
            
            st.markdown(f"""
                <div style="
                    border: 2px solid {border_color};
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 10px;
                    background-color: rgba(255, 255, 255, 0.05);
                ">
                    <h4 style="margin: 0; color: {border_color};">{warning_icon}{med.get('name', 'Unknown')}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 14px;"><b>Dosage:</b> {med.get('dosage', 'N/A')}</p>
                    <p style="margin: 2px 0 0 0; font-size: 14px;"><b>Frequency:</b> {med.get('frequency', 'N/A')}</p>
                    <p style="margin: 2px 0 0 0; font-size: 14px;"><b>Timing:</b> {', '.join(med.get('timing', []))}</p>
                    <p style="margin: 5px 0 0 0; font-style: italic; font-size: 12px;">{med.get('instructions', '')}</p>
                </div>
            """, unsafe_allow_html=True)


def render_transparency_panel(audit_data: Dict[str, Any], model_name: str):
    """Render the AI Transparency Panel in the sidebar."""
    st.sidebar.divider()
    with st.sidebar.expander("🔬 AI Transparency Panel", expanded=True):
        st.write(f"**Model:** `{model_name}`")
        
        # Prescription Detection Result
        val_data = audit_data.get("validation", {})
        is_p = val_data.get("is_prescription", False)
        conf = val_data.get("confidence", 0)
        reason = val_data.get("reason", "N/A")
        
        st.write(f"**Prescription detected:** {'Yes' if is_p else 'No'} (Confidence: {conf:.2f})")
        if not is_p:
             st.caption(f"Reason: {reason}")
             
        st.write("**Pipeline Steps:**")
        st.caption("0. Prescription Validation (Safety Gate)")
        st.caption("1. Vision OCR Extraction")
        st.caption("2. Entity Normalization")
        st.caption("3. Schedule Inference")
        st.caption("4. Safety & Ambiguity Audit")
        
        if audit_data.get("safety_flags"):
            st.warning("Safety Considerations detected in extraction.")
        
        # New: Ambiguity Status
        state = audit_data.get("ambiguity_state", "CLEAR")
        state_color = "green" if state == "CLEAR" else "orange" if state == "CLARIFIABLE" else "red"
        st.markdown(f"**Ambiguity Status:** <span style='color:{state_color}'>{state}</span>", unsafe_allow_html=True)
        
        if state == "UNRESOLVABLE":
            st.write("**Reason:**")
            st.caption("• Visual noise too high")
            st.caption("• No safe medical alternatives detected")
            st.write("**Action Taken:** Requested human clarification.")

        st.info("💡 Always verify AI results with the physical prescription.")


def render_unresolvable_card(extraction: Dict[str, Any], audit_data: Dict[str, Any]):
    """Render a dedicated Assisted Clarification Card for UNRESOLVABLE state."""
    st.markdown("""
        <div style="background-color: rgba(220, 53, 69, 0.1); border: 2px solid #dc3545; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #dc3545; margin-top: 0;">⚠️ Handwriting Too Unclear</h3>
            <p>The prescription handwriting is not clear enough for AI to safely identify the medicine. Hallucination risk is high.</p>
            <p><b>Please help by manually identifying the medicine:</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("assisted_clarification_form"):
        col1, col2 = st.columns(2)
        with col1:
            manual_name = st.text_input("Medicine Name", placeholder="e.g., Amoxicillin")
        with col2:
            med_type = st.selectbox("Type", ["Tablet", "Syrup", "Injection", "Drops", "Ointment", "Other"])
            
        submitted = st.form_submit_button("Confirm & Update Extraction", width="stretch")
        if submitted:
            if manual_name:
                # Add to extraction
                if "medicines" not in extraction:
                    extraction["medicines"] = []
                
                new_med = {
                    "name": f"{manual_name} ({med_type})",
                    "dosage": "Verifying...",
                    "frequency": "Verifying...",
                    "timing": [],
                    "instructions": f"Manually confirmed by user.",
                    "confidence": 1.0
                }
                extraction["medicines"].append(new_med)
                extraction["overall_confidence"] = 0.8 # Boosted by human verification
                
                # Manually override state so it doesn't block UI on rerun
                audit_data["ambiguity_state"] = "CLEAR"
                
                # Update DB
                if "prescription_id" in st.session_state:
                    update_prescription_data(
                        st.session_state.prescription_id,
                        extraction,
                        audit_data
                    )
                st.success(f"Added {manual_name}. Extraction updated.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("Please enter a medicine name.")


def render_ambiguity_resolver(audit_data: Dict[str, Any], extraction: Dict[str, Any]):
    """Render a UI block for resolving handwriting ambiguities and update state."""
    ambiguities = audit_data.get("ambiguities", [])
    if not ambiguities:
        return

    st.warning("🧐 **Handwriting Clarification Required**")
    st.write("The AI is uncertain about some items. Please confirm which one looks correct:")
    
    for i, amb in enumerate(ambiguities):
        with st.container():
            med_name = amb.get("medicine_name", "Unknown Medicine")
            field = amb.get("field", "name")
            issue = amb.get("issue")
            
            st.write(f"**Medicine:** `{med_name}`")
            st.caption(f"Clarification for **{field}**: {issue}")
            
            options = amb.get("options", [])
            cols = st.columns(len(options) + 1)
            
            for j, opt in enumerate(options):
                if cols[j].button(f"It's {opt}", key=f"amb_{i}_{j}", width="stretch"):
                    # Update the specific field in the extraction data
                    if "medicines" in extraction:
                        for med in extraction["medicines"]:
                            if med.get("name") == med_name:
                                med[field] = opt
                                med["confidence"] = 1.0  # User verified
                                break
                    
                    # Persist the update to DB
                    if "prescription_id" in st.session_state:
                        update_prescription_data(
                            st.session_state.prescription_id,
                            extraction,
                            audit_data
                        )
                    
                    # Remove from ambiguities
                    ambiguities.pop(i)
                    if not ambiguities:
                        audit_data["ambiguity_state"] = "CLEAR"
                    st.success(f"Confirmed {field}: {opt}")
                    time.sleep(0.5)
                    st.rerun()
            
            if cols[-1].button("None of these", key=f"amb_{i}_none", width="stretch"):
                # Just remove it and let user handle in chat
                ambiguities.pop(i)
                if not ambiguities:
                    audit_data["ambiguity_state"] = "CLEAR"
                st.info("Please clarify in the chat below.")
                time.sleep(0.5)
                st.rerun()
    st.divider()


def render_chat_mode_selector():
    """Render the mode selector for focused medical chat in the sidebar."""
    st.sidebar.subheader("🎯 Focused Medical Chat")
    modes = ["🩺 Explain Prescription", "⏰ Create Schedule"]
    
    selected_mode = st.sidebar.radio(
        "Select Chat Mode:",
        modes,
        horizontal=False,
        label_visibility="collapsed"
    )
    st.sidebar.divider()
    return " ".join(selected_mode.split(" ")[1:]) # Remove emoji for backend


def render_sidebar() -> Dict[str, Any]:
    """Render sidebar with conversation history and model controls."""
    
    # Focused Medical Chat Mode Selector
    chat_mode = render_chat_mode_selector()
    
    # Previous Conversations from DB
    st.sidebar.subheader("💬 Conversations")
    
    db_convs = get_all_prescriptions()
    active_id = st.session_state.get("prescription_id")
    
    if db_convs:
        for conv in db_convs:
            conv_id = conv["id"]
            title = f"📷 {conv['created_at'][:16]}" # Placeholder title from date
            is_active = conv_id == active_id
            
            col1, col2 = st.sidebar.columns([4, 1])
            
            with col1:
                button_type = "primary" if is_active else "secondary"
                if st.button(
                    title,
                    key=f"conv_{conv_id}",
                    width="stretch",
                    type=button_type
                ):
                    st.session_state.switch_to_prescription_id = conv_id
                    st.rerun()
            
            with col2:
                if st.button(
                    "🗑️",
                    key=f"delete_{conv_id}",
                    width="stretch",
                    help="Delete"
                ):
                    delete_prescription(conv_id)
                    
                    if is_active:
                        st.session_state.prescription_id = None
                        st.session_state.chat_memory.clear()
                    
                    st.rerun()
    else:
        st.sidebar.info("No conversations")
    
    
    # Model Settings - Collapsible
    with st.sidebar.expander("⚙️ Model Settings", expanded=False):
        DEFAULTS = {
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.9,
            "top_k": 40,
            "presence_penalty": 0.0
        }
        
        use_defaults = st.session_state.get("use_default_params", False)
        reset_counter = st.session_state.get("param_reset_counter", 0)
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULTS["temperature"] if use_defaults else st.session_state.get("_temperature", DEFAULTS["temperature"]),
            step=0.1,
            key=f"temperature_{reset_counter}"
        )
        st.session_state._temperature = temperature
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=256,
            max_value=4096,
            value=DEFAULTS["max_tokens"] if use_defaults else st.session_state.get("_max_tokens", DEFAULTS["max_tokens"]),
            step=256,
            key=f"max_tokens_{reset_counter}"
        )
        st.session_state._max_tokens = max_tokens
        
        top_p = st.slider(
            "Top-P",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULTS["top_p"] if use_defaults else st.session_state.get("_top_p", DEFAULTS["top_p"]),
            step=0.05,
            key=f"top_p_{reset_counter}"
        )
        st.session_state._top_p = top_p
        
        top_k = st.slider(
            "Top-K",
            min_value=1,
            max_value=100,
            value=DEFAULTS["top_k"] if use_defaults else st.session_state.get("_top_k", DEFAULTS["top_k"]),
            step=1,
            key=f"top_k_{reset_counter}"
        )
        st.session_state._top_k = top_k
        
        presence_penalty = st.slider(
            "Presence Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=DEFAULTS["presence_penalty"] if use_defaults else st.session_state.get("_presence_penalty", DEFAULTS["presence_penalty"]),
            step=0.1,
            key=f"presence_penalty_{reset_counter}"
        )
        st.session_state._presence_penalty = presence_penalty
    
    
    # Image Upload Section
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
        
    uploaded_file = st.sidebar.file_uploader(
        "📤 Upload Image",
        type=["png", "jpg", "jpeg"],
        help="Upload an image to start a new conversation",
        key=f"uploader_{st.session_state.uploader_key}"
    )
    
    st.sidebar.divider()
    
    # Action buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 New Chat", width="stretch", type="primary", key="new_chat_btn"):
            st.session_state.prescription_id = None
            st.session_state.active_img_hash = None
            st.session_state.chat_history = []
            st.session_state.chat_memory.clear()
            st.session_state.uploader_key += 1 # Force reset uploader widget
            st.rerun()
    
    with col2:
        if st.button("⚡ Reset Params", width="stretch", type="secondary", key="reset_params_btn"):
            st.session_state.param_reset_counter = reset_counter + 1
            for key in ["_temperature", "_max_tokens", "_top_p", "_top_k", "_presence_penalty"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.use_default_params = True
            st.rerun()
    
    return {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "presence_penalty": presence_penalty,
        "uploaded_file": uploaded_file,
        "chat_mode": chat_mode
    }

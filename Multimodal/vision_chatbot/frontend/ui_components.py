"""
Streamlit UI components - Sidebar only.
Clean minimal version ready for redesign.
"""
import streamlit as st
from typing import Dict, Any


def render_welcome_screen():
    """Render welcome screen when no conversation is active."""
    
    # Center content horizontally
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Title with icon on the right side
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <h1 style="font-size: 36px; font-weight: 700; margin: 0; color: #FFFFFF;">Welcome to Vision AI</h1>
                <div style="
                    width: 48px;
                    height: 48px;
                    background: linear-gradient(135deg, #9a1b74 0%, #ff6ec7 100%);
                    border-radius: 50%;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(154, 27, 116, 0.3);
                    margin-left: 1rem;
                ">
                    <span style="font-size: 24px;">💬</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Subtitle - larger
        st.markdown("<p style='text-align: center; font-size: 16px; color: #E0E0E0; margin: 0 0 2rem 0; line-height: 1.6;'>Start a new conversation by uploading an image and asking questions about it</p>", unsafe_allow_html=True)
        
        # How it works box - compact with larger title
        st.markdown("""
            <div style="background: linear-gradient(135deg, #9a1b74 0%, #ff6ec7 100%); border: 1px solid #9a1b74; border-radius: 10px; padding: 1.5rem;">
                <h3 style="font-size: 20px; font-weight: 700; margin: 0 0 1rem 0; text-align: center; color: #FFFFFF; text-transform: uppercase; letter-spacing: 1px;">How it works</h3>
                <p style="margin-bottom: 0.75rem; color: #F0F0F0; font-size: 15px; line-height: 1.5;"><strong style="color: #FFFFFF;">1.</strong> Click "New Chat" to start a conversation</p>
                <p style="margin-bottom: 0.75rem; color: #F0F0F0; font-size: 15px; line-height: 1.5;"><strong style="color: #FFFFFF;">2.</strong> Upload an image (PNG, JPG, or JPEG)</p>
                <p style="margin-bottom: 0.75rem; color: #F0F0F0; font-size: 15px; line-height: 1.5;"><strong style="color: #FFFFFF;">3.</strong> Ask questions about your image in natural language</p>
                <p style="margin-bottom: 0; color: #F0F0F0; font-size: 15px; line-height: 1.5;"><strong style="color: #FFFFFF;">4.</strong> Adjust model parameters in the sidebar to customize responses</p>
            </div>
        """, unsafe_allow_html=True)





def render_sidebar() -> Dict[str, Any]:
    """Render sidebar with conversation history and model controls."""
    
    # Previous Conversations
    st.sidebar.subheader("💬 Conversations")
    
    conversations = st.session_state.get("conversations", {})
    active_id = st.session_state.get("active_conversation_id")
    
    if conversations:
        sorted_convs = sorted(
            conversations.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        
        for conv_id, conv_data in sorted_convs:
            is_active = conv_id == active_id
            
            col1, col2 = st.sidebar.columns([4, 1])
            
            with col1:
                button_type = "primary" if is_active else "secondary"
                if st.button(
                    f"📷 {conv_data['title']}",
                    key=f"conv_{conv_id}",
                    width="stretch",
                    type=button_type,
                    help=f"Image: {conv_data['image_name']}"
                ):
                    st.session_state.switch_to_conversation = conv_id
                    st.rerun()
            
            with col2:
                if st.button(
                    "🗑️",
                    key=f"delete_{conv_id}",
                    width="stretch",
                    help="Delete"
                ):
                    del st.session_state.conversations[conv_id]
                    
                    if is_active:
                        st.session_state.active_conversation_id = None
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
    uploaded_file = st.sidebar.file_uploader(
        "📤 Upload Image",
        type=["png", "jpg", "jpeg"],
        help="Upload an image to start a new conversation"
    )
    
    st.sidebar.divider()
    
    # Action buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 New Chat", width="stretch", type="primary", key="new_chat_btn"):
            st.session_state.active_conversation_id = None
            st.session_state.chat_memory.clear()
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
        "stream": True,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "presence_penalty": presence_penalty,
        "uploaded_file": uploaded_file
    }

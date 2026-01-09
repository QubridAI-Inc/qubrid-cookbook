"""
Vision AI - Chat Interface
Clean minimal UI - ready for redesign.
"""
import streamlit as st
from PIL import Image
import time
import base64
from datetime import datetime
from typing import Dict, Any

from backend.chain import VisionChain
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from frontend.ui_components import render_sidebar, render_welcome_screen
from frontend.base_config import get_base_css

# Page configuration
st.set_page_config(
    page_title="Vision AI",
    page_icon="frontend/assets/qubrid_logo.png",
    layout="wide"
)

# Apply global design constraints
st.markdown(get_base_css(), unsafe_allow_html=True)


def get_banner_base64():
    """Load and encode banner image as base64."""
    with open("frontend/assets/qubrid_banner.png", "rb") as f:
        return base64.b64encode(f.read()).decode()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None
    
    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = InMemoryChatMessageHistory()
    
    if "vision_chain" not in st.session_state:
        st.session_state.vision_chain = VisionChain(st.session_state.chat_memory)

    if "last_uploaded_image_name" not in st.session_state:
        st.session_state.last_uploaded_image_name = None


def create_conversation(image: Image.Image, image_name: str) -> str:
    """Create a new conversation."""
    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    st.session_state.conversations[conversation_id] = {
        "title": image_name,
        "image": image,
        "image_name": image_name,
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    
    return conversation_id


def switch_conversation(conversation_id: str):
    """Switch to a different conversation and rebuild LangChain memory."""
    if conversation_id not in st.session_state.conversations:
        return
    
    st.session_state.active_conversation_id = conversation_id
    st.session_state.chat_memory.clear()
    
    conversation = st.session_state.conversations[conversation_id]
    for msg in conversation["messages"]:
        if isinstance(msg, HumanMessage):
            st.session_state.chat_memory.add_user_message(msg.content)
        elif isinstance(msg, AIMessage):
            st.session_state.chat_memory.add_ai_message(msg.content)


def add_message_to_conversation(role: str, content: str):
    """
    Add message to active conversation (UI storage only).
    IMPORTANT: Does NOT touch LangChain memory.
    """
    if not st.session_state.active_conversation_id:
        return
    
    if role == "human":
        message = HumanMessage(content=content)
    else:
        message = AIMessage(content=content)
    
    conversation = st.session_state.conversations[st.session_state.active_conversation_id]
    conversation["messages"].append(message)
    
    # Update title with first user message
    if role == "human" and len(conversation["messages"]) == 1:
        title_text = content[:27] + ("..." if len(content) > 27 else "")
        conversation["title"] = f"🔍 {title_text}"


def get_active_conversation() -> Dict[str, Any]:
    """Get the currently active conversation."""
    if not st.session_state.active_conversation_id:
        return None
    return st.session_state.conversations.get(st.session_state.active_conversation_id)


def main():
    """Main chat application logic."""
    initialize_session_state()
    
    # Handle conversation switching from sidebar
    if "switch_to_conversation" in st.session_state:
        conv_id = st.session_state.switch_to_conversation
        switch_conversation(conv_id)
        del st.session_state.switch_to_conversation
    
    # Branded Header with Banner Background
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #9a1b74 0%, #ff6ec7 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <h1 style="
                    font-size: 48px;
                    font-weight: 700;
                    line-height: 1.1;
                    margin: 0;
                    padding: 0;
                    color: #FFFFFF;
                ">Vision AI</h1>
                <p style="
                    font-size: 20px;
                    font-weight: 400;
                    line-height: 1.4;
                    margin: 4px 0 0 0;
                    padding: 0;
                    color: #F0F0F0;
                ">Vision-based AI Chatbot</p>
                <p style="
                    font-size: 16px;
                    font-weight: 400;
                    line-height: 1.4;
                    margin: 2px 0 0 0;
                    padding: 0;
                    color: #E0E0E0;
                ">Powered by Qubrid AI</p>
            </div>
            <div style="flex-shrink: 0; margin-left: 2rem;">
                <img src="data:image/png;base64,{banner_base64}" style="height: 80px; opacity: 0.9;" />
            </div>
        </div>
    """.format(banner_base64=get_banner_base64()), unsafe_allow_html=True)
    
    # Render sidebar and get model config + uploaded file
    model_config = render_sidebar()
    uploaded_file = model_config.pop("uploaded_file", None)
    
    # Handle image upload
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Only create new conversation if different image
        if st.session_state.last_uploaded_image_name != uploaded_file.name:
            conversation_id = create_conversation(image, uploaded_file.name)
            switch_conversation(conversation_id)
            
            st.session_state.last_uploaded_image_name = uploaded_file.name
            st.success(f"New conversation: {uploaded_file.name}")

    
    # Main chat area
    active_conv = get_active_conversation()
    
    if active_conv:
        # Display image in collapsible section
        with st.expander("🖼️ View Image", expanded=False):
            st.image(active_conv["image"], width=200)
        
        st.divider()
        
        # Display messages
        for message in active_conv["messages"]:
            if message.type == "human":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message.content)
            elif message.type == "ai":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message.content)
        
        # Chat input
        user_query = st.chat_input("Ask about the image...")
        
        if user_query:
            # Add user message
            add_message_to_conversation("human", user_query)
            
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_query)
            
            # Get AI response
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                
                try:
                    response = st.session_state.vision_chain.stream(
                        image=active_conv["image"],
                        user_query=user_query,
                        temperature=model_config.get("temperature", 0.7),
                        max_tokens=model_config.get("max_tokens", 1024),
                        top_p=model_config.get("top_p", 0.9),
                        top_k=model_config.get("top_k", 40),
                        presence_penalty=model_config.get("presence_penalty", 0.0)
                    )
                    
                    full_response = ""
                    chunk_buffer = ""
                    
                    for chunk in response:
                        chunk_buffer += chunk
                        
                        if len(chunk_buffer) >= 3:
                            full_response += chunk_buffer
                            message_placeholder.markdown(full_response + "▌")
                            chunk_buffer = ""
                            time.sleep(0.02)
                    
                    if chunk_buffer:
                        full_response += chunk_buffer
                    
                    message_placeholder.markdown(full_response)
                    
                    add_message_to_conversation("ai", full_response)
                    st.rerun()
                
                except Exception as e:
                    message_placeholder.error(f"Error: {str(e)}")
    else:
        # Show welcome screen when no conversation is active
        render_welcome_screen()



if __name__ == "__main__":
    main()

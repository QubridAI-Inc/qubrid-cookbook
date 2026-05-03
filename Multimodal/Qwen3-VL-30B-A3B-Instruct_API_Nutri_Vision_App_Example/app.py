"""
NutriVision AI - Production Application
"""
import streamlit as st
from PIL import Image
import time
import json
from datetime import datetime

# Core imports
from config import Config
from prompts import DETAILED_NUTRITION_PROMPT, CHAT_SYSTEM_PROMPT
from utils.api_client import call_qubrid_api, call_qubrid_api_stream
from utils.image_processor import encode_image_to_base64
from utils.parser import parse_nutrition_data
from utils.styles import get_custom_css

# UI Components
from utils.ui_components import (
    display_macro_row, 
    display_health_bar, 
    display_metrics_footer,
    format_analysis_report
)

Config.validate()

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'nutrition_data' not in st.session_state:
    st.session_state.nutrition_data = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    theme = st.radio("🌗 Theme", ["Light", "Dark"], horizontal=True, index=0)
    user_goal = st.selectbox("🎯 Your Goal", ["General Health", "Weight Loss", "Muscle Gain", "Athletic Performance"])
    enable_stream = st.toggle("⚡ Enable Streaming", value=True)
    
    st.markdown("---")
    st.markdown("### 📸 Upload Food Image")
    
    uploaded_file = st.file_uploader("Drag & drop or browse", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        # --- FIX APPLIED HERE (Line 60) ---
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        if 'last_uploaded' not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            st.session_state.uploaded_image = image
            st.session_state.image_base64 = encode_image_to_base64(image)
            st.session_state.last_uploaded = uploaded_file.name
            
    st.markdown("---")
    if st.session_state.history:
        st.markdown("### 📜 Recent History")
        for i, item in enumerate(reversed(st.session_state.history)):
            if i >= 3: break
            st.caption(f"🕒 {item['time']} - {item['dish']}")

    if st.button("🔄 Reset App", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- INJECT CSS ---
st.markdown(get_custom_css(theme), unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🍽️ NutriVision AI</div>
    <div class="hero-subtitle">Your AI-Powered Nutrition Analysis Companion</div>
    <div class="hero-badge">⚡ Powered by Advanced Vision AI</div>
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    st.markdown(f"""
    <div style="text-align: center; opacity: 0.6; margin-top: 4rem;">
        <h3 style="color: {'#e2e8f0' if theme == 'Dark' else '#94a3b8'};">👈 Upload a food image to start</h3>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- ANALYSIS LOGIC ---
    if not st.session_state.analyzed:
        st.markdown("### 🔍 Ready to Analyze")
        if st.button("🚀 Analyze Food", type="primary", use_container_width=True):
            st.session_state.analyzing = True
            
            with st.spinner("🔍 Analyzing nutritional content..."):
                try:
                    # 1. Call API for Analysis (Strict JSON Mode)
                    messages = [{"role": "user", "content": DETAILED_NUTRITION_PROMPT, "image": st.session_state.image_base64}]
                    
                    start_time = time.time()
                    # We typically don't stream the JSON analysis because we need to parse it all at once
                    response_text = call_qubrid_api(messages) 
                    end_time = time.time()
                    
                    # 2. Parse Data
                    data = parse_nutrition_data(response_text)
                    st.session_state.nutrition_data = data
                    st.session_state.analyzed = True
                    
                    # 3. Stats & History
                    st.session_state.last_stats = (len(response_text)//4, end_time-start_time, (len(response_text)//4)/(end_time-start_time))
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "dish": data.get('dish_name', 'Unknown')
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- RESULTS DISPLAY ---
    if st.session_state.analyzed:
        data = st.session_state.nutrition_data
        
        # 1. Dish Title
        dish_name = data.get('dish_name', 'Unknown Dish')
        st.markdown(f"""
        <div class="dish-title-card">
            <h2 class="dish-name">🍽️ {dish_name}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Nutrition Cards (RESTORED HERE)
        display_macro_row(data)
        display_health_bar(data.get('health_score', 0))
        
        # 3. Detailed Report
        with st.expander("📋 View Full Analysis Report", expanded=True):
            report = format_analysis_report(data)
            st.markdown(report)
            
        # 4. Stats Footer
        if hasattr(st.session_state, 'last_stats'):
            tokens, duration, tps = st.session_state.last_stats
            display_metrics_footer(tokens, duration, tps)
            
        # 5. Chat Interface
        st.markdown("---")
        st.markdown("### 💬 Ask Follow-Up Questions")
        
        for msg in st.session_state.messages:
            cls = "chat-message-user" if msg['role'] == 'user' else "chat-message-ai"
            st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)
            
        if prompt := st.chat_input("Ask about this food..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# --- CHAT GENERATION LOGIC ---
if st.session_state.analyzed and st.session_state.messages and st.session_state.messages[-1]['role'] == 'user':
    with st.spinner("Thinking..."):
        # Create a clean context for the chat
        # We inject the parsed data so the AI knows what it's talking about
        data_context = json.dumps(st.session_state.nutrition_data, indent=2)
        system_msg = CHAT_SYSTEM_PROMPT.format(nutrition_data=data_context)
        
        # Build message history for the API
        api_messages = [{"role": "system", "content": system_msg}]
        
        # Add conversation history
        for msg in st.session_state.messages:
            api_messages.append(msg)
            
        # Call API (Streamed)
        full_response = ""
        try:
            for chunk in call_qubrid_api_stream(api_messages):
                full_response += chunk
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"Chat Error: {e}")

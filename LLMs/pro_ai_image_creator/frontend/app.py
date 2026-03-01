import streamlit as st
import sys
import os
import time
import base64

# Path setup for project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, create_session, get_history, get_sessions
from frontend.sidebar import render_sidebar
from frontend.styles import get_css
from backend.graph import build_graph
from config.settings import API_KEY, GENERATED_IMAGES_DIR
from PIL import Image

# --- INITIALIZATION ---
init_db()
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

# --- Qubrid Branding in Browser Tab ---
# 1. Load the image from your local asset folder
# Using a relative path makes it "portable" so it works on any computer
logo_path = "frontend/assets/qubrid_logo.png"
logo_image = Image.open(logo_path)

# 2. Set the branding using the loaded image object
st.set_page_config(
    page_title="Advanced AI Image Creation",
    page_icon=logo_image, # Pass the image object here, not the path string
    layout="wide",
    initial_sidebar_state="expanded"
)

# Persistent state management
if "current_session_id" not in st.session_state:
    st.session_state["current_session_id"] = None
if "auto_prompt" not in st.session_state:
    st.session_state["auto_prompt"] = None

# Inject Global Glassmorphism CSS from styles.py
st.markdown(get_css(), unsafe_allow_html=True)

# Additional UI Polish for Status Widgets and Dark Mode Force
st.markdown("""
<style>
    /* 1. Prevent Background Dimming during generation */
    .st-emotion-cache-6qob1r { 
        background-color: transparent !important; 
    }
    
    /* 2. Generation Status Box styling */
    [data-testid="stStatusWidget"] { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        backdrop-filter: blur(10px); 
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
    }

    /* 3. Force Sidebar Title visibility */
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: white !important;
        opacity: 1 !important;
    }

    /* 4. Workspace Chat Input (Bottom bar) logic */
    [data-testid="stChatInput"] textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPERS ---

def run_generation(session_id, user_prompt):
    """Orchestrates AI generation with a transparent status bar."""
    with st.status("⚡ Quantum rendering in progress...", expanded=True) as status:
        st.write("Initializing Stable Diffusion 3.5...")
        prog = st.progress(20)
        time.sleep(0.3)
        
        graph = build_graph()
        result = graph.invoke({
            "session_id": session_id, 
            "user_prompt": user_prompt, 
            "generated_image_url": None, 
            "error": None
        })
        
        prog.progress(100)
        status.update(label="✨ Creation Complete!", state="complete", expanded=False)
        return result

def get_download_link(img_path):
    """Encodes image for high-res download."""
    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'''<a href="data:image/png;base64,{b64}" download="art.png" 
                  style="display:inline-block; padding:10px 20px; text-decoration:none; 
                  color:white; margin-top:10px; border-radius:12px; 
                  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1);">
                  ⬇️ Download High-Res</a>'''
    except: return ""

# --- RENDER SIDEBAR ---
render_sidebar()

# --- VIEW CONTROLLER ---

if st.session_state["current_session_id"] is None:
    # --- LANDING VIEW ---
    st.markdown("""
        <div style="text-align: center; padding: 60px 20px 20px 20px;">
            <div class="hero-title">Advanced AI<br>Image Creation</div>
            <div class="hero-subtitle">Transform your imagination into breathtaking visuals with our professional Al studio. Optimized for Game Assets, Concept Art, and Photorealism using <b>Stable Diffusion 3.5</b>.</div>
        </div>
    """, unsafe_allow_html=True)

    # Styles Grid
    st.markdown("<h4 style='text-align:center; color:rgba(255,255,255,0.5); margin-bottom: 20px;'>🔥 Curated Styles</h4>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    def card(col, title, img, prompt):
        with col:
            st.markdown(f'''<div class="glass-card">
                <img src="{img}" style="width:100%; height:180px; object-fit:cover; opacity:0.8;">
                <div style="padding:15px; font-weight:bold; color:white;">{title}</div>
            </div>''', unsafe_allow_html=True)
            if st.button("Create", key=f"btn_{title}", use_container_width=True):
                st.session_state["current_session_id"] = create_session(title=prompt)
                st.session_state["auto_prompt"] = prompt
                st.rerun()

    card(c1, "Cyberpunk", "https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=600", "Cyberpunk city, neon, rain, 8k")
    card(c2, "Fantasy", "https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?w=600", "Epic fantasy castle, magic, clouds")
    card(c3, "Portrait", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600", "Cinematic portrait, detailed skin, 85mm")
    card(c4, "Isometric", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600", "Isometric cute magic shop, 3d render")

    # The Centered Floating Pill Input
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 2, 1])
    with col_m:
        # Combined Input logic - CSS handles the button overlay
        landing_prompt = st.text_input("Landing", placeholder="✨ Describe your vision...", key="landing_input", label_visibility="hidden")
        
        if landing_prompt:
            st.session_state["current_session_id"] = create_session(title=landing_prompt)
            st.session_state["auto_prompt"] = landing_prompt
            st.rerun()
            
        st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.3); font-size:0.8rem; margin-top:10px;'>Powered by Qubrid AI</div>", unsafe_allow_html=True)

else:
    # --- STUDIO WORKSPACE ---
    st.markdown("## 🎨 Studio Workspace")
    
    history = get_history(st.session_state["current_session_id"])
    for msg in history:
        if msg['role'] == 'user':
            st.markdown(f'<div class="user-msg"><div>👤</div><div>{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            if msg['image_url'] and os.path.exists(msg['image_url']):
                st.image(msg['image_url']) 
                st.markdown(get_download_link(msg['image_url']), unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:30px'></div>", unsafe_allow_html=True)

    # Trigger generation for first entry from landing
    if st.session_state.get("auto_prompt"):
        p = st.session_state["auto_prompt"]
        st.session_state["auto_prompt"] = None 
        run_generation(st.session_state["current_session_id"], p)
        st.rerun()

    # Bottom Workspace Chat Input
    prompt = st.chat_input("Describe your vision...")
    if prompt:
        run_generation(st.session_state["current_session_id"], prompt)
        st.rerun()

"""
Reusable UI components for SnapCode AI.
Handles the rendering of headers, upload zones, previews, code boxes, and footer.
"""
import streamlit as st
import streamlit.components.v1 as components
from config.settings import APP_NAME, APP_TAGLINE, SUPPORTED_FORMATS

def render_header():
    """
    Renders the main title, tagline, and the animated "powered by" badge.
    """
    # 10vh push to center it vertically on the screen
    st.markdown(f"<h1 style='text-align: center; margin-top: 10vh; margin-bottom: 0.1em; font-size: 4rem; font-weight: 900; background: linear-gradient(135deg, #4F8EF7 0%, #00D4FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{APP_NAME} ⚡</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #f8fafc; font-weight: 500; font-size: 1.3rem; margin-top: 0.5rem; margin-bottom: 2rem; max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.6;'>Transform any UI screenshot, wireframe, or mockup right into pixel-perfect HTML and Tailwind CSS.</p>", unsafe_allow_html=True)
    
    badge_html = """
    <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 4rem; margin-top: 1.5rem;'>
        <div style='background: rgba(30, 30, 40, 0.8); border: 2px solid rgba(79,142,247,0.5); padding: 0.6rem 1.5rem; border-radius: 30px; display: inline-flex; align-items: center; gap: 10px; font-size: 1rem; color: #ffffff; font-weight: 600; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.15);'>
            <span style='width: 10px; height: 10px; border-radius: 50%; background-color: #10b981; display: inline-block; box-shadow: 0 0 10px #10b981, 0 0 20px #10b981; animation: pulse 2s infinite;'></span>
            Supercharged by Kimi K2.5 Vision <span style='opacity: 0.5; margin: 0 8px;'>✦</span> Powered natively by Qubrid AI
        </div>
    </div>
    <style>
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
        100% { opacity: 1; transform: scale(1); }
    }
    </style>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

def render_upload_zone(upload_key="file_uploader"):
    """
    Renders the file uploader and instruction text.
    """
    st.markdown("<div style='text-align: center; margin-bottom: 1.5rem; font-size: 1.2rem; font-weight: 600; color: #f8fafc;'>Upload any UI screenshot, wireframe, or design</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Image",
        type=SUPPORTED_FORMATS,
        label_visibility="collapsed",
        key=upload_key
    )
    
    # Render format chips
    chips_html = ("<div style='display: flex; gap: 6px; justify-content: center; margin-top: -10px; margin-bottom: 20px;'>" + 
                  "".join([f"<span style='background: #1a1a2e; color: #4F8EF7; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: 600; border: 1px solid rgba(79,142,247,0.2); text-transform: uppercase;'>{fmt}</span>" for fmt in SUPPORTED_FORMATS]) + 
                  "</div>")
    st.markdown(chips_html, unsafe_allow_html=True)
    
    return uploaded_file

def render_image_preview(uploaded_file, width, height):
    """
    Shows the uploaded image in a styled card.
    """
    st.markdown("<div style='margin-bottom: 0.5rem; font-weight: 600; color: #e2e8f0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;'>Your Design</div>", unsafe_allow_html=True)
    
    # Show dimensions badge
    st.markdown(f"<div style='margin-bottom: 10px; display: inline-block; background: rgba(0,212,255,0.1); color: #00D4FF; font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; font-weight: 600;'>{width} × {height} px</div>", unsafe_allow_html=True)
    
    st.image(uploaded_file, width="stretch")

def render_code_output(html_code: str, tokens: int, latency: float):
    """
    Shows the generated HTML, metrics, download button, and preview.
    """
    # Metrics Row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tokens Used", f"{tokens:,}")
    with col2:
        st.metric("Generation Time", f"{latency / 1000:.2f}s")
        
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    
    # Download Code
    st.download_button(
        label="⬇️ Download HTML",
        data=html_code,
        file_name="snapcode_output.html",
        mime="text/html",
        width="stretch"
    )
    
    # Live Preview Expander
    with st.expander("Live HTML Preview", expanded=True):
        st.info("Note: The preview is embedded in an iframe. For best results, download the HTML and view in a full browser window.")
        # Increased height from 500 to 900 to prevent the generated design from cutting off visually
        components.html(html_code, height=900, scrolling=True)
    
    # Code View
    st.markdown("<div style='margin-top: 1rem; margin-bottom: 0.5rem; font-weight: 600; color: #e2e8f0;'>Generated Code</div>", unsafe_allow_html=True)
    st.code(html_code, language="html")

def render_footer():
    """
    Renders a centered subtle footer.
    """
    footer_html = """
    <div style='text-align: center; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.05); color: #64748b; font-size: 0.8rem;'>
        Built with Kimi K2.5 × Qubrid AI | SnapCode AI
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

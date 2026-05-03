"""
Custom CSS for ThinkTrace AI Streamlit UI.
Inject via st.markdown('<style>...</style>', unsafe_allow_html=True)
"""
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Global Theme */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        background-color: #FDFBF7 !important;
        color: #333333;
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(253, 251, 247, 0) !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #F4EFE6 !important;
    }
    
    /* Brain Pulse Animated Header */
    .brain-pulse-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(270deg, #5E6C3A, #D28A47, #5E6C3A);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: BrainPulse 4s ease infinite;
        margin-bottom: 0px;
        text-align: center;
    }
    @keyframes BrainPulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Taglines and badges */
    .tagline {
        color: #666666;
        font-size: 1.2rem;
        margin-top: -10px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .badge-container {
        text-align: center;
        margin-bottom: 20px;
    }

    .brand-badge {
        display: inline-flex;
        align-items: center;
        background-color: rgba(94, 108, 58, 0.1);
        border: 1px solid rgba(94, 108, 58, 0.3);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        color: #5E6C3A;
        font-weight: 600;
    }
    .pulse-dot {
        height: 8px;
        width: 8px;
        background-color: #5E6C3A;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 8px rgba(94, 108, 58, 0.8);
        animation: PulseDot 2s infinite;
    }
    @keyframes PulseDot {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(94, 108, 58, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(94, 108, 58, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(94, 108, 58, 0); }
    }
    
    /* Input Area */
    div[data-testid="stTextArea"] label {
        color: #D28A47 !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Progress bar overrides for Thinking Depth */
    .stProgress > div > div > div > div {
        background-color: #5E6C3A;
    }
    
    /* Blinking cursor for loading state */
    .blinking-cursor::after {
        content: "▋";
        color: #5E6C3A;
        animation: blink 1s step-start infinite;
    }
    @keyframes blink { 50% { opacity: 0; } }

    /* Make code block backgrounds subtle beige for reasoning */
    div.stCodeBlock > div {
        background-color: #F4EFE6 !important;
        border-left: 4px solid #5E6C3A !important;
        border-radius: 0 8px 8px 0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    /* Ensure code text color matches the light theme closely */
    div.stCodeBlock code {
        color: #333333 !important;
    }

    /* Start Button style */
    div[data-testid="stButton"] button {
        background-color: #5E6C3A;
        color: #FFFBF7;
        border: none;
        box-shadow: 0 2px 8px rgba(94, 108, 58, 0.3);
    }
    div[data-testid="stButton"] button:hover {
        background-color: #4A552D;
        color: #FFFBF7;
        box-shadow: 0 4px 12px rgba(94, 108, 58, 0.4);
        border: none;
    }

    /* Answer header highlight */
    .answer-highlight {
        color: #D28A47;
    }

    /* Thinking Loading container */
    .thinking-loading-container {
        background-color: #F4EFE6;
        padding: 20px;
        border-left: 4px solid #D28A47;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }
    
    /* Center the category radio buttons */
    div[data-testid="stRadio"] > div {
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

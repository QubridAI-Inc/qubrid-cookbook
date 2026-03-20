"""
Styles and CSS injection for the SnapCode AI application.
"""
import streamlit as st

def apply_custom_styles():
    """
    Injects custom CSS to style the Streamlit app.
    Design language: deep dark background, glass morphism cards, electric blue accents.
    """
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Fira+Code:wght@400&display=swap');

    /* Thin top gradient bar */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4F8EF7, #00D4FF);
        z-index: 999999;
    }

    /* Base Styling */
    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #0a0a0f !important;
        color: #f0f0f5 !important;
    }



    /* Hide default footer */
    footer {visibility: hidden;}

    /* Typography */
    h1, h2, h3 {
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }

    /* Primary Action Button (Generate Code) */
    div[data-testid="stBaseButton-primary"] > button {
        background: linear-gradient(135deg, #4F8EF7 0%, #00D4FF 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(79, 142, 247, 0.3) !important;
        width: 100% !important;
    }
    div[data-testid="stBaseButton-primary"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(79, 142, 247, 0.5) !important;
        background: linear-gradient(135deg, #5c9df7 0%, #16dfff 100%) !important;
    }
    div[data-testid="stBaseButton-primary"] > button:active {
        transform: translateY(0) !important;
    }

    /* Secondary / Sidebar Buttons (History) */
    div[data-testid="stBaseButton-secondary"] > button {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #94a3b8 !important;
        font-weight: 400 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        text-align: left !important;
    }
    div[data-testid="stBaseButton-secondary"] > button:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #f8fafc !important;
        border-color: rgba(79, 142, 247, 0.4) !important;
    }

    /* Download Button */
    .stDownloadButton > button {
        background: transparent !important;
        color: #4F8EF7 !important;
        border: 1px solid rgba(79, 142, 247, 0.4) !important;
        box-shadow: none !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(79, 142, 247, 0.1) !important;
        border-color: #4F8EF7 !important;
        box-shadow: 0 0 10px rgba(79, 142, 247, 0.2) !important;
    }

    /* File Uploader styling */
    .stFileUploader > div > div {
        background: rgba(26, 26, 46, 0.4) !important;
        border: 2px dashed rgba(79, 142, 247, 0.5) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease !important;
    }
    .stFileUploader > div > div:hover {
        border-color: #4F8EF7 !important;
        background: rgba(79, 142, 247, 0.05) !important;
    }
    
    /* Code output block styles */
    .stCode {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    code {
        font-family: 'Fira Code', monospace !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1a2e !important;
        border-radius: 12px !important;
        border: 1px solid rgba(79, 142, 247, 0.2) !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        border: 1px solid rgba(79, 142, 247, 0.2) !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        background: #0a0a0f !important;
    }

    /* Custom Cards / Metrics */
    div[data-testid="stMetricValue"] {
        color: #00D4FF !important;
        font-weight: 800 !important;
    }

    /* Alerts and spinners */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    .stSpinner > div > div {
        border-color: #4F8EF7 !important;
        border-bottom-color: transparent !important;
    }
    
    /* Form inputs (text input) */
    .stTextInput > div > div > input {
        background-color: #1a1a2e !important;
        border: 1px solid rgba(79, 142, 247, 0.3) !important;
        border-radius: 10px !important;
        color: white !important;
        transition: all 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00D4FF !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
    }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

"""
Global UI configuration for Vision AI.
Clean, consolidated purple theme styling.
"""

def get_base_css() -> str:
    """
    Returns consolidated base CSS for purple theme.
    Single source of truth for all styling.
    """
    return """
    <style>
        /* ===== GLOBAL THEME ===== */
        .stApp {
            background-color: #1a0b2e;
            color: #FFFFFF;
        }
        
        /* System fonts */
        body, .stMarkdown, .stText, p, span, div:not([data-testid*="stIcon"]):not(.material-icons) {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            color: #FFFFFF;
        }
        
        /* Allow icons to render */
        [data-testid*="stIcon"], .material-icons, .material-icons-outlined {
            font-family: 'Material Icons', 'Material Icons Outlined' !important;
        }
        
        /* Minimal animations */
        * {
            transition-duration: 0.1s !important;
        }
        
        /* ===== HEADER ===== */
        header[data-testid="stHeader"] {
            background-color: #1a0b2e !important;
        }
        
        .stDeployButton {
            display: none;
        }
        
        /* ===== MAIN AREA ===== */
        .stMain .block-container {
            max-width: 100%;
            padding: 1rem 2rem 3rem 2rem !important;
        }
        
        .stMain {
            overflow-anchor: none;
        }
        
        /* Images */
        .stMain img {
            display: block;
            margin: 0 auto;
            max-width: 200px !important;
            max-height: 200px !important;
            width: auto !important;
            height: auto !important;
            border-radius: 8px;
            object-fit: contain;
        }
        
        .stMain [data-testid="stImage"] {
            max-width: 200px !important;
            margin: 0 auto;
        }
        
        /* Expanders in main area */
        .stMain details,
        .stMain [data-testid="stExpander"] {
            background-color: #1a0b2e !important;
        }
        
        .stMain details summary,
        .stMain [data-testid="stExpander"] summary,
        .stMain .streamlit-expanderHeader {
            background-color: #3a2a5a !important;
            color: #FFFFFF !important;
            border-color: #4a3a6a !important;
        }
        
        /* Target all nested divs in expander summary */
        .stMain details summary > div,
        .stMain [data-testid="stExpander"] summary > div,
        .stMain details summary div,
        .stMain [data-testid="stExpander"] summary div {
            background-color: transparent !important;
        }
        
        .stMain .streamlit-expanderContent {
            background-color: #1a0b2e !important;
        }
        
        /* Chat input */
        .stMain [data-testid="stChatInput"],
        .stMain [data-testid="stChatInput"] > div,
        .stMain [data-testid="stBottom"],
        .stMain [data-testid="stBottom"] > div {
            background-color: #1a0b2e !important;
        }
        
        .stMain [data-testid="stChatInput"] textarea {
            background-color: #3a2a5a !important;
            color: #FFFFFF !important;
            border-color: #4a3a6a !important;
        }
        
        .stMain [data-testid="stChatInput"] textarea::placeholder {
            color: #B0B0B0 !important;
        }
        
        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {
            background-color: #2a1a4a !important;
        }
        
        /* Sidebar text */
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {
            color: #FFFFFF !important;
        }
        
        /* Sidebar inputs */
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea {
            background-color: #3a2a5a !important;
            color: #FFFFFF !important;
            border-color: #4a3a6a !important;
        }
        
        /* Sidebar buttons */
        section[data-testid="stSidebar"] button {
            color: #FFFFFF !important;
        }
        
        section[data-testid="stSidebar"] button[kind="secondary"],
        section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
            background-color: #3a2a5a !important;
            border: 1px solid #4a3a6a !important;
        }
        
        section[data-testid="stSidebar"] button[kind="secondary"]:hover,
        section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
            background-color: #4a3a6a !important;
        }
        
        /* Sidebar expanders */
        section[data-testid="stSidebar"] details,
        section[data-testid="stSidebar"] .streamlit-expanderContent {
            background-color: #2a1a4a !important;
        }
        
        section[data-testid="stSidebar"] details summary,
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            background-color: #3a2a5a !important;
            color: #FFFFFF !important;
            border-color: #4a3a6a !important;
        }
        
        /* Sidebar file uploader */
        section[data-testid="stSidebar"] [data-testid="stFileUploader"],
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div {
            background-color: #3a2a5a !important;
            border-color: #4a3a6a !important;
        }
        
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] small {
            color: #E0E0E0 !important;
        }

        /* Main area file uploader */
        .stMain [data-testid="stFileUploader"],
        .stMain [data-testid="stFileUploader"] > div,
        .stMain [data-testid="stFileUploaderDropzone"],
        .stMain [data-testid="stFileUploaderDropzone"] > div,
        .stMain [data-testid="stFileUploaderDropzone"] section,
        .stMain [data-testid="stFileUploaderDropzone"] button {
            background-color: #3a2a5a !important;
            border-color: #4a3a6a !important;
        }

        .stMain [data-testid="stFileUploader"] label,
        .stMain [data-testid="stFileUploader"] small,
        .stMain [data-testid="stFileUploader"] span {
            color: #E0E0E0 !important;
        }

        /* File uploader button */
        .stMain [data-testid="stFileUploader"] button {
            background-color: #4a3a6a !important;
            color: #FFFFFF !important;
            border-color: #5a4a7a !important;
        }

        .stMain [data-testid="stFileUploader"] button:hover {
            background-color: #5a4a7a !important;
        }

        
        /* ===== UNIVERSAL OVERRIDES ===== */
        hr {
            margin: 1rem 0 1.5rem 0 !important;
        }
        
        .stButton button,
        .stTextInput input,
        .stSelectbox select {
            box-shadow: none !important;
            border-radius: 4px;
        }
        
        /* ===== PINK/MAGENTA THEME OVERRIDES ===== */
        /* Change all orange (#ff4b4b) elements to pink/magenta */
        
        /* Primary buttons (New Chat, etc.) */
        [data-testid="stBaseButton-primary"],
        button[kind="primary"] {
            background-color: #d946a6 !important;
            border-color: #d946a6 !important;
        }
        
        [data-testid="stBaseButton-primary"]:hover,
        button[kind="primary"]:hover {
            background-color: #c23594 !important;
            border-color: #c23594 !important;
        }
        
        [data-testid="stBaseButton-primary"]:active,
        button[kind="primary"]:active {
            background-color: #b02482 !important;
        }
        
        /* Sliders - thumb and filled track */
        [data-testid="stSlider"] div[role="slider"] {
            background-color: #d946a6 !important;
        }
        
        /* Slider filled track (progress portion) */
        [data-testid="stSlider"] div[data-baseweb="slider"] div[data-baseweb="slider"] > div:first-child {
            background: linear-gradient(90deg, #d946a6 0%, #d946a6 100%) !important;
        }
        
        /* Chat input focus border */
        [data-testid="stChatInput"]:focus-within,
        [data-testid="stChatInput"] textarea:focus {
            outline: none !important;
            border-color: #d946a6 !important;
        }
        
        /* Conversation history active button */
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:active,
        section[data-testid="stSidebar"] button[kind="secondary"]:active {
            background-color: #d946a6 !important;
            border-color: #d946a6 !important;
        }
        
        /* File uploader focus state */
        [data-testid="stFileUploader"]:focus-within {
            box-shadow: 0 0 0 1px #d946a6 !important;
        }
        
        /* Any other focus states */
        *:focus-visible {
            outline-color: #d946a6 !important;
        }
        
        /* Tooltip styling - change white to purple */
        [data-testid="stTooltipIcon"],
        .stTooltipIcon,
        [role="tooltip"],
        div[data-baseweb="tooltip"] {
            background-color: #3a2a5a !important;
            color: #FFFFFF !important;
        }
        
        /* Tooltip content */
        div[data-baseweb="tooltip"] > div {
            background-color: #3a2a5a !important;
            color: #FFFFFF !important;
        }
    </style>
    """


# Font size constants 
FONT_SIZES = {
    "app_title": "42px",
    "section_header": "18px",
    "chat_text": "14px",
    "helper_text": "12px",
    "button_text": "14px",
}

# Color constants
COLORS = {
    "background": "#1a0b2e",
    "sidebar_bg": "#2a1a4a",
    "element_bg": "#3a2a5a",
    "border": "#4a3a6a",
    "text_primary": "#FFFFFF",
    "text_secondary": "#E0E0E0",
}

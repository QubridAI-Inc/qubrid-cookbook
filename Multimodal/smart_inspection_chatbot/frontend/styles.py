import streamlit as st  # Main library to inject HTML/CSS into the app

def apply_custom_styles(mode="Light"):
    """
    Injects custom CSS variables and rules to control the look and feel 
    of the application. It supports dynamic theming (Light vs Dark).
    
    Args:
        mode (str): 'Light' or 'Dark'. Defaults to 'Light'.
    """
    
    # --- COLOR PALETTES DEFINITION ---
    # We define all our colors in Python dictionaries first.
    # This makes it easy to swap them out based on the 'mode' argument.
    
    if mode == "Dark":
        # Cyberpunk / Engineering Dark Theme
        # Designed for low-light environments (like factory control rooms).
        colors = {
            "bg_main": "#0e1117",           # Very dark blue-grey (Main Background)
            "bg_panel": "#161b22",          # Slightly lighter grey (Cards/Chat bubbles)
            "sidebar_bg": "#010409",        # Almost black (Sidebar)
            "text_primary": "#e6edf3",      # High contrast white for readability
            "text_secondary": "#8b949e",    # Soft grey for less important text
            "border_color": "#30363d",      # Subtle dark borders
            "accent_primary": "#1f6feb",    # Bright blue for primary actions
            "input_bg": "#0d1117",          # Very dark for text input boxes
            "table_header_bg": "#21262d",   # distinctive background for table headers
            "table_border": "#30363d",      # matching border color
            "button_bg": "#21262d"          # Dark button background to blend in
        }
    else:
        # Precision Light (Default)
        # Clean, professional look similar to Jira or GitHub Light.
        colors = {
            "bg_main": "#f4f5f7",           # Light grey (Main Background)
            "bg_panel": "#ffffff",          # Pure white (Cards/Chat bubbles)
            "sidebar_bg": "#091e42",        # Dark blue sidebar (Classic Enterprise look)
            "text_primary": "#172b4d",      # Dark navy text (easier on eyes than black)
            "text_secondary": "#5e6c84",    # Grey for secondary text
            "border_color": "#dfe1e6",      # Light grey borders
            "accent_primary": "#0052cc",    # Enterprise blue for actions
            "input_bg": "#ffffff",          # White input boxes
            "table_header_bg": "#f4f5f7",   # Light grey for table headers
            "table_border": "#dfe1e6",      # Matching light border
            "button_bg": "#ffffff"          # White button background
        }

    # --- CSS INJECTION ---
    # We use st.markdown with unsafe_allow_html=True to write raw <style> tags.
    # This overrides Streamlit's default styling.
    st.markdown(f"""
    <style>
        /* Import professional fonts: Inter (UI) and JetBrains Mono (Code/Technical) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

        /* --- DYNAMIC CSS VARIABLES --- */
        /* We map the Python dictionary values to CSS variables (--var-name).
           This allows us to use these colors anywhere in the CSS below. */
        :root {{
            --bg-main: {colors['bg_main']};
            --bg-panel: {colors['bg_panel']};
            --sidebar-bg: {colors['sidebar_bg']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border_color']};
            --accent: {colors['accent_primary']};
            --input-bg: {colors['input_bg']};
            --table-header-bg: {colors['table_header_bg']};
            --table-border: {colors['table_border']};
            --button-bg: {colors['button_bg']};
        }}

        /* --- GLOBAL APP STYLES --- */
        .stApp {{
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }}
        
        /* --- SIDEBAR STYLING --- */
        section[data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg);
        }}
        /* Force all sidebar text to be light grey.
           This is necessary because standard Streamlit might try to use dark text
           if the system theme is Light, which would be invisible on our dark sidebar. */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] .stMarkdown {{
            color: #c9d1d9 !important; 
        }}

        /* --- TYPOGRAPHY (HEADERS) --- */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
        }}
        /* Main Title (DiagnostiQ) - Big and Bold */
        h1 {{
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-transform: uppercase;
            text-align: center;
        }}
        /* Subtitle - Monospace and Technical */
        h3 {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
        }}

        /* --- BUTTONS --- */
        /* Standard Buttons: Override Streamlit defaults to match our theme */
        div.stButton > button, div.stDownloadButton > button {{
            background-color: var(--button-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
        }}
        /* Hover Effect: Glow with the accent color */
        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }}
        /* Primary Buttons (like 'New Inspection'): Solid accent color */
        button[kind="primary"] {{
            background-color: var(--accent) !important;
            color: white !important;
            border: none !important;
        }}

        /* --- UI PANELS --- */
        /* File Uploader Box: Add a dashed border and background color */
        div[data-testid="stFileUploader"] {{
            background-color: var(--bg-panel);
            border: 2px dashed var(--accent);
            border-radius: 8px;
            padding: 30px;
        }}
        
        /* Chat Input Field: Custom background color */
        .stChatInputContainer textarea {{
            background-color: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
        }}
        
        /* Chat Message Bubbles: Custom background and border */
        div[data-testid="stChatMessage"] {{
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
        }}
        /* Ensure text inside chat bubbles is readable */
        div[data-testid="stChatMessage"] p {{
            color: var(--text-primary) !important;
        }}
        div[data-testid="stMarkdownContainer"] p {{
            color: var(--text-primary) !important;
        }}
        div[data-testid="stMarkdownContainer"] li {{
            color: var(--text-primary) !important;
        }}
        div[data-testid="stMarkdownContainer"] strong {{
            color: var(--text-primary) !important;
            font-weight: 700;
        }}

        /* --- TABLES (MARKDOWN) --- */
        /* These rules fix the visibility of tables in Dark Mode.
           By default, Streamlit tables might have transparent backgrounds 
           that make white text hard to read on light backgrounds or vice versa. */
        div[data-testid="stMarkdownContainer"] table {{
            color: var(--text-primary) !important;
            border-color: var(--table-border) !important;
            width: 100%;
        }}
        div[data-testid="stMarkdownContainer"] th {{
            background-color: var(--table-header-bg) !important;
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--table-border) !important;
            font-weight: 600;
        }}
        div[data-testid="stMarkdownContainer"] td {{
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--table-border) !important;
        }}
        div[data-testid="stMarkdownContainer"] tr {{
            background-color: transparent !important;
        }}

        /* --- METRICS PILLS --- */
        /* The small tags (Tokens, Latency) under the AI response.
           We style them to look like technical badges. */
        .tech-pill {{
            background: var(--bg-main);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            display: inline-block;
            margin-right: 8px;
        }}
    </style>
    """, unsafe_allow_html=True) 

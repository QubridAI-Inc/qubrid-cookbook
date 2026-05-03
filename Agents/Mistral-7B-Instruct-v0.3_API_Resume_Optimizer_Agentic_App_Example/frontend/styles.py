"""Theme styling for Resume-Optimizer-AI."""

LIGHT_THEME_CSS = """
<style>
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --bg-elevated: #f3f4f6;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --accent-purple: #8B5CF6;
        --accent-pink: #EC4899;
        --border-color: #e5e7eb;
    }
    
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-right: 1px solid var(--border-color);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(139, 92, 246, 0.4);
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-pink) 100%) !important;
    }
    
    .stProgress > div > div {
        background-color: var(--bg-elevated) !important;
        border-radius: 10px !important;
    }
    
    .streamlit-expanderHeader {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    
    h1 {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
"""

DARK_THEME_CSS = """
<style>
    :root {
        --bg-primary: #1a1a2e;
        --bg-secondary: #252538;
        --bg-elevated: #2d2d44;
        --text-primary: #e0e0e0;
        --text-secondary: #b0b0b0;
        --accent-purple: #8B5CF6;
        --accent-pink: #EC4899;
        --border-color: #3d3d5c;
    }
    
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    header, [data-testid="stHeader"] {
        background-color: var(--bg-primary) !important;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-right: 1px solid var(--border-color);
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    .stFileUploader {
        background-color: transparent;
    }
    
    [data-testid="stFileUploadDropzone"] {
        background-color: var(--bg-elevated);
        border: 2px dashed var(--border-color);
    }
    
    details {
        background-color: transparent !important;
    }
    
    summary {
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    .streamlit-expanderHeader p {
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(139, 92, 246, 0.4);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    h1 {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stDownloadButton > button {
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--accent-purple) !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown div {
        color: var(--text-primary) !important;
    }
    
    code {
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    pre {
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
    }
    
    a {
        color: var(--accent-purple) !important;
    }
</style>
"""


def get_theme_css(theme: str = "light") -> str:
    """Get CSS for the specified theme."""
    return DARK_THEME_CSS if theme == "dark" else LIGHT_THEME_CSS
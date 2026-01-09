"""
Dynamic CSS Manager for Light/Dark Themes
"""

def get_custom_css(theme_mode):
    # Define Color Palettes
    if theme_mode == "Dark":
        vars = {
            # Base Colors
            "bg_app": "#0f172a",          # Deep Blue/Slate
            "bg_sidebar": "#1e293b",
            "text_main": "#ffffff",       # Pure White
            "text_sec": "#cbd5e1",        # Slate 300
            
            # Cards
            "card_bg": "#1e293b",         # Dark Slate
            "card_border": "#334155",     # Slate 700
            
            # Nutrition Bar Specifics
            "macro_bg": "#020617",        # Almost Black
            "macro_text": "#ffffff",      # White
            "macro_subtext": "#94a3b8",   # Gray
            
            # Chat & Inputs
            "hero_grad": "linear-gradient(135deg, #4c1d95 0%, #6d28d9 100%)",
            "chat_user": "#334155",
            "chat_ai": "linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%)",
            
            # DARK MODE INPUT SPECIFICS (Frosted Glass)
            "input_bg": "rgba(30, 41, 59, 0.85)",  # Semi-transparent Dark
            "input_text": "#ffffff",
            "input_border": "rgba(71, 85, 105, 0.5)",
            "placeholder": "#94a3b8"
        }
    else:
        vars = {
            # Base Colors
            "bg_app": "#f8fafc",          # Slate 50
            "bg_sidebar": "#ffffff",      # White
            "text_main": "#0f172a",       # Slate 900
            "text_sec": "#475569",        # Slate 600
            
            # Cards
            "card_bg": "#ffffff",
            "card_border": "#e2e8f0",
            
            # Nutrition Bar Specifics
            "macro_bg": "#f1f5f9",        # Light Gray
            "macro_text": "#0f172a",      # Dark Slate
            "macro_subtext": "#64748b",   # Slate 500
            
            # Chat & Inputs
            "hero_grad": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
            "chat_user": "#f1f5f9",
            "chat_ai": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
            
            # LIGHT MODE INPUT SPECIFICS (Frosted Glass)
            "input_bg": "rgba(255, 255, 255, 0.85)", # Semi-transparent White
            "input_text": "#0f172a",
            "input_border": "rgba(226, 232, 240, 0.8)",
            "placeholder": "#64748b"
        }

    return f"""
    <style>
        /* 1. GLOBAL SETTINGS */
        .stApp {{
            background-color: {vars['bg_app']} !important;
        }}
        
        h1, h2, h3, h4, h5, h6, strong {{ color: {vars['text_main']} !important; }}
        p, li, span {{ color: {vars['text_sec']}; }}
        
        /* 2. SIDEBAR */
        section[data-testid="stSidebar"] {{
            background-color: {vars['bg_sidebar']} !important;
            border-right: 1px solid {vars['card_border']};
        }}
        section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {{
            color: {vars['text_main']} !important;
        }}

        /* --- NEW SECTION: TOP HEADER STYLING --- */
        header[data-testid="stHeader"] {{
            background-color: {vars['bg_app']} !important;
            border-bottom: 1px solid {vars['card_border']} !important;
        }}
        /* Ensure icons/text in header contrast correctly */
        header[data-testid="stHeader"] * {{
             color: {vars['text_main']} !important;
        }}

        /* 3. HERO & CARDS */
        .hero-container {{
            background: {vars['hero_grad']};
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            margin-bottom: 2rem;
            color: white !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .hero-title {{ font-size: 3rem; font-weight: 800; color: white !important; }}
        .hero-subtitle {{ color: rgba(255,255,255,0.9) !important; }}
        
        .glass-card {{
            background-color: {vars['card_bg']} !important;
            border: 1px solid {vars['card_border']};
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }}
        
        .dish-title-card {{
            background-color: {vars['card_bg']} !important;
            border: 1px solid {vars['card_border']};
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .dish-name {{
            color: {vars['text_main']} !important;
            font-size: 2.2rem;
            font-weight: 800;
        }}

        /* 4. MACRO ROW */
        .macro-container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            background-color: {vars['macro_bg']} !important;
            border-radius: 12px;
            padding: 1.2rem;
            margin-top: 0.5rem;
            border: 1px solid {vars['card_border']};
        }}
        .macro-value {{
            display: block;
            font-size: 1.3rem;
            font-weight: 800;
            color: {vars['macro_text']} !important;
            margin-top: 4px;
        }}
        .macro-label {{
            font-size: 0.85rem;
            color: {vars['macro_subtext']} !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .macro-divider {{
            width: 1px;
            height: 40px;
            background-color: {vars['card_border']};
            opacity: 0.5;
        }}

        /* 5. CHAT MESSAGES */
        .chat-message-ai {{
            background: {vars['chat_ai']};
            color: white !important;
            padding: 1.5rem;
            border-radius: 4px 20px 20px 20px;
            margin: 1rem auto 1rem 0;
            max-width: 85%;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .chat-message-ai p, .chat-message-ai li, .chat-message-ai strong {{ color: white !important; }}
        
        .chat-message-user {{
            background: {vars['chat_user']};
            color: {vars['text_main']};
            padding: 1rem 1.5rem;
            border-radius: 20px 20px 0 20px;
            margin: 1rem 0 1rem auto;
            max-width: 80%;
            border: 1px solid {vars['card_border']};
        }}

        /* 6. EXPANDER */
        div[data-testid="stExpander"] details summary {{
            background: {vars['hero_grad']} !important;
            color: white !important;
            border-radius: 12px;
            padding: 1rem;
            font-weight: 600;
        }}
        div[data-testid="stExpander"] {{
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }}
        div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
            background: {vars['card_bg']};
            border: 1px solid {vars['card_border']};
            border-radius: 0 0 12px 12px;
            padding: 1.5rem;
        }}

        /* ============================================================
           7. THE GEMINI FIX (Scroll Behind + Frosted Glass)
           ============================================================ */
        
        /* Remove the background from the bottom container */
        .stBottom, 
        div[data-testid="stBottom"], 
        .stChatFloatingInputContainer,
        div[data-testid="stChatFloatingInputContainer"] {{
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* The Wrapper: Invisible, but positioned */
        div[data-testid="stChatInput"] {{
            background-color: transparent !important;
            position: fixed !important;
            bottom: 40px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 99999 !important;
            width: 60% !important;
            min-width: 400px !important;
            max-width: 800px !important;
        }}

        /* The Pill: Semi-transparent + Blur */
        div[data-testid="stChatInput"] > div {{
            background-color: {vars['input_bg']} !important; /* Semi-transparent */
            backdrop-filter: blur(12px); /* FROSTED GLASS EFFECT */
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {vars['input_border']} !important;
            border-radius: 40px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
            padding: 5px 10px !important;
        }}
        
        div[data-testid="stChatInput"] textarea {{
            background: transparent !important;
            color: {vars['input_text']} !important;
            caret-color: {vars['input_text']} !important;
        }}

        div[data-testid="stChatInput"] textarea::placeholder {{
            color: {vars['placeholder']} !important;
        }}
        
        div[data-testid="stChatInput"] button {{
            background: {vars['hero_grad']} !important;
            border: none !important;
            color: white !important;
            border-radius: 50%;
        }}
        
        /* Hide Footer only (removed header hide) */
        footer {{ display: none !important; }}
        
        /* THE KEY FIX: Reduce padding so content scrolls BEHIND the input */
        .main .block-container {{
            padding-bottom: 2rem !important;
        }}
    </style>
    """

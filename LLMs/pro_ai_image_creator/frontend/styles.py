def get_css():
    """
    Returns the 'Qubrid Dark Glass' CSS with Force-Dark UI Normalization.
    """
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .stApp {
            background: radial-gradient(circle at 50% 10%, #1a103c 0%, #050505 60%, #000000 100%);
            background-attachment: fixed;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        /* --- PILL INPUT & FLOATING BUTTON --- */
        .stTextInput {
            position: relative;
            display: flex;
            align-items: center;
        }

        .stTextInput input {
            width: 100% !important;
            height: 54px !important;
            border-radius: 27px !important; /* Perfect Pill (Height/2) */
            padding: 0 60px 0 25px !important; /* Padding for internal button */
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            font-size: 1rem !important;
            -webkit-text-fill-color: white !important;
        }

        /* The circular send icon inside the input */
        .stTextInput::after {
            content: "➤";
            position: absolute;
            right: 7px;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1rem;
            pointer-events: none; /* Let clicks hit the underlying Enter action */
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }

        /* Sidebar Visibility Fix for Manager */
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: white !important;
            opacity: 1 !important;
        }

        /* --- REST OF THE STYLES --- */
        header[data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stSidebar"] { background-color: rgba(5, 5, 10, 0.6) !important; backdrop-filter: blur(20px); }
        .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; overflow: hidden; transition: transform 0.3s ease; }
        .hero-title { font-size: 5rem; font-weight: 900; color: #FFFFFF !important; line-height: 1.1; margin-bottom: 2rem; }
        .user-msg { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; margin-bottom: 20px; display: flex; gap: 15px; }
        
        [data-testid="InputInstructions"], .stTextInput label { display: none !important; }
        footer, #MainMenu { display: none !important; }
    </style>
    """
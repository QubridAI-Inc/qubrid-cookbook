"""
frontend/styles.py

Burnt Sienna Premium CSS palette and global Streamlit style injection
for NewsletterAgent. Rebuilt from the ground up for maximum aesthetic appeal.
"""

SUMMER_BREEZE_CSS = """
<style>
/* ── Global Reset & Base ──────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.stApp {
    background-color: #F5F5DC;
}
[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* ── Typography & Headers ────────────────────────────────────────────── */
.app-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    animation: fadeInDown 0.6s ease-out;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Text Input Styling ──────────────────────────────────────────────── */
.stTextInput input {
    border-radius: 10px !important;
    border: 2px solid #EAE0C8 !important;
    padding: 0.85rem 1.25rem !important;
    font-size: 1.05rem !important;
    background: #FAFAF7 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    color: #333333 !important;
}
.stTextInput input:focus {
    border-color: #E35336 !important;
    box-shadow: 0 0 0 4px rgba(227, 83, 54, 0.15) !important;
    background: #FFFFFF !important;
}

/* ── Radio Buttons & Labels ──────────────────────────────────────────── */
.stRadio label {
    font-weight: 600 !important;
    color: #4A4A4A !important;
    font-size: 0.95rem !important;
}
div[role="radiogroup"] > label {
    background: #FAFAF7;
    border: 1px solid #EAE0C8;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin-right: 0.5rem;
    transition: all 0.2s;
    cursor: pointer;
}
div[role="radiogroup"] > label:hover {
    border-color: #F4A460;
    background: #FFFFFF;
}

/* ── Connection Badges ───────────────────────────────────────────────── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.2rem;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 600;
    margin: 0 0.4rem;
    transition: all 0.3s ease;
}
.status-connected {
    background: #FFFFFF;
    color: #2E7D32;
    border: 1px solid rgba(46, 125, 50, 0.2);
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.status-disconnected {
    background: #FFF5F4;
    color: #E35336;
    border: 1px solid rgba(227, 83, 54, 0.2);
}

/* ── CTA Buttons (Generate & Send) ───────────────────────────────────── */
button[kind="primary"] {
    background: linear-gradient(135deg, #E35336 0%, #F4A460 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.75rem 0 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 20px rgba(227, 83, 54, 0.25) !important;
    text-transform: uppercase;
}
button[kind="primary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(227, 83, 54, 0.4) !important;
    background: linear-gradient(135deg, #D44326 0%, #E39450 100%) !important;
}
button[kind="primary"]:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(227, 83, 54, 0.2) !important;
}
button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #4A4A4A !important;
    border: 1.5px solid #EAE0C8 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.72rem 0 !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
button[kind="secondary"]:hover {
    border-color: #E35336 !important;
    color: #E35336 !important;
    box-shadow: 0 4px 12px rgba(227, 83, 54, 0.1) !important;
    transform: translateY(-1px) !important;
}
/* tighten column gaps */
[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
}

/* ── Chat Messages & Agents ──────────────────────────────────────────── */
.chat-agent {
    background: #FFFFFF;
    color: #333333;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    border-left: 4px solid #F4A460;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
.chat-system {
    background: rgba(234, 224, 200, 0.5);
    color: #8C6A5A;
    border-radius: 999px;
    padding: 0.4rem 1.2rem;
    margin: 0.8rem auto;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
    display: inline-block;
}
.agent-badge {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: #FFF5F4;
    color: #E35336;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    margin-right: 0.5rem;
    font-weight: 700;
}

/* ── Stepper UI ──────────────────────────────────────────────────────── */
.stepper-container {
    display: flex;
    align-items: center;
    justify-content: center;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    border: 1px solid #EAE0C8;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    z-index: 2;
}
.step-dot {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}
.step-dot.done {
    background: #2E7D32;
    color: white;
    box-shadow: 0 0 0 4px rgba(46, 125, 50, 0.1);
}
.step-dot.running {
    background: #F4A460;
    color: white;
    box-shadow: 0 0 0 4px rgba(244, 164, 96, 0.2);
    animation: pulse-orange 1.5s infinite;
}
.step-dot.waiting {
    background: #FAFAF7;
    color: #8C6A5A;
    border: 2px solid #EAE0C8;
}
.step-dot.error {
    background: #E35336;
    color: white;
}
@keyframes pulse-orange {
    0% { box-shadow: 0 0 0 0 rgba(244, 164, 96, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(244, 164, 96, 0); }
    100% { box-shadow: 0 0 0 0 rgba(244, 164, 96, 0); }
}
.step-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #4A4A4A;
    text-align: center;
    white-space: nowrap;
}
.step-connector {
    flex: 1;
    height: 3px;
    background: #EAE0C8;
    margin: 0 10px;
    position: relative;
    top: -10px;
}
.step-connector.done {
    background: #2E7D32;
}
.step-connector.running {
    background: linear-gradient(90deg, #2E7D32 0%, #F4A460 100%);
}

/* ── Preview Box & Extras ────────────────────────────────────────────── */
.preview-box {
    border: 1px solid rgba(227, 83, 54, 0.2);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.05);
    background: #FFFFFF;
    margin-top: 1rem;
}

/* ── Sidebar & Stats & History ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #EAE0C8 !important;
}
.stats-card {
    background: #E6D8C4;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}
.stats-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #5C5C5C;
    padding: 0.3rem 0;
}
.stats-value {
    font-weight: 800;
    color: #1A1A1A;
}
.history-card {
    background: #FFFFFF;
    border-left: 5px solid #E35336;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    transition: transform 0.2s ease;
}
.history-card:hover {
    transform: translateX(4px);
}
.history-topic {
    background: #FFF5F4;
    color: #E35336;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}
.history-summary {
    font-size: 0.85rem;
    color: #4A4A4A;
    line-height: 1.5;
    margin-bottom: 0.5rem;
}
.history-meta {
    display: flex;
    gap: 0.8rem;
    align-items: center;
    font-size: 0.75rem;
    color: #888888;
}
.status-pill {
    border-radius: 999px;
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    font-weight: 700;
}
.status-complete { background: #E8F5E9; color: #2E7D32; }
.status-running  { background: #EAE0C8; color: #8C6A5A; }
.status-failed   { background: #FFEBEE; color: #C62828; }

/* ── Newsletter Preview Extras ───────────────────────────────────────── */
.preview-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
}
.preview-title {
    font-size: 1.2rem;
    font-weight: 800;
    color: #1A1A1A;
}
.topic-badge {
    background: linear-gradient(135deg, #E35336 0%, #F4A460 100%);
    color: #FFFFFF;
    border-radius: 6px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(227, 83, 54, 0.2);
}
.app-footer {
    text-align: center;
    padding: 2rem 0 1rem;
    font-size: 0.8rem;
    color: #9E9E9E;
}

</style>
"""

def inject_styles() -> str:
    """Return the full CSS block to be rendered via st.markdown."""
    return SUMMER_BREEZE_CSS

"""
Custom CSS for ToneCraft AI — Stormy Morning colour palette (vibrant pastel revision).

Palette:
  #38bdf8  Sky blue         — primary accent, buttons
  #7dd3fc  Light sky        — highlights, hover
  #a5f3fc  Pale cyan        — badges, pills
  #c4b5fd  Lavender         — academic accent
  #6ee7b7  Mint green       — casual accent
  #f9a8d4  Blush pink       — persuasive accent
  #0f172a  Deep navy        — page background
  #1e293b  Slate            — card background
"""

import streamlit as st


TONE_COLORS: dict[str, str] = {
    "🎯 Executive": "#38bdf8",
    "💬 Casual":    "#6ee7b7",
    "🎤 Persuasive":"#f9a8d4",
    "🎓 Academic":  "#c4b5fd",
    "📣 Marketing": "#fdba74",
    "🤝 Diplomatic":"#a5f3fc",
}


def get_custom_css() -> str:
    """Return the full custom CSS string for the Stormy Morning theme."""
    return """
<style>
/* ── Google Font ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* ── Page background ─────────────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(160deg, #e8f4fd 0%, #f0f9ff 55%, #dbeafe 100%);
    color: #1e293b;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #dbeafe 0%, #e0f2fe 100%) !important;
    border-right: 1px solid rgba(56, 189, 248, 0.3) !important;
}
[data-testid="stSidebar"] * { color: #1e293b !important; }

/* ── Header — no box, pure centered text ─────────────────────────────────── */
.tc-header {
    text-align: center;
    padding: 3rem 2rem 1rem 2rem;
    background: transparent;
}

.tc-app-name {
    font-size: 4rem;
    font-weight: 900;
    margin: 0 0 0.5rem 0;
    line-height: 1.1;
    color: #0284c7;
    letter-spacing: -1.5px;
    display: block;
}

.tc-tagline {
    font-size: 1.4rem;
    color: #0369a1;
    margin: 0 0 1rem 0;
    font-weight: 700;
    letter-spacing: 0.1px;
    display: block;
}

.tc-subtitle {
    font-size: 1.05rem;
    color: #475569;
    margin: 0 auto 0.6rem auto;
    max-width: 640px;
    line-height: 1.7;
    font-weight: 400;
    display: block;
    text-align: center;
}

.tc-subtitle-accent {
    display: block;
    margin-top: 5px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    color: #0ea5e9;
    text-align: center;
}

.tc-brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 24px;
    padding: 5px 16px;
    font-size: 0.8rem;
    color: #7dd3fc;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.tc-pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #38bdf8;
    display: inline-block;
    animation: pulse 2s infinite;
    flex-shrink: 0;
}

@keyframes pulse {
    0%, 100% { opacity: 1;   transform: scale(1);   box-shadow: 0 0 0 0 rgba(56,189,248,0.4); }
    50%       { opacity: 0.7; transform: scale(1.2); box-shadow: 0 0 0 4px rgba(56,189,248,0); }
}

.tc-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(56,189,248,0.4) 50%, transparent 100%);
    margin: 1.5rem auto;
    border: none;
    max-width: 600px;
}

/* ── Tone selector ───────────────────────────────────────────────────────── */
.tc-tone-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.75rem;
}

.tc-tone-card {
    background: rgba(255, 255, 255, 0.75);
    border: 1.5px solid rgba(56, 189, 248, 0.22);
    border-radius: 12px;
    padding: 1rem 1.1rem 0.8rem 1.1rem;
    margin-bottom: 0.4rem;
    transition: all 0.2s ease;
    min-height: 76px;
    box-shadow: 0 1px 4px rgba(56, 189, 248, 0.08);
}

.tc-tone-card:hover {
    border-color: rgba(56, 189, 248, 0.5);
    background: rgba(255, 255, 255, 0.95);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
}

.tc-tone-card.exec    { border-top: 3px solid #38bdf8; }
.tc-tone-card.casual  { border-top: 3px solid #6ee7b7; }
.tc-tone-card.persu   { border-top: 3px solid #f9a8d4; }
.tc-tone-card.acad    { border-top: 3px solid #c4b5fd; }
.tc-tone-card.mktg    { border-top: 3px solid #fdba74; }
.tc-tone-card.diplo   { border-top: 3px solid #a5f3fc; }

.tc-tone-card.selected {
    background: rgba(56, 189, 248, 0.1);
    box-shadow: 0 0 0 1.5px #38bdf8, 0 4px 20px rgba(56, 189, 248, 0.18);
}

.tc-tone-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0f172a;
}

.tc-tone-desc {
    font-size: 0.73rem;
    color: #64748b;
    margin-top: 3px;
    line-height: 1.45;
}

/* ── Text comparison panels ──────────────────────────────────────────────── */
.tc-panel {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 12px;
    padding: 1.2rem 1.3rem;
    min-height: 160px;
    font-size: 0.92rem;
    line-height: 1.7;
    color: #1e293b;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 1px 6px rgba(56, 189, 248, 0.08);
}

.tc-panel-rewritten {
    border-left: 3px solid #38bdf8;
    background: rgba(219, 234, 254, 0.4);
}

.tc-panel-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b;
    margin-bottom: 0.6rem;
}

.tc-arrow-center {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    font-size: 1.5rem;
    padding-top: 3rem;
    background: linear-gradient(135deg, #38bdf8, #a5f3fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Diff pills ──────────────────────────────────────────────────────────── */
.tc-pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 1.1rem 0;
}

.tc-pill {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.45);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #1e3a5f;
    font-weight: 600;
    white-space: nowrap;
}

/* ── Explanation card ────────────────────────────────────────────────────── */
.tc-explanation-card {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-left: 4px solid #38bdf8;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #334155;
    box-shadow: 0 1px 6px rgba(56, 189, 248, 0.08);
}

.tc-explanation-header {
    font-size: 0.72rem;
    font-weight: 700;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 0.7rem;
}

/* ── Section titles ──────────────────────────────────────────────────────── */
.tc-section-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #64748b;
    margin: 1.6rem 0 0.7rem 0;
}

/* ── Sidebar — stats card ────────────────────────────────────────────────── */
.tc-stats-card {
    background: rgba(255, 255, 255, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    line-height: 1.9;
    color: #1e293b;
    box-shadow: 0 1px 6px rgba(56, 189, 248, 0.1);
}

/* ── Sidebar — history cards ─────────────────────────────────────────────── */
.tc-history-card {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    margin-bottom: 0.45rem;
    transition: border-color 0.15s;
}
.tc-history-card:hover {
    border-color: rgba(56, 189, 248, 0.45);
    background: rgba(255, 255, 255, 0.9);
}

.tc-history-tone-badge {
    display: inline-block;
    border-radius: 10px;
    padding: 1px 9px;
    font-size: 0.68rem;
    font-weight: 600;
    margin-bottom: 4px;
    color: #0f172a;
    background: rgba(56, 189, 248, 0.12);
}

.tc-history-snippet {
    font-size: 0.77rem;
    color: #475569;
    line-height: 1.45;
}

.tc-history-time {
    font-size: 0.67rem;
    color: #94a3b8;
    margin-top: 3px;
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.tc-footer {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
    font-size: 0.74rem;
    color: #94a3b8;
    border-top: 1px solid rgba(56, 189, 248, 0.2);
    margin-top: 3rem;
}

/* ── Streamlit widget overrides ──────────────────────────────────────────── */
/* Text area */
.stTextArea textarea {
    background-color: rgba(255, 255, 255, 0.85) !important;
    color: #1e293b !important;
    border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    line-height: 1.65 !important;
    caret-color: #0ea5e9;
}
.stTextArea textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15) !important;
}
.stTextArea textarea::placeholder { color: #94a3b8 !important; }

/* Buttons */
.stButton > button {
    background: rgba(255, 255, 255, 0.75) !important;
    color: #0369a1 !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    padding: 0.45rem 1rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
    color: #ffffff !important;
    border-color: #38bdf8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35) !important;
}

/* Primary (rewrite) button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%) !important;
    color: #0f172a !important;
    border: none !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 20px rgba(56, 189, 248, 0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #38bdf8 0%, #7dd3fc 100%) !important;
    box-shadow: 0 6px 24px rgba(56, 189, 248, 0.4) !important;
    transform: translateY(-2px) !important;
    color: #0f172a !important;
}

/* Download button */
.stDownloadButton > button {
    background: rgba(110, 231, 183, 0.08) !important;
    color: #6ee7b7 !important;
    border: 1px solid rgba(110, 231, 183, 0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: rgba(110, 231, 183, 0.18) !important;
    border-color: #6ee7b7 !important;
    color: #6ee7b7 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.5) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(56, 189, 248, 0.12) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
.streamlit-expanderContent {
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(56, 189, 248, 0.1) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 0.5rem !important;
}

/* Alerts */
.stAlert { border-radius: 10px !important; }

/* Spinner */
.stSpinner > div { border-top-color: #38bdf8 !important; }

/* Code block */
.stCode code {
    background: rgba(15, 23, 42, 0.9) !important;
    color: #a5f3fc !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* Character counter */
.tc-char-ok     { color: #334155; font-size: 0.75rem; text-align: right; margin-top: 2px; }
.tc-char-amber  { color: #fbbf24; font-size: 0.75rem; text-align: right; margin-top: 2px; font-weight: 600; }
.tc-char-red    { color: #f87171; font-size: 0.75rem; text-align: right; margin-top: 2px; font-weight: 700; }

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Agent pipeline tracker ──────────────────────────────────────────────── */
.tc-pipeline {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    margin: 0.8rem 0 1.2rem 0;
    padding: 0.9rem 1.2rem;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 14px;
}
.tc-pipeline-arrow {
    color: #94a3b8;
    font-size: 1rem;
    padding: 0 2px;
    flex-shrink: 0;
}
.tc-agent-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 7px 12px;
    border-radius: 10px;
    min-width: 84px;
    text-align: center;
    transition: background 0.25s, border-color 0.25s, box-shadow 0.25s;
}
.tc-agent-node.pending {
    background: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.2);
}
.tc-agent-node.active {
    background: rgba(14, 165, 233, 0.1);
    border: 1.5px solid #38bdf8;
    animation: pipeline-pulse 1.6s ease-in-out infinite;
}
.tc-agent-node.done {
    background: rgba(110, 231, 183, 0.1);
    border: 1px solid rgba(110, 231, 183, 0.4);
}
.tc-agent-node.skipped {
    background: rgba(148, 163, 184, 0.05);
    border: 1px dashed rgba(148, 163, 184, 0.18);
    opacity: 0.45;
}
@keyframes pipeline-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.35); }
    50%       { box-shadow: 0 0 0 7px rgba(56, 189, 248, 0); }
}
.tc-agent-icon  { font-size: 1.25rem; }
.tc-agent-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.2px; }
.tc-agent-status { font-size: 0.68rem; font-weight: 700; margin-top: 1px; }

.tc-agent-node.pending .tc-agent-label  { color: #94a3b8; }
.tc-agent-node.active  .tc-agent-label  { color: #0369a1; }
.tc-agent-node.done    .tc-agent-label  { color: #065f46; }
.tc-agent-node.skipped .tc-agent-label  { color: #94a3b8; }

.tc-agent-node.pending  .tc-agent-status { color: #cbd5e1; }
.tc-agent-node.done     .tc-agent-status { color: #6ee7b7; }
.tc-agent-node.skipped  .tc-agent-status { color: #cbd5e1; }
.tc-agent-node.active   .tc-agent-status { color: #38bdf8; }

.tc-agent-spinner {
    display: inline-block;
    width: 9px; height: 9px;
    border: 2px solid rgba(56, 189, 248, 0.25);
    border-top-color: #38bdf8;
    border-radius: 50%;
    animation: node-spin 0.75s linear infinite;
}
@keyframes node-spin { to { transform: rotate(360deg); } }

/* ── Live streaming panel ────────────────────────────────────────────────── */
.tc-streaming {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-left: 4px solid #38bdf8;
    border-radius: 12px;
    padding: 1rem 1.3rem;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #1e293b;
    margin: 0.5rem 0;
    min-height: 60px;
    white-space: pre-wrap;
}
.tc-streaming-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #38bdf8;
    margin-bottom: 0.5rem;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.tc-cursor { display: inline-block; animation: blink 0.8s infinite; color: #38bdf8; font-weight: 700; }

/* ── Quality breakdown card ──────────────────────────────────────────────── */
.tc-quality-bar-bg {
    background: rgba(56, 189, 248, 0.1);
    border-radius: 20px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin: 6px 0 2px 0;
}
.tc-quality-bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 0.6s ease;
}

/* ── Agent metadata badges ───────────────────────────────────────────────── */
.tc-meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin: 0.6rem 0 1rem 0;
}
.tc-meta-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem;
    font-weight: 600;
    color: #1e3a5f;
    white-space: nowrap;
}
.tc-meta-badge.quality-high  { border-color: rgba(110, 231, 183, 0.5); color: #065f46; background: rgba(110, 231, 183, 0.12); }
.tc-meta-badge.quality-mid   { border-color: rgba(251, 191, 36, 0.5);  color: #78350f; background: rgba(251, 191, 36, 0.10); }
.tc-meta-badge.quality-low   { border-color: rgba(248, 113, 113, 0.5); color: #7f1d1d; background: rgba(248, 113, 113, 0.10); }
.tc-meta-badge.refined       { border-color: rgba(167, 139, 250, 0.5); color: #4c1d95; background: rgba(167, 139, 250, 0.10); }

/* ── Tone recommendations ────────────────────────────────────────────────── */
.tc-recommendations {
    background: rgba(255, 255, 255, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-left: 4px solid #0ea5e9;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.86rem;
    color: #1e293b;
}
.tc-recommendations-header {
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #0ea5e9;
    margin-bottom: 0.5rem;
}
.tc-rec-item {
    margin-bottom: 0.35rem;
    line-height: 1.5;
}
.tc-rec-tone {
    font-weight: 700;
    color: #0369a1;
}

/* ── Chat panel ──────────────────────────────────────────────────────────── */
.tc-chat-history {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 1rem;
    max-height: 320px;
    overflow-y: auto;
    padding: 0.5rem 0;
}
.tc-chat-user {
    align-self: flex-end;
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.3);
    border-radius: 14px 14px 4px 14px;
    padding: 0.6rem 1rem;
    font-size: 0.88rem;
    color: #0c4a6e;
    max-width: 80%;
    line-height: 1.5;
}
.tc-chat-assistant {
    align-self: flex-start;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px 14px 14px 4px;
    padding: 0.6rem 1rem;
    font-size: 0.88rem;
    color: #334155;
    max-width: 80%;
    line-height: 1.5;
}

/* Text input inside chat */
.stTextInput input {
    background: rgba(255, 255, 255, 0.85) !important;
    color: #1e293b !important;
    border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15) !important;
}
</style>
"""


def inject_css() -> None:
    """Inject the Stormy Morning custom CSS into the Streamlit app."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)

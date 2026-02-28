import streamlit as st

def load_css():

    # Nuclear option: hide mode buttons and fix sidebar toggle via JS + inline style injection
    st.markdown("""
    <script>
    (function() {
        var MODE_LABELS = ["Upload File", "YouTube URL", "Record Live"];

        function fixButtons() {
            var doc = window.parent.document;

            // Kill white bg on ALL stButton wrappers
            doc.querySelectorAll("[data-testid=stButton]").forEach(function(w) {
                w.style.background = "transparent";
                w.style.boxShadow = "none";
                w.style.border = "none";
            });

            // Hide the 3 mode selector buttons by their exact label text
            doc.querySelectorAll("button[kind=secondary]").forEach(function(btn) {
                var t = (btn.innerText || btn.textContent || "").trim();
                if (MODE_LABELS.indexOf(t) !== -1) {
                    var wrap = btn.closest("[data-testid=stButton]");
                    if (wrap) {
                        wrap.style.cssText = "background:transparent!important;border:none!important;box-shadow:none!important;margin-top:-108px!important;height:108px!important;position:relative!important;overflow:visible!important;z-index:10!important;";
                    }
                    btn.style.cssText = "opacity:0!important;width:100%!important;height:108px!important;cursor:pointer!important;background:transparent!important;border:none!important;box-shadow:none!important;display:block!important;";
                }
            });
        }
        fixButtons();
        new MutationObserver(fixButtons).observe(window.parent.document.body, {childList:true, subtree:true});
    })();
    </script>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');


        /* ── Force hero subtitle truly centered in flex context ─────────────── */
        .hero-wrap { display: flex !important; flex-direction: column !important; align-items: center !important; }
        .hero-wrap * { text-align: center !important; }

        html, body, .stApp {
            background: radial-gradient(ellipse at 25% 20%, #0a2020 0%, #071a1a 45%, #040f0f 100%);
            font-family: 'Inter', sans-serif;
            color: #e2e8f0;
        }
        .stApp::before {
            content: ''; position: fixed; top: -10%; left: -5%;
            width: 700px; height: 700px;
            background: radial-gradient(circle, rgba(20,184,166,0.18) 0%, transparent 65%);
            border-radius: 50%; pointer-events: none; z-index: 0;
        }
        .stApp::after {
            content: ''; position: fixed; bottom: -15%; right: -5%;
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(6,182,212,0.14) 0%, transparent 65%);
            border-radius: 50%; pointer-events: none; z-index: 0;
        }
        header { visibility: hidden; }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 100%; position: relative; z-index: 1; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }

        /* ── Force ALL text white ───────────────────────────────────────────────── */
        p, span, div, label, li, td, th, .stMarkdown,
        [data-testid="stText"], [data-testid="stMarkdownContainer"] { color: #e2e8f0; }
        .stDataFrame td, .stDataFrame th { color: #e2e8f0 !important; background: transparent !important; }
        .stDataFrame thead th { color: #5eead4 !important; background: rgba(20,184,166,0.1) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.06em; }
        [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] span { color: #94a3b8 !important; }

        /* ── Sidebar ────────────────────────────────────────────────────────────── */
        /* Native sidebar hidden — we use column layout instead */
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }

        /* ── Centered Hero ──────────────────────────────────────────────────────── */
        .hero-wrap { text-align: center; padding: 52px 0 44px 0; }
        .hero-badge { display: none; }   /* moved to footer */
        .footer-badge {
            position: fixed; bottom: 18px;
            left: 0; right: 0; width: fit-content;
            margin: 0 auto;
            background: rgba(10,13,28,0.85);
            border: 1px solid rgba(20,184,166,0.2);
            color: #475569 !important; font-size: 0.68rem; font-weight: 600;
            letter-spacing: 0.1em; text-transform: uppercase;
            padding: 6px 18px; border-radius: 20px;
            backdrop-filter: blur(12px); z-index: 9999;
            white-space: nowrap; display: flex; align-items: center; gap: 7px;
        }
        .hero-title {
            font-size: 4.4rem; font-weight: 900; margin: 0 0 12px 0; line-height: 1.05;
            color: #ffffff;
            letter-spacing: -0.03em;
            text-shadow: 0 0 60px rgba(20,184,166,0.4), 0 2px 4px rgba(0,0,0,0.5);
        }
        /* Override Streamlit's h1 reset inside hero */
        .hero-wrap h1.hero-title {
            font-size: 4.4rem !important; font-weight: 900 !important;
            margin: 0 0 12px 0 !important; line-height: 1.05 !important;
            color: #ffffff !important; letter-spacing: -0.03em !important;
            text-shadow: 0 0 60px rgba(20,184,166,0.4), 0 2px 4px rgba(0,0,0,0.5);
            padding: 0 !important;
        }
        .hero-tagline {
            color: #64748b !important; font-size: 0.88rem; font-weight: 400;
            letter-spacing: 0.01em; margin: 0 0 14px 0; line-height: 1.6;
        }
        .tagline-highlight {
            color: #5eead4 !important; font-weight: 700;
            background: rgba(20,184,166,0.12);
            padding: 1px 7px; border-radius: 5px;
            border: 1px solid rgba(20,184,166,0.3);
        }
        .tagline-dim {
            color: #475569 !important; font-weight: 500;
        }
        .hero-subtitle {
            color: #64748b !important; font-size: 1rem; margin: 0 auto 4px auto;
            max-width: 560px; line-height: 1.7;
            text-align: center !important; width: 100%; display: block;
        }

        /* ── Animated Progress Bars ─────────────────────────────────────────────── */
        @keyframes flow {
            0%   { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
        }
        @keyframes flowSlow {
            0%   { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%       { opacity: 0.4; transform: scale(0.7); }
        }
        .progress-wrap {
            background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
            border-radius: 16px; padding: 28px 32px; margin: 8px 0 24px 0;
        }
        .progress-label {
            font-size: 0.8rem; font-weight: 600; color: #5eead4 !important;
            letter-spacing: 0.05em; margin-bottom: 18px;
            display: flex; align-items: center; gap: 10px;
        }
        .pulse-dot {
            width: 8px; height: 8px; background: #14b8a6; border-radius: 50%;
            animation: pulse-dot 1.2s ease-in-out infinite;
        }
        .progress-track {
            background: rgba(255,255,255,0.05); border-radius: 999px;
            height: 5px; overflow: hidden; margin-bottom: 10px; position: relative;
        }
        .progress-bar-1 {
            position: absolute; top: 0; left: 0; height: 100%; width: 35%;
            background: linear-gradient(90deg, transparent, #0d9488, #0891b2, transparent);
            border-radius: 999px;
            animation: flow 2s ease-in-out infinite;
        }
        .progress-bar-2 {
            position: absolute; top: 0; left: 0; height: 100%; width: 25%;
            background: linear-gradient(90deg, transparent, #06b6d4, #22d3ee, transparent);
            border-radius: 999px;
            animation: flow 2.8s ease-in-out infinite 0.6s;
        }
        .progress-bar-3 {
            position: absolute; top: 0; left: 0; height: 100%; width: 45%;
            background: linear-gradient(90deg, transparent, #14b8a6, #0d9488, transparent);
            border-radius: 999px;
            animation: flow 3.4s ease-in-out infinite 1.2s;
        }
        .progress-step {
            font-size: 0.75rem; color: #475569 !important; margin-top: 4px; padding-left: 2px;
        }



        /* ── Tabs ───────────────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255,255,255,0.03); border-radius: 12px;
            padding: 4px; gap: 4px; border: 1px solid rgba(255,255,255,0.06);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px; color: #64748b !important; font-weight: 500;
            font-size: 0.875rem; padding: 8px 16px; transition: all 0.2s;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(20,184,166,0.2), rgba(6,182,212,0.2)) !important;
            color: #5eead4 !important; border: 1px solid rgba(20,184,166,0.3) !important;
        }
        .stTabs [data-baseweb="tab-highlight"] { display: none; }

        /* ── Cards ──────────────────────────────────────────────────────────────── */
        .chapter-card {
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px; padding: 16px 20px; margin-bottom: 10px; transition: all 0.2s;
        }
        .chapter-card:hover { background: rgba(20,184,166,0.05); border-color: rgba(20,184,166,0.25); }
        .chapter-timestamp {
            font-family: monospace; font-size: 0.78rem; font-weight: 700; color: #2dd4bf !important;
            background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.2);
            padding: 2px 8px; border-radius: 6px; margin-right: 10px;
        }
        .chapter-title { font-weight: 600; color: #e2e8f0 !important; font-size: 0.95rem; }
        .chapter-summary { color: #64748b !important; font-size: 0.85rem; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.04); }

        .moment-card {
            background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06);
            border-left: 3px solid #14b8a6; border-radius: 12px; padding: 18px 20px; margin-bottom: 12px; transition: all 0.2s;
        }
        .moment-card:hover { background: rgba(20,184,166,0.04); border-left-color: #5eead4; }
        .moment-timestamp { font-family: monospace; font-size: 0.78rem; font-weight: 700; color: #2dd4bf !important; background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.2); padding: 2px 8px; border-radius: 6px; display: inline-block; margin-bottom: 10px; }
        .moment-quote { font-size: 0.97rem; font-style: italic; color: #99f6e4 !important; font-weight: 500; line-height: 1.55; margin-bottom: 8px; }
        .moment-reason { font-size: 0.82rem; color: #475569 !important; }

        .topic-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 16px 20px; margin-bottom: 10px; }
        .topic-name { font-weight: 600; color: #e2e8f0 !important; font-size: 0.93rem; margin-bottom: 6px; }
        .topic-chapters { font-size: 0.8rem; color: #14b8a6 !important; font-weight: 500; }

        .brief-card {
            background: linear-gradient(135deg, rgba(20,184,166,0.08), rgba(6,182,212,0.05));
            border: 1px solid rgba(20,184,166,0.2); border-radius: 14px; padding: 22px 26px; margin-bottom: 20px;
        }
        .brief-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #2dd4bf !important; margin-bottom: 10px; }
        .brief-text { color: #cbd5e1 !important; font-size: 0.97rem; line-height: 1.8; }

        .match-badge {
            display: inline-block; background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.2);
            color: #2dd4bf !important; font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 20px; margin-bottom: 12px;
        }

        /* ── Inputs / Misc ──────────────────────────────────────────────────────── */
        .stTextInput input,
        .stTextInput > div > div > input,
        [data-testid="stTextInput"] input {
            background: #0a1f1f !important;
            border: 1px solid rgba(20,184,166,0.2) !important;
            border-radius: 10px !important;
            color: #f1f5f9 !important;
            caret-color: #5eead4 !important;
            padding: 10px 14px !important;
            font-size: 0.9rem !important;
        }
        .stTextInput input::placeholder,
        [data-testid="stTextInput"] input::placeholder { color: rgba(148,163,184,0.4) !important; }
        .stTextInput input:focus,
        [data-testid="stTextInput"] input:focus {
            background: #0a1f1f !important;
            border-color: rgba(20,184,166,0.55) !important;
            box-shadow: 0 0 0 3px rgba(20,184,166,0.1) !important;
            color: #f1f5f9 !important;
            outline: none !important;
        }
        .stTextInput input::placeholder { color: #475569 !important; }

        [data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.02) !important;
            border: 2px dashed rgba(20,184,166,0.25) !important;
            border-radius: 16px !important; transition: border-color 0.2s !important;
        }
        [data-testid="stFileUploader"]:hover { border-color: rgba(20,184,166,0.5) !important; }
        /* Kill the white inner box Streamlit renders inside uploader */
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(255,255,255,0.02) !important;
            border: none !important;
        }
        [data-testid="stFileUploaderDropzone"] * { color: #64748b !important; }
        [data-testid="stFileUploaderDropzone"] button {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            color: #94a3b8 !important; border-radius: 8px !important;
        }

        .stDownloadButton > button {
            background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.1) !important;
            color: #94a3b8 !important; border-radius: 8px !important; font-weight: 500 !important; transition: all 0.2s !important;
        }
        .stDownloadButton > button:hover { background: rgba(20,184,166,0.1) !important; border-color: rgba(20,184,166,0.3) !important; color: #5eead4 !important; }

        /* ── Kill white background on ALL button wrappers ──────────────────────── */
        [data-testid="stButton"],
        [data-testid="stButton"] > div,
        [data-testid="stBaseButton-secondary"],
        .stButton { 
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
        }

        /* ── Regular sidebar/history buttons ────────────────────────────────────── */
        .stButton > button {
            background: rgba(4,15,15,0.95) !important;
            border: 1px solid rgba(20,184,166,0.08) !important;
            color: rgba(20,184,166,0.3) !important;
            border-radius: 8px !important;
            font-size: 0.75rem !important;
            text-align: left !important;
            box-shadow: none !important;
            transition: all 0.15s !important;
        }
        .stButton > button:hover {
            background: rgba(20,184,166,0.07) !important;
            border-color: rgba(20,184,166,0.2) !important;
            color: #5eead4 !important;
        }

        /* ── Mode card: card sits above, button pulled up to overlay it ─────────── */
        .mode-card {
            margin-bottom: -4px;
        }
        /* Any button immediately after a mode-card div — make it the invisible overlay */
        div:has(> .mode-card) + div button,
        div:has(> .mode-card) ~ div button {
            opacity: 0 !important;
            position: relative !important;
            z-index: 10 !important;
            margin-top: -108px !important;
            height: 108px !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            cursor: pointer !important;
            display: block !important;
        }
        div:has(> .mode-card) + div,
        div:has(> .mode-card) ~ div [data-testid="stButton"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* ── Primary buttons: teal gradient ─────────────────────────────────────── */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0d9488, #0891b2) !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 15px rgba(20,184,166,0.35) !important;
            opacity: 1 !important;
            margin-top: 0 !important;
            height: auto !important;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(20,184,166,0.5) !important;
        }

        hr { border-color: rgba(255,255,255,0.06) !important; margin: 20px 0 !important; }
        .stAlert { border-radius: 10px !important; }

        /* ── Use-case pills (hero) ───────────────────────────────────────────── */
        .hero-pills {
            display: flex; flex-wrap: wrap; gap: 8px;
            justify-content: center; margin-top: 24px;
        }
        .hero-pill {
            display: inline-block;
            background: rgba(20,184,166,0.08);
            border: 1px solid rgba(20,184,166,0.22);
            color: #5eead4 !important;
            font-size: 0.8rem; font-weight: 600;
            padding: 7px 16px; border-radius: 20px;
            letter-spacing: 0.01em;
            transition: all 0.2s;
        }
        .hero-pill:hover {
            background: rgba(20,184,166,0.18);
            border-color: rgba(20,184,166,0.45);
            color: #ccfbf1 !important;
            transform: translateY(-1px);
        }
        /* legacy */
        .use-case-pill {
            display: inline-block;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.09);
            color: #64748b !important;
            font-size: 0.75rem; font-weight: 600;
            padding: 5px 12px; border-radius: 20px;
        }

        /* ── Mode selector cards ────────────────────────────────────────────── */
        .mode-card {
            border-radius: 14px; padding: 18px 10px 14px;
            text-align: center; cursor: pointer;
            transition: all 0.2s; margin-bottom: 0;
        }
        .mode-card:hover { filter: brightness(1.15); transform: translateY(-1px); }
        .active-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: #14b8a6; margin: 8px auto 0;
        }
        /* Mode select buttons — hidden via JS after render (see load_css inject) */

        /* ── Collapse the entire button row below mode cards to zero ────────────── */
        .mode-btn-row {
            height: 0 !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
            position: absolute !important;
            top: -9999px !important;
        }

        /* ── Quote postcard cards ────────────────────────────────────────────── */
        .quote-card {
            background: linear-gradient(135deg, rgba(20,184,166,0.08), rgba(6,182,212,0.04));
            border: 1px solid rgba(20,184,166,0.2);
            border-radius: 16px;
            padding: 28px 28px 20px 28px;
            margin-bottom: 16px;
            position: relative;
            overflow: hidden;
            transition: all 0.2s;
        }
        .quote-card::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, #0d9488, #0891b2, #06b6d4);
        }
        .quote-card:hover {
            border-color: rgba(20,184,166,0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(20,184,166,0.12);
        }
        .quote-mark {
            font-size: 4rem; line-height: 0.8; color: rgba(20,184,166,0.2);
            font-family: Georgia, serif; margin-bottom: 8px; display: block;
        }
        .quote-text {
            font-size: 1.05rem; font-style: italic; color: #e2e8f0 !important;
            font-weight: 500; line-height: 1.65; margin-bottom: 16px;
        }
        .quote-footer {
            display: flex; align-items: center; gap: 12px;
            padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);
        }
        .quote-reason {
            font-size: 0.8rem; color: #475569 !important; font-style: normal;
        }

        /* ── Confidence bar ──────────────────────────────────────────────────── */
        .confidence-bar {
            display: flex; align-items: center; gap: 8px;
            padding: 10px 16px; margin-bottom: 14px;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
        }

    </style>
    """, unsafe_allow_html=True)

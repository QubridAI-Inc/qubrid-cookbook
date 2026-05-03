"""
ReVive AI — Custom CSS styles.
Design language: Mango Popsicle — light, bright, warm.

Palette (the only 4 colours used):
  #F2B949  Mango        — primary brand, buttons, active states
  #EDD377  Golden Sand  — secondary highlights, sidebar bg tint
  #F2E829  Vivid Yellow — bright accents, badges, hover glows
  #F27430  Burnt Orange — CTAs, strong accents, links

All backgrounds are light yellow tones derived from the palette.
All text is near-black derived by darkening the orange (#1A0F00).
"""

# ── Colour palette ─────────────────────────────────────────────────────────────
COLORS = {
    # backgrounds — light, airy, warm yellow
    "bg_page":        "#FFFBEF",   # very light warm yellow (almost white)
    "bg_sidebar":     "#FFF3CC",   # soft golden sand
    "card_bg":        "#FFFFFF",   # white cards
    "card_border":    "rgba(242, 185, 73, 0.45)",

    # brand palette — the 4 source colours
    "accent_gold":    "#F2B949",   # Mango         — primary
    "accent_bright":  "#F2E829",   # Vivid Yellow  — highlight
    "accent_orange":  "#F27430",   # Burnt Orange  — CTA / done
    "accent_sand":    "#EDD377",   # Golden Sand   — secondary

    "glow":           "rgba(242, 185, 73, 0.25)",

    # text — warm near-black, never pure black
    "text_primary":   "#1A0F00",   # darkened mango hue
    "text_secondary": "#F27430",   # burnt orange
    "text_muted":     "#B8720A",   # medium amber

    # semantic — all from the 4 palette colours
    "success":        "#F27430",   # orange  = approved / complete
    "warning":        "#F2B949",   # mango   = caution
    "error":          "#D94010",   # deep orange-red = failure

    # agent states
    "agent_active":   "#F2B949",   # mango pulse
    "agent_done":     "#F27430",   # orange = done
    "agent_wait":     "#EDD377",   # sand   = waiting
}


def get_css() -> str:
    """Return the complete custom CSS block for injection into Streamlit."""
    c = COLORS
    return f"""
<style>
/* ── Page & base ─────────────────────────────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {{
    background-color: {c['bg_page']} !important;
    color: {c['text_primary']};
}}
[data-testid="stSidebar"] {{
    background-color: {c['bg_sidebar']} !important;
    border-right: 2px solid {c['accent_gold']};
}}
[data-testid="stSidebar"] * {{
    color: {c['text_primary']} !important;
}}
[data-testid="stHeader"],
header[data-testid="stHeader"],
[data-testid="stHeader"] > div,
[data-testid="stToolbar"] {{
    background-color: {c['bg_page']} !important;
    border-bottom: none !important;
    box-shadow: none !important;
}}
/* Kill any dark backgrounds Streamlit injects */
section[data-testid="stSidebar"] > div:first-child {{
    background-color: {c['bg_sidebar']} !important;
}}

/* ── Typography ──────────────────────────────────────── */
h1, h2, h3, h4 {{
    color: {c['text_primary']} !important;
    font-family: 'Georgia', serif;
}}
p, li, div {{
    color: {c['text_primary']};
}}
label, .stMarkdown p {{
    color: {c['text_primary']} !important;
}}

/* ── Cards ───────────────────────────────────────────── */
.revive-card {{
    background: {c['card_bg']};
    border: 1.5px solid {c['card_border']};
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(242,185,73,0.12);
}}

/* ── Gradient title ──────────────────────────────────── */
.revive-title {{
    background: linear-gradient(135deg, {c['accent_orange']} 0%, {c['accent_gold']} 50%, {c['accent_bright']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 4rem;
    font-weight: 900;
    letter-spacing: -2px;
    font-family: 'Georgia', serif;
    line-height: 1;
}}
.revive-tagline {{
    color: {c['text_primary']};
    font-size: 1.4rem;
    font-style: italic;
    font-family: 'Georgia', serif;
    margin-top: 4px;
}}
.revive-sub-tagline {{
    color: {c['text_muted']};
    font-size: 1rem;
    margin-top: 2px;
}}
.revive-brand {{
    color: {c['text_muted']};
    font-size: 0.8rem;
    margin-top: 8px;
    letter-spacing: 0.5px;
}}
.revive-rule {{
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, {c['accent_gold']}, {c['accent_orange']}, transparent);
    margin: 16px 0;
    opacity: 0.5;
}}

/* ── Animated pulse dot ──────────────────────────────── */
@keyframes mangoPulse {{
    0%, 100% {{ opacity: 1;   box-shadow: 0 0 6px {c['accent_gold']}; }}
    50%       {{ opacity: 0.5; box-shadow: 0 0 18px {c['accent_bright']}; }}
}}
.pulse-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: {c['accent_gold']};
    animation: mangoPulse 2s ease-in-out infinite;
    margin-left: 8px;
    vertical-align: middle;
}}

/* ── Upload zone ─────────────────────────────────────── */
.upload-zone {{
    border: 2px dashed {c['accent_gold']};
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    background: rgba(242,185,73,0.06);
    transition: all 0.3s ease;
}}
.upload-zone:hover {{
    background: rgba(242,232,41,0.1);
    border-color: {c['accent_orange']};
    box-shadow: 0 0 24px rgba(242,185,73,0.25);
}}

/* ── Format chips ────────────────────────────────────── */
.format-chip {{
    display: inline-block;
    background: rgba(242,185,73,0.15);
    border: 1px solid rgba(242,185,73,0.5);
    color: {c['text_primary']};
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin: 2px;
    font-weight: 500;
}}

/* ── Agent rows (st.markdown fallback styles) ────────── */
.agent-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    background: rgba(242,185,73,0.06);
    border: 1.5px solid rgba(242,185,73,0.25);
    transition: all 0.3s ease;
}}
.agent-row.active {{
    border-color: {c['accent_gold']};
    background: rgba(242,185,73,0.14);
    box-shadow: 0 0 16px rgba(242,185,73,0.3);
}}
.agent-row.complete {{
    border-color: rgba(242,116,48,0.5);
    background: rgba(242,116,48,0.07);
}}
.agent-row.error {{
    border-color: rgba(217,64,16,0.4);
    background: rgba(217,64,16,0.06);
}}

@keyframes activePulse {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.3; }}
}}
.status-dot {{
    width: 10px; height: 10px;
    border-radius: 50%; flex-shrink: 0;
}}
.status-dot.waiting  {{ background: {c['agent_wait']}; border: 1px solid rgba(242,185,73,0.4); }}
.status-dot.active   {{ background: {c['agent_active']}; animation: activePulse 1s ease-in-out infinite; box-shadow: 0 0 8px {c['agent_active']}; }}
.status-dot.complete {{ background: {c['agent_done']}; }}
.status-dot.error    {{ background: {c['error']}; }}

.agent-name    {{ font-weight: 600; color: {c['text_primary']}; font-size: 0.9rem; }}
.agent-output  {{ color: {c['text_muted']}; font-size: 0.78rem; font-style: italic; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.latency-badge {{ background: rgba(242,185,73,0.2); border: 1px solid rgba(242,185,73,0.5); color: {c['text_primary']}; border-radius: 12px; padding: 1px 8px; font-size: 0.7rem; font-weight: 600; }}

/* ── Model badges ────────────────────────────────────── */
.model-badge-vision {{
    display: inline-block;
    background: rgba(242,185,73,0.18);
    border: 1px solid rgba(242,185,73,0.55);
    color: {c['text_primary']};
    border-radius: 12px; padding: 1px 8px; font-size: 0.7rem;
    font-weight: 600; white-space: nowrap;
}}
.model-badge-reasoning {{
    display: inline-block;
    background: rgba(242,116,48,0.15);
    border: 1px solid rgba(242,116,48,0.45);
    color: {c['accent_orange']};
    border-radius: 12px; padding: 1px 8px; font-size: 0.7rem;
    font-weight: 600; white-space: nowrap;
}}
.model-badge-tool {{
    display: inline-block;
    background: rgba(237,211,119,0.25);
    border: 1px solid rgba(237,211,119,0.6);
    color: {c['text_primary']};
    border-radius: 12px; padding: 1px 8px; font-size: 0.7rem;
    font-weight: 600; white-space: nowrap;
}}

/* ── Era badge ───────────────────────────────────────── */
.era-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(242,185,73,0.15);
    border: 1.5px solid {c['accent_gold']};
    color: {c['text_primary']};
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.85rem;
    font-family: 'Georgia', serif;
    font-weight: 600;
    letter-spacing: 0.3px;
}}

/* ── Verdict badges ──────────────────────────────────── */
.verdict-approved {{
    display: inline-block;
    background: rgba(242,116,48,0.15);
    border: 1.5px solid {c['accent_orange']};
    color: {c['accent_orange']};
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.85rem; font-weight: 700;
}}
.verdict-retry {{
    display: inline-block;
    background: rgba(217,64,16,0.12);
    border: 1.5px solid {c['error']};
    color: {c['error']};
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.85rem; font-weight: 700;
}}

/* ── Severity pills ──────────────────────────────────── */
.severity-mild     {{ display:inline-block; background:rgba(242,232,41,.2);  border:1px solid rgba(242,185,73,.6);  color:{c['text_primary']}; border-radius:12px; padding:2px 10px; font-size:.78rem; font-weight:600; }}
.severity-moderate {{ display:inline-block; background:rgba(242,185,73,.2);  border:1px solid rgba(242,185,73,.6);  color:{c['text_primary']}; border-radius:12px; padding:2px 10px; font-size:.78rem; font-weight:600; }}
.severity-severe   {{ display:inline-block; background:rgba(242,116,48,.2);  border:1px solid rgba(242,116,48,.6);  color:{c['accent_orange']}; border-radius:12px; padding:2px 10px; font-size:.78rem; font-weight:600; }}
.damage-pill {{ display:inline-block; background:rgba(242,185,73,.15); border:1px solid rgba(242,185,73,.4); color:{c['text_primary']}; border-radius:12px; padding:2px 10px; font-size:.75rem; margin:2px; }}

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, {c['accent_gold']}, {c['accent_orange']});
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 1rem;
    transition: all 0.2s ease;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(242,116,48,0.3);
}}
.stButton > button:hover {{
    box-shadow: 0 4px 22px rgba(242,116,48,0.5);
    transform: translateY(-1px);
    background: linear-gradient(135deg, {c['accent_orange']}, {c['accent_gold']});
}}
[data-testid="stDownloadButton"] > button {{
    background: transparent;
    border: 1.5px solid {c['accent_gold']};
    color: {c['text_primary']};
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: rgba(242,185,73,0.12);
    border-color: {c['accent_orange']};
    box-shadow: 0 0 14px rgba(242,185,73,0.3);
}}

/* ── Sidebar delete (bin) buttons ── transparent, no border ── */
[data-testid="stSidebar"] [data-testid="stColumn"]:last-child button,
[data-testid="stSidebar"] [data-testid="stColumn"]:last-child button:focus,
[data-testid="stSidebar"] [data-testid="stColumn"]:last-child button:active {{
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 2px !important;
    font-size: 1.25rem !important;
    min-height: 34px !important;
    line-height: 1 !important;
    color: rgba(120,70,40,0.75) !important;
}}
[data-testid="stSidebar"] [data-testid="stColumn"]:last-child button:hover {{
    background: rgba(220,38,38,0.12) !important;
    background-color: rgba(220,38,38,0.12) !important;
    background-image: none !important;
    border-radius: 8px !important;
    transform: none !important;
}}

/* ── Streamlit element overrides ─────────────────────── */
[data-testid="stFileUploader"] {{
    background: rgba(242,185,73,0.06);
    border: 1.5px dashed rgba(242,185,73,0.5);
    border-radius: 12px;
}}
[data-testid="stFileUploader"] * {{
    color: {c['text_primary']} !important;
}}
[data-testid="stTextInput"] input {{
    background: #FFFFFF;
    border: 1.5px solid rgba(242,185,73,0.5);
    color: {c['text_primary']};
    border-radius: 8px;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {c['accent_gold']};
    box-shadow: 0 0 0 2px rgba(242,185,73,0.2);
}}
[data-testid="stMetric"] {{
    background: {c['card_bg']};
    border: 1.5px solid {c['card_border']};
    border-radius: 10px;
    padding: 12px;
}}
.stExpander {{
    background: {c['card_bg']};
    border: 1.5px solid {c['card_border']} !important;
    border-radius: 10px;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(242,185,73,0.1);
    border-radius: 8px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {c['text_muted']};
    font-weight: 600;
}}
.stTabs [aria-selected="true"] {{
    color: {c['accent_orange']} !important;
}}
/* Warning/info/error boxes */
[data-testid="stAlert"] {{
    border-radius: 10px;
}}

/* ── Footer ──────────────────────────────────────────── */
.revive-footer {{
    text-align: center;
    padding: 32px 0 16px;
    color: {c['text_muted']};
    font-size: 0.8rem;
    border-top: 1.5px solid rgba(242,185,73,0.3);
    margin-top: 40px;
}}
</style>
"""

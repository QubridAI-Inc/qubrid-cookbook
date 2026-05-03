"""Custom styling for the Recall AI interface."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st


def inject_styles() -> None:
    """Inject the custom CSS theme used across the application."""
    st.markdown(
        dedent(
            """
            <style>
            :root {
                --bg: #fffdfb;
                --bg-soft: #f7f3ee;
                --surface: rgba(255, 255, 255, 0.88);
                --surface-strong: #ffffff;
                --sidebar: #eef8ef;
                --mint: #ADEBB3;
                --coral: #FF857A;
                --lavender: #EBAEE6;
                --brown: #6B403C;
                --text: #6B403C;
                --text-soft: #85615d;
                --text-muted: #a3837e;
                --line: rgba(107, 64, 60, 0.12);
                --glow: rgba(173, 235, 179, 0.35);
                --warning: #FF857A;
                --error: #FF857A;
            }

            html, body, [class*="css"] {
                font-family: "Avenir Next", "Trebuchet MS", sans-serif;
            }

            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at top left, rgba(173, 235, 179, 0.55), transparent 22%),
                    radial-gradient(circle at top right, rgba(235, 174, 230, 0.32), transparent 18%),
                    linear-gradient(180deg, var(--bg) 0%, var(--bg-soft) 100%);
                color: var(--text);
            }

            [data-testid="stAppViewContainer"]::before {
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image:
                    linear-gradient(rgba(107, 64, 60, 0.025) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(107, 64, 60, 0.025) 1px, transparent 1px);
                background-size: 44px 44px;
                mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.35), transparent 95%);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #f4fbf4 0%, var(--sidebar) 100%);
                border-right: 1px solid rgba(107, 64, 60, 0.08);
            }

            [data-testid="stSidebar"] .recall-stats-card,
            [data-testid="stSidebar"] .recall-context-card {
                margin-top: 1rem;
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            [data-testid="stToolbar"] {
                background: transparent;
            }

            .block-container {
                max-width: 1440px;
                padding-top: 2rem;
                padding-bottom: 2.8rem;
            }

            .stMarkdown p,
            .stMarkdown div,
            .stMarkdown span,
            .stMarkdown strong,
            .stMarkdown li,
            label {
                color: var(--text);
            }

            .recall-memory-shell,
            .recall-prompt-draft,
            .recall-stats-card,
            .recall-sidebar-card,
            .recall-session-card,
            .recall-context-card {
                border: 1px solid var(--line);
                box-shadow: 0 16px 34px rgba(107, 64, 60, 0.08);
            }

            .recall-hero {
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding: 0.25rem 1.65rem 0.5rem 1.65rem;
                margin-bottom: 0.15rem;
                border: 0;
                box-shadow: none;
                background: transparent;
            }

            .recall-hero-copy {
                max-width: 38rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.55rem;
            }

            .recall-title {
                margin: 0;
                font-family: "Iowan Old Style", "Palatino Linotype", serif;
                font-size: clamp(3rem, 5vw, 5.1rem);
                line-height: 0.92;
                letter-spacing: -0.045em;
                color: var(--text);
            }

            .recall-kicker,
            .recall-persona-summary-label {
                color: var(--coral);
                font-size: 0.74rem;
                letter-spacing: 0.18em;
                text-transform: uppercase;
            }

            .recall-kicker {
                margin: 0.2rem 0 0 0;
            }

            .recall-hero-copy-block {
                display: flex;
                flex-direction: column;
                max-width: 44rem;
            }

            .recall-hero-lead {
                margin: 0;
                color: var(--text-soft);
                line-height: 1.6;
                font-size: 1.04rem;
                color: var(--text);
                font-weight: 600;
            }

            .recall-brand-badge,
            .recall-locked-badge,
            .recall-topic-pill,
            .recall-context-badge,
            .recall-session-persona {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                border-radius: 999px;
                padding: 0.48rem 0.85rem;
                border: 1px solid rgba(107, 64, 60, 0.1);
                background: rgba(235, 174, 230, 0.18);
                color: var(--text);
            }

            .recall-brand-dot {
                width: 0.55rem;
                height: 0.55rem;
                border-radius: 50%;
                background: var(--coral);
                box-shadow: 0 0 0 0 rgba(255, 133, 122, 0.45);
                animation: recall-pulse-dot 2.4s ease-in-out infinite;
            }

            .recall-agent-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.3rem;
                border-radius: 999px;
                padding: 0.3rem 0.7rem;
                border: 1px solid rgba(0, 150, 120, 0.25);
                background: rgba(0, 200, 150, 0.12);
                color: #00a878;
                font-size: 0.72rem;
                font-weight: 600;
                margin-left: 0.4rem;
            }

            .recall-soft-label,
            .recall-section-copy,
            .recall-stats-label,
            .recall-bubble-meta,
            .recall-capacity-sub,
            .recall-session-meta {
                color: var(--text-soft);
            }

            .recall-section-head {
                margin: 0.45rem 0 0.75rem 0;
            }

            .recall-section-head-tight {
                margin-top: 0.8rem;
            }

            .recall-section-title {
                font-size: 1.02rem;
                font-weight: 800;
                color: var(--text);
                margin-bottom: 0.25rem;
            }

            .recall-memory-shell {
                padding: 1rem 1.1rem;
                margin: 0.55rem 0 1rem 0;
                border-radius: 22px;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(250, 244, 239, 0.96));
            }

            .recall-memory-bar-head,
            .recall-memory-bar-foot,
            .recall-stats-row,
            .recall-session-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.8rem;
            }

            .recall-memory-count {
                color: var(--coral);
                font-size: 0.92rem;
                font-weight: 700;
            }

            .recall-memory-bar {
                width: 100%;
                height: 10px;
                border-radius: 999px;
                background: rgba(107, 64, 60, 0.08);
                overflow: hidden;
                margin: 0.65rem 0 0.8rem 0;
            }

            .recall-memory-bar-fill {
                height: 100%;
                border-radius: inherit;
                box-shadow: 0 0 24px var(--glow);
                animation: recall-breathe 3s ease-in-out infinite;
            }

            .recall-persona-summary {
                margin: 0.8rem 0 0.3rem 0;
                padding: 0.8rem 0.95rem;
                border-radius: 16px;
                border: 1px solid rgba(107, 64, 60, 0.1);
                background: rgba(235, 174, 230, 0.14);
            }

            .recall-persona-summary-label {
                display: block;
                margin-bottom: 0.35rem;
            }

            .recall-persona-summary-text {
                color: var(--text);
                font-size: 0.95rem;
                line-height: 1.5;
            }

            [data-testid="stSelectbox"] > div[data-baseweb="select"] > div {
                background: rgba(255, 255, 255, 0.96);
                border-color: rgba(107, 64, 60, 0.14);
                border-radius: 14px;
                min-height: 3rem;
            }

            [data-testid="stSelectbox"] svg {
                fill: var(--coral);
            }

            [data-testid="stToggle"] {
                margin: 0.2rem 0 0.65rem 0;
            }

            [data-testid="stToggle"] label p {
                color: var(--text);
                font-weight: 600;
            }

            [data-testid="stToggle"] [data-testid="stWidgetLabelHelpInline"] {
                color: var(--text-soft);
            }

            .recall-prompt-draft {
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
                border-radius: 22px;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(244, 251, 244, 0.96));
            }

            .recall-prompt-draft-text {
                color: var(--text);
                line-height: 1.65;
                font-size: 1rem;
            }

            .recall-bubble {
                border-radius: 20px;
                padding: 0.95rem 1rem;
                border: 1px solid transparent;
                animation: recall-rise 0.28s ease both;
            }

            .recall-message-meta {
                font-size: 0.8rem;
                font-weight: 700;
                margin-bottom: 0.45rem;
                color: var(--text-soft);
            }

            .recall-message-meta.assistant {
                color: var(--text);
            }

            [data-testid="stChatMessageContent"] p,
            [data-testid="stChatMessageContent"] li,
            [data-testid="stChatMessageContent"] strong,
            [data-testid="stChatMessageContent"] h1,
            [data-testid="stChatMessageContent"] h2,
            [data-testid="stChatMessageContent"] h3 {
                color: var(--text);
            }

            [data-testid="stChatMessageContent"] h1,
            [data-testid="stChatMessageContent"] h2,
            [data-testid="stChatMessageContent"] h3 {
                font-family: "Iowan Old Style", "Palatino Linotype", serif;
                font-weight: 700;
                margin-top: 1rem;
                margin-bottom: 0.6rem;
            }

            [data-testid="stChatMessageContent"] p,
            [data-testid="stChatMessageContent"] li {
                line-height: 1.7;
                font-size: 1rem;
            }

            [data-testid="stChatMessageContent"] ul,
            [data-testid="stChatMessageContent"] ol {
                padding-left: 1.25rem;
            }

            .recall-bubble-user {
                background: linear-gradient(180deg, rgba(173, 235, 179, 0.42), rgba(255, 255, 255, 0.98));
                border-color: rgba(107, 64, 60, 0.12);
                box-shadow: inset 4px 0 0 rgba(255, 133, 122, 0.88);
            }

            .recall-bubble-assistant {
                background: linear-gradient(180deg, rgba(235, 174, 230, 0.2), rgba(255, 255, 255, 0.98));
                border-color: rgba(107, 64, 60, 0.12);
                box-shadow: inset 4px 0 0 rgba(173, 235, 179, 0.92);
            }

            .recall-avatar {
                width: 1.5rem;
                height: 1.5rem;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                border-radius: 999px;
                background: linear-gradient(135deg, rgba(255, 133, 122, 0.28), rgba(235, 174, 230, 0.24));
                border: 1px solid rgba(107, 64, 60, 0.12);
                color: var(--text);
                font-weight: 800;
                flex: 0 0 auto;
            }

            .recall-message-content {
                color: var(--text);
                font-size: 0.98rem;
                line-height: 1.68;
            }

            .recall-stats-card,
            .recall-sidebar-card,
            .recall-session-card,
            .recall-context-card {
                border-radius: 24px;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(244, 251, 244, 0.98));
            }

            .recall-stats-card,
            .recall-sidebar-card,
            .recall-context-card {
                padding: 1.05rem 1.05rem 0.4rem 1.05rem;
                margin-bottom: 1rem;
            }

            .recall-stats-row {
                padding: 0.52rem 0;
                border-bottom: 1px solid rgba(107, 64, 60, 0.08);
                font-size: 0.93rem;
            }

            .recall-stats-row:last-child {
                border-bottom: 0;
            }

            .recall-topics-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin: 0.8rem 0;
            }

            .recall-capacity {
                margin: 0.85rem 0 0.35rem 0;
                padding: 1rem;
                border-radius: 20px;
                background: linear-gradient(180deg, rgba(173, 235, 179, 0.38), rgba(255, 255, 255, 0.94));
                border: 1px solid rgba(107, 64, 60, 0.08);
            }

            .recall-capacity-hero {
                font-size: 1.28rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
                color: var(--text);
            }

            .recall-session-card {
                padding: 0.95rem 0.95rem 0.65rem 0.95rem;
                margin-bottom: 0.75rem;
            }

            .recall-session-title {
                font-size: 0.95rem;
                font-weight: 750;
                margin: 0.45rem 0 0.55rem 0;
                color: var(--text);
            }

            .recall-typing {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.85rem 1rem;
                border-radius: 18px;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(244, 251, 244, 0.96));
                border: 1px solid rgba(107, 64, 60, 0.12);
            }

            .recall-dot {
                width: 0.46rem;
                height: 0.46rem;
                border-radius: 50%;
                background: var(--coral);
                opacity: 0.4;
                animation: recall-bounce 1.1s infinite ease-in-out;
            }

            .recall-dot:nth-child(2) {
                animation-delay: 0.18s;
            }

            .recall-dot:nth-child(3) {
                animation-delay: 0.36s;
            }

            .recall-footer {
                text-align: center;
                color: var(--text-muted);
                margin-top: 1.4rem;
                font-size: 0.88rem;
                line-height: 1.4;
            }

            [data-testid="stButton"] > button {
                min-height: 2.85rem;
                border-radius: 14px;
                border: 1px solid rgba(107, 64, 60, 0.1);
                background: rgba(255, 255, 255, 0.96);
                color: var(--text);
                font-weight: 700;
                transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
            }

            [data-testid="stButton"] > button[kind="primary"] {
                background: linear-gradient(180deg, rgba(255, 133, 122, 0.92), rgba(235, 174, 230, 0.9));
                color: #4c2c28;
                border-color: rgba(107, 64, 60, 0.08);
            }

            [data-testid="stButton"] > button:hover {
                transform: translateY(-1px);
                border-color: rgba(255, 133, 122, 0.4);
                box-shadow: 0 0 0 3px rgba(235, 174, 230, 0.2);
            }

            [data-testid="stChatInput"] {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 244, 239, 0.98));
                border-radius: 18px;
                border: 1px solid rgba(107, 64, 60, 0.12);
                padding: 0.2rem 0.3rem;
                box-shadow: 0 10px 24px rgba(107, 64, 60, 0.08);
            }

            [data-testid="stChatInput"] textarea,
            [data-testid="stChatInput"] input {
                color: var(--text);
            }

            [data-testid="stExpander"] details {
                border: 1px solid rgba(107, 64, 60, 0.12);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.92);
            }

            @media (max-width: 900px) {
                .block-container {
                    padding-top: 1.3rem;
                }
            }

            @keyframes recall-rise {
                from {
                    transform: translateY(8px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            @keyframes recall-breathe {
                0%, 100% {
                    filter: brightness(1);
                    transform: scaleX(1);
                }
                50% {
                    filter: brightness(1.05);
                    transform: scaleX(1.004);
                }
            }

            @keyframes recall-bounce {
                0%, 80%, 100% {
                    transform: translateY(0);
                    opacity: 0.4;
                }
                40% {
                    transform: translateY(-5px);
                    opacity: 1;
                }
            }

            @keyframes recall-pulse-dot {
                0%, 100% {
                    box-shadow: 0 0 0 0 rgba(255, 133, 122, 0.45);
                }
                50% {
                    box-shadow: 0 0 0 9px rgba(255, 133, 122, 0);
                }
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

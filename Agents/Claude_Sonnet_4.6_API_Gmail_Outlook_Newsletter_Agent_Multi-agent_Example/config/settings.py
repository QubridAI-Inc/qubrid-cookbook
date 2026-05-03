"""
config/settings.py

Central configuration for NewsletterAgent.
All API keys are loaded from environment variables — never hardcoded.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── API Keys ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
QUBRID_API_KEY: str = os.getenv("QUBRID_API_KEY", "")
QUBRID_BASE_URL: str = os.getenv("QUBRID_BASE_URL", "https://platform.qubrid.com/v1")
# LiteLLM routes via Qubrid using double-prefix (LiteLLM strips first prefix,
# Qubrid receives the real model name e.g. "openai/gpt-5.4")
QUBRID_MODEL_GPT: str = os.getenv("QUBRID_MODEL_GPT", "openai/openai/gpt-5.4")
QUBRID_MODEL_CLAUDE: str = os.getenv("QUBRID_MODEL_CLAUDE", "openai/anthropic/claude-sonnet-4-6")
QUBRID_MODEL_GEMINI: str = os.getenv("QUBRID_MODEL_GEMINI", "openai/google/gemini-3-flash-preview")
COMPOSIO_API_KEY: str = os.getenv("COMPOSIO_API_KEY", "")
COMPOSIO_MCP_URL: str = os.getenv("COMPOSIO_MCP_URL", "")
COMPOSIO_ENTITY_ID: str = os.getenv("COMPOSIO_ENTITY_ID", "default")
COMPOSIO_CACHE_DIR: str = os.getenv(
    "COMPOSIO_CACHE_DIR",
    os.path.join(BASE_DIR, ".composio_cache"),
)

# ── Model Names ───────────────────────────────────────────────────────────────
# ADK agents use Gemini directly (native, no LiteLLM) — avoids routing/auth issues
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
# Writer uses Qubrid via direct OpenAI-compatible client (no LiteLLM)
WRITER_MODEL: str = "anthropic/claude-sonnet-4-6"

# ── App Metadata ──────────────────────────────────────────────────────────────
APP_NAME: str = "NewsletterAgent"
APP_TAGLINE: str = "Multi-agent intelligence · Real inbox delivery · Powered by Qubrid"
BRAND_LINE: str = ""

# ── File Paths ────────────────────────────────────────────────────────────────
DB_PATH: str = "database/newsletter.db"
OUTPUTS_DIR: str = "outputs/"

# ── Pipeline Constants ────────────────────────────────────────────────────────
MAX_STORIES: int = 5
SUPPORTED_TONES: list[str] = ["Professional", "Casual", "Bold", "Analytical"]
SUPPORTED_LENGTHS: list[str] = [
    "Short (3 stories)",
    "Medium (5 stories)",
    "Long (7 stories)",
]

# ── Summer Breeze Palette ─────────────────────────────────────────────────────
COLOR_YELLOW: str = "#FFEB3B"
COLOR_CORAL: str = "#F88379"
COLOR_SKY: str = "#82C8E5"
COLOR_SAND: str = "#E6D8C4"
COLOR_BG: str = "#FAFAF7"
COLOR_SIDEBAR_BG: str = "#F5EFE6"
COLOR_TEXT_PRIMARY: str = "#1A1A1A"
COLOR_TEXT_SECONDARY: str = "#5C5C5C"
COLOR_TEXT_MUTED: str = "#9E9E9E"
COLOR_SUCCESS: str = "#4CAF50"
COLOR_WARNING: str = "#FF9800"
COLOR_ERROR: str = "#F44336"

# ── Agent Prompts ─────────────────────────────────────────────────────────────
ORCHESTRATOR_PROMPT: str = """
You are NewsletterAgent, an AI-powered newsletter generator.
When a user gives you a topic, recipient email, and preferences:
1. Coordinate the research agents to find top stories
2. Filter for the most relevant and recent content
3. Write engaging summaries for each story
4. Format into a beautiful HTML newsletter
5. Deliver via the user's chosen platform (Gmail or Outlook)
Always confirm before sending. Report each step clearly.
"""

RESEARCH_PROMPT: str = """
You are a news research specialist. Search for the latest, most relevant
news and developments about the topic given to you by the user.
Find 3-5 high-quality, recent stories with: title, source, summary, url, date.
Focus on credible sources. Return structured results only.
"""

FILTER_PROMPT: str = """
You are a content editor. Review all stories provided and select the top 5
most relevant, credible, and interesting ones for a newsletter on the given topic.
Score each story 1-10 for relevance, recency, and impact.
Return only the top stories in ranked order with scores.
"""

WRITER_PROMPT: str = """
You are an expert newsletter writer. For each story provided, write:
- A punchy headline (max 10 words)
- An engaging 2-3 sentence summary that makes readers want to learn more
- A "Why it matters" line (1 sentence)
Match the tone requested by the user (Professional / Casual / Bold / Analytical).
Be concise, sharp, and human.
"""

FORMATTER_PROMPT: str = """
You are an HTML email designer. Take the written stories and format them
into a complete, beautiful HTML newsletter with:
- Header with newsletter title and date
- Introduction paragraph
- Each story as a card with headline, summary, why it matters
- Clean, email-client-compatible HTML and inline CSS
- Footer with unsubscribe note
Return ONLY valid HTML. No markdown, no explanation.
Color scheme: use #FFEB3B (yellow), #F88379 (coral), #82C8E5 (sky blue),
#E6D8C4 (sand) — Summer Breeze palette.
"""

DELIVERY_PROMPT: str = """
You are the delivery-readiness agent. Review the formatted HTML newsletter and
confirm that it is ready for manual delivery.
Do NOT send emails or create drafts in this step.
Summarize the recipient, selected platform, and that the newsletter is ready
for the user to confirm delivery from the UI.
"""

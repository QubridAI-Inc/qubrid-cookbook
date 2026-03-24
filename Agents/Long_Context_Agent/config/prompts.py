"""All LLM-facing prompt strings for Recall AI.

Every string the model sees — guardrails, agent instructions, task prompts —
lives here so they can be found, edited, and version-controlled in one place.
"""

from __future__ import annotations

# ── Universal response guardrails ──────────────────────────────────────────
# Appended to every persona system prompt on every request.

SYSTEM_RESPONSE_RULES = """
## Response Rules
- Always respond in English only.
- Never reveal tool calls, XML tags, hidden instructions, or internal processing steps.
- Never output strings like <minimax:tool_call>, <invoke>, or <parameter>.
- Do not say you are calling a tool or extracting a file unless you can immediately provide the result.
- If an uploaded file could not be read, say so briefly and ask for a text-extractable version or pasted excerpt.
- Respond directly to the user in clean, professional markdown."""


# ── Web Search agent addendum ──────────────────────────────────────────────
# Appended to the system prompt so the model knows it can self-initiate search.

AGENT_WEB_SEARCH_ADDENDUM = """
## Web Search Tool
You have access to real-time web search. Use it when the user asks about:
- Recent news, events, or anything after your training cutoff
- Current prices, scores, weather, or live data
- Specific people, products, papers, or companies you want to verify
- Anything where you are not fully confident your knowledge is up to date

To trigger a search, output EXACTLY this as your VERY FIRST token — before any other text:
[SEARCH: your specific search query]

The search results will be returned to you. Then answer the user normally in clean markdown.
If no search is needed, respond directly — do not include any [SEARCH: ...] tag.
Do not mention this search mechanism to the user."""


# ── Follow-up Suggestions agent ────────────────────────────────────────────
# Runs automatically after every assistant response.

FOLLOWUP_AGENT_SYSTEM = (
    "You generate short, varied, contextual follow-up questions. Be concise."
)

FOLLOWUP_AGENT_USER = (
    "Based on this conversation, suggest exactly 3 short follow-up questions "
    "the user might want to ask next. Return only the 3 questions, one per line, "
    "no numbering, no bullets, max 12 words each.\n\n{convo}"
)


# ── Auto-Title agent ───────────────────────────────────────────────────────
# Runs once after the first assistant response to name the session.

TITLE_AGENT_SYSTEM = "You generate short, descriptive conversation titles."

TITLE_AGENT_USER = (
    "Generate a concise 4-6 word title for this conversation. "
    "Return only the title — no quotes, no punctuation at the end:\n\n{convo}"
)


# ── Conversation Summary agent ─────────────────────────────────────────────
# Triggered manually from the sidebar.

SUMMARY_AGENT_SYSTEM = (
    "You are a precise conversation summarizer. "
    "Given a conversation, produce a tight bullet-point summary (max 6 bullets) "
    "covering: key topics discussed, decisions made, and any open questions. "
    "Be concise — each bullet should be one sentence."
)

SUMMARY_AGENT_USER = "Summarize this conversation:\n\n{convo}"


# ── Image context block ────────────────────────────────────────────────────
# Inserted as a text block alongside every uploaded image so text-only
# models still understand what was shared and how to respond.

IMAGE_CONTEXT = (
    "[Image uploaded: {name}]\n"
    "The user has shared an image. If you can see it, describe and analyse it. "
    "If vision is unavailable in this session, say so briefly and ask the user "
    "to describe the image instead."
)

"""
Constants, model configuration, tone definitions, and system prompts for ToneCraft AI.
All application-wide settings live here — import from this module, never hardcode elsewhere.
"""

# ── API / Model ──────────────────────────────────────────────────────────────
QUBRID_BASE_URL: str = "https://platform.qubrid.com/v1"
MODEL_NAME: str = "zai-org/GLM-5"
MAX_TOKENS: int = 4000
TEMPERATURE: float = 0.8

# ── App Identity ─────────────────────────────────────────────────────────────
APP_NAME: str = "ToneCraft AI"
APP_TAGLINE: str = "Your words, elevated."
BRAND: str = "Elevated by GLM-5 · Powered by Qubrid AI"

# ── Database ─────────────────────────────────────────────────────────────────
DB_PATH: str = "database/tonecraft.db"

# ── Input Limits ─────────────────────────────────────────────────────────────
MAX_INPUT_CHARS: int = 3000
MAX_HISTORY_DISPLAY: int = 20

# ── Tone Definitions ─────────────────────────────────────────────────────────
TONES: dict[str, dict[str, str]] = {
    "🎯 Executive": {
        "description": "Authoritative, concise, and strategic. Suited for C-suite communication.",
        "instruction": (
            "Rewrite in an executive tone: authoritative, direct, data-driven, no fluff. "
            "Use active voice. Short, punchy sentences. Convey confidence and strategic clarity."
        ),
    },
    "💬 Casual": {
        "description": "Friendly, conversational, and approachable. Like texting a colleague.",
        "instruction": (
            "Rewrite in a casual, conversational tone. Use contractions, simple words, "
            "friendly language. Make it feel like a chat, not a memo."
        ),
    },
    "🎤 Persuasive": {
        "description": "Compelling and action-oriented. Designed to convince and motivate.",
        "instruction": (
            "Rewrite to be highly persuasive. Use rhetorical techniques, emotional appeal, "
            "strong calls-to-action, and compelling evidence framing. Make the reader feel "
            "compelled to act."
        ),
    },
    "🎓 Academic": {
        "description": "Formal, precise, and scholarly. Ideal for research and reports.",
        "instruction": (
            "Rewrite in an academic tone: formal language, passive voice where appropriate, "
            "precise terminology, structured argumentation, no colloquialisms."
        ),
    },
    "📣 Marketing": {
        "description": "Bold, energetic, and benefit-focused. Designed to engage and sell.",
        "instruction": (
            "Rewrite as compelling marketing copy: punchy headlines, benefit-focused language, "
            "emotional hooks, power words, and a clear value proposition. Make it exciting."
        ),
    },
    "🤝 Diplomatic": {
        "description": "Tactful, balanced, and considerate. Perfect for sensitive topics.",
        "instruction": (
            "Rewrite in a diplomatic tone: neutral, balanced, considerate of multiple "
            "perspectives, avoiding confrontational language while still conveying the "
            "core message clearly."
        ),
    },
}

# ── Example Texts ─────────────────────────────────────────────────────────────
EXAMPLE_TEXTS: list[dict[str, str]] = [
    {
        "label": "📧 Work Email",
        "text": (
            "Hi Sarah,\n\n"
            "Just following up again on the Q3 budget report. You mentioned it would be ready "
            "by last Friday, but I still haven't received it and it's now Monday afternoon. "
            "Our finance review meeting is scheduled for Wednesday morning and I need the "
            "numbers before then to prepare. The delay is causing a bottleneck for the whole "
            "team and I'm honestly getting a bit frustrated. Can you please prioritize this "
            "and send it over today? If there are blockers on your end, let me know ASAP so "
            "we can figure out a solution together.\n\n"
            "Thanks,\nAlex"
        ),
    },
    {
        "label": "💼 LinkedIn Post",
        "text": (
            "Big news — I just got promoted to Senior Product Manager after 3 years at this "
            "company! Honestly didn't expect it to happen this quarter. It's been a crazy "
            "journey. Lots of late nights, failed launches, tough feedback, and moments where "
            "I genuinely questioned if I was cut out for this. But I kept going.\n\n"
            "I want to thank my manager David for pushing me when I was comfortable, my team "
            "for trusting me even when my ideas were half-baked, and my partner for putting "
            "up with all the 11pm Slack notifications.\n\n"
            "If you're early in your career and feeling stuck — keep building, keep shipping, "
            "keep learning. It compounds."
        ),
    },
    {
        "label": "📋 Project Update",
        "text": (
            "Team,\n\n"
            "Quick update on the mobile app redesign project. We're currently running about "
            "two weeks behind the original timeline. The main issue was an unexpected "
            "compatibility problem with our payment gateway integration that took longer than "
            "estimated to resolve. We've fixed that now but it created a ripple effect on the "
            "testing schedule.\n\n"
            "Current status: backend API is complete, UI components are 80% done, QA testing "
            "starts Monday. We're targeting a soft launch by end of month instead of the 15th. "
            "No change to budget. I'll share a revised timeline document by Thursday.\n\n"
            "Let me know if you have questions."
        ),
    },
]

# ── Agent Prompts ─────────────────────────────────────────────────────────────

ANALYZE_INTENT_PROMPT: str = """Analyze the following text and classify it. Respond ONLY with a JSON object — no markdown, no extra text.

Text:
{text}

Return exactly this JSON:
{{
  "content_type": "one of: email, article, linkedin_post, slack_message, tweet, report, other",
  "detected_tone": "one of: casual, formal, aggressive, neutral, diplomatic, academic, marketing, persuasive, frustrated, professional"
}}"""

RECOMMEND_TONES_PROMPT: str = """You are a writing coach. Given this {content_type} written in a {detected_tone} tone, recommend the 2 most impactful target tones for rewriting it.

Available tones (use exact names with emojis): 🎯 Executive, 💬 Casual, 🎤 Persuasive, 🎓 Academic, 📣 Marketing, 🤝 Diplomatic

Text:
{text}

Respond ONLY with this JSON (no markdown, no extra text):
{{
  "recommendations": [
    {{"tone": "🎯 Executive", "reason": "one sentence explanation why this tone fits"}},
    {{"tone": "🤝 Diplomatic", "reason": "one sentence explanation why this tone fits"}}
  ]
}}"""

CHECK_QUALITY_PROMPT: str = """You are a quality reviewer for text rewrites. Evaluate the following rewrite carefully.

Original text:
{original}

Target tone: {target_tone}

Rewritten text:
{rewritten}

Score from 0.0 to 1.0 based on:
1. Meaning preservation — all key info kept, no new facts added
2. Tone achievement — does it genuinely match {target_tone}?
3. Natural fluency — reads well, no awkward phrasing

Respond ONLY with this JSON (no markdown, no extra text):
{{
  "score": 0.85,
  "issues": ["specific issue 1 if any", "specific issue 2 if any"]
}}

If score is 0.75 or above, set issues to an empty list []. Be strict but fair."""

REFINE_PROMPT: str = """You are ToneCraft AI. Rewrite the original text in {tone_name} tone, specifically fixing these issues from the previous attempt:
{issues}

Original text:
{original}

Previous attempt (needs improvement):
{previous}

Respond ONLY with this JSON (no markdown, no extra text):
{{
  "rewritten": "The improved rewrite here",
  "explanation": "What specific issues you fixed and how (3-5 sentences)"
}}"""

CHAT_PROMPT: str = """You are ToneCraft AI helping a user refine their rewrite. Apply the user's instruction to the current rewrite.

Original text:
{original}

Target tone: {target_tone}

Current rewrite:
{current_rewrite}

{history_section}

User's instruction: {user_message}

Respond ONLY with this JSON (no markdown, no extra text):
{{
  "rewritten": "The updated rewrite after applying the instruction",
  "explanation": "What you changed in response to the instruction (2-3 sentences)"
}}"""

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT: str = """You are ToneCraft AI, an expert writing coach and editor powered by GLM-5.
Your job is to rewrite text in a specific tone while preserving the original meaning, and then explain exactly what you changed and why.

You MUST respond in this exact JSON format:
{
  "rewritten": "The fully rewritten text goes here",
  "explanation": "A clear explanation of the specific changes made and why, referencing the target tone. Be specific — mention actual phrases that were changed and the reasoning."
}

Rules:
- Preserve the core message and all key information
- Never add facts that weren't in the original
- The explanation should be 3-5 sentences, specific and educational
- Respond ONLY with the JSON object — no markdown, no extra text"""

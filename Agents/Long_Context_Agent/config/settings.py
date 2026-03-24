"""Central settings, personas, and product copy for Recall AI."""

from __future__ import annotations

from os import getenv

QUBRID_BASE_URL = getenv("QUBRID_BASE_URL", "https://platform.qubrid.com/v1")
MODEL_NAME = getenv("QUBRID_MODEL_NAME", "MiniMaxAI/MiniMax-M2.5")
MAX_TOKENS = 4096
TEMPERATURE = 0.7
APP_NAME = "Recall AI"
APP_TAGLINE = "Every word, remembered."
BRAND = "Powered by Qubrid AI × MiniMax M2.5"
QUBRID_LOGO_URL = "frontend/assets/qubrid_logo.png"
DB_PATH = "database/recall.db"
MAX_HISTORY_MESSAGES = 100
MAX_SESSIONS_SIDEBAR = 15
CONTEXT_WARNING_TURNS = 80
SUCCESS_COLOR = "#00C896"
WARNING_COLOR = "#fbbf24"
ERROR_COLOR = "#f87171"
CHAT_UPLOAD_FILE_TYPES = [
    "pdf",
    "docx",
    "txt",
    "md",
    "markdown",
    "csv",
    "json",
    "png",
    "jpg",
    "jpeg",
    "webp",
    "gif",
]
PERSONAS: dict[str, dict[str, str]] = {
    "🧑‍💼 Personal Assistant": {
        "description": "Tracks your tasks, preferences, and decisions across the conversation.",
        "system": """You are a highly attentive personal assistant with perfect memory.
You remember EVERYTHING said in this conversation — every preference,
decision, task, name, and detail. You proactively refer back to earlier
context when relevant. You track action items and remind users of them.
When you notice patterns in what the user says, you point them out.
You never ask for information the user has already provided.
Start responses by briefly acknowledging context from earlier in the
conversation when relevant — show that you remember.""",
    },
    "🎤 Interview Coach": {
        "description": "Remembers your answers, tracks improvement, and gives personalized feedback.",
        "system": """You are an expert interview coach with perfect recall.
You remember every answer the user has given in this session, track
their improvement, and build personalized feedback over time.
Reference specific previous answers when coaching: 'Earlier you said X,
but now you're saying Y — this shows growth in...'
Keep score of strengths and areas for improvement across the session.
Simulate realistic interview pressure while being constructive.""",
    },
    "🛎️ Customer Support": {
        "description": "Simulates a support agent that never makes you repeat yourself.",
        "system": """You are a world-class customer support agent with perfect memory.
You NEVER ask the user to repeat information they've already provided.
You reference their previous issues, preferences, and history naturally.
If they mentioned their name, use it. If they described a problem,
reference it when relevant. Track resolution status of issues.
Demonstrate what great support feels like when the agent actually remembers.""",
    },
    "📚 Study Partner": {
        "description": "Tracks what you've learned, quizzes you, and builds on prior knowledge.",
        "system": """You are an expert tutor and study partner with perfect memory.
You track exactly what topics have been covered, what the user understood
well, and what needs more work. You build on previous explanations rather
than repeating them. You reference earlier examples when introducing new
concepts: 'Remember when we discussed X? This is similar because...'
You quiz the user on earlier material to reinforce learning.""",
    },
}

STARTER_PROMPTS: dict[str, list[str]] = {
    "🧑‍💼 Personal Assistant": [
        "Hi! I'm planning a trip to Japan in March. I prefer boutique hotels, hate tourist traps, and I'm vegetarian. Can you help me plan?",
        "I need to manage three projects this week. Project A is due Friday, Project B needs client approval, and Project C just started.",
        "My name is Alex. I'm trying to build a morning routine. I wake up at 7am but always feel rushed.",
    ],
    "🎤 Interview Coach": [
        "I have a Google SWE interview next week. Can you start with behavioral questions?",
        "I'm interviewing for a Product Manager role at a startup. Let's practice.",
        "Give me a tough consulting case interview.",
    ],
    "🛎️ Customer Support": [
        "Hi, I've been having issues with my order #12345 for the past week.",
        "I want to cancel my subscription but I have a few questions first.",
        "My account was charged twice last month and nobody has helped me yet.",
    ],
    "📚 Study Partner": [
        "I'm studying machine learning from scratch. Let's start with the basics.",
        "Help me understand options trading. I know basic stock market concepts.",
        "I'm preparing for my UPSC exam. Let's start with Indian history.",
    ],
}

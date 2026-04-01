"""
agents/writer.py

Newsletter writer agent: uses Gemini natively (via GOOGLE_API_KEY) to
turn the filtered stories into polished newsletter copy.
"""

from google.adk.agents import Agent  # type: ignore
from google.adk.models.lite_llm import LiteLlm  # type: ignore

from config.settings import QUBRID_MODEL_CLAUDE, QUBRID_API_KEY, QUBRID_BASE_URL, WRITER_PROMPT

qubrid_claude = LiteLlm(
    model=QUBRID_MODEL_CLAUDE,
    api_key=QUBRID_API_KEY,
    api_base=QUBRID_BASE_URL
)

writer_agent = Agent(
    name="newsletter_writer",
    model=qubrid_claude,
    instruction=(
        WRITER_PROMPT + "\n\nUse the requested user tone from the conversation "
        "and transform the filtered stories into final newsletter copy."
    ),
)

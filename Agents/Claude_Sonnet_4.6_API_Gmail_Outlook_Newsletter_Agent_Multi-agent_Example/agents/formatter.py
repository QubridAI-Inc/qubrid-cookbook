"""
agents/formatter.py

HTML formatter agent: converts written newsletter copy into a
Summer Breeze-themed, email-client-compatible HTML document.
"""

from google.adk.agents import Agent  # type: ignore
from google.adk.models.lite_llm import LiteLlm  # type: ignore

from config.settings import QUBRID_MODEL_GPT, QUBRID_API_KEY, QUBRID_BASE_URL, FORMATTER_PROMPT

qubrid_gpt = LiteLlm(
    model=QUBRID_MODEL_GPT,
    api_key=QUBRID_API_KEY,
    api_base=QUBRID_BASE_URL
)

formatter_agent = Agent(
    name="html_formatter",
    model=qubrid_gpt,
    instruction=FORMATTER_PROMPT,
)

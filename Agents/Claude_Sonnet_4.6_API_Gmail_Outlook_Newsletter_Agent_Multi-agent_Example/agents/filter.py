"""
agents/filter.py

Content filter agent: selects and ranks the top N stories
from the combined research output for the newsletter.
"""

from google.adk.agents import Agent  # type: ignore
from google.adk.models.lite_llm import LiteLlm  # type: ignore

from config.settings import QUBRID_MODEL_GPT, QUBRID_API_KEY, QUBRID_BASE_URL, FILTER_PROMPT

qubrid_gpt = LiteLlm(
    model=QUBRID_MODEL_GPT,
    api_key=QUBRID_API_KEY,
    api_base=QUBRID_BASE_URL
)

filter_agent = Agent(
    name="content_filter",
    model=qubrid_gpt,
    instruction=FILTER_PROMPT,
)

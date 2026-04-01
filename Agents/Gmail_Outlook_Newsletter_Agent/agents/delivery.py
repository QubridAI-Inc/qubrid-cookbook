"""
agents/delivery.py

Delivery agent: validates that the formatted HTML newsletter is ready
for manual send confirmation in the UI.
"""

from google.adk.agents import Agent  # type: ignore
from google.adk.models.lite_llm import LiteLlm  # type: ignore

from config.settings import QUBRID_MODEL_GPT, QUBRID_API_KEY, QUBRID_BASE_URL, DELIVERY_PROMPT

qubrid_gpt = LiteLlm(
    model=QUBRID_MODEL_GPT,
    api_key=QUBRID_API_KEY,
    api_base=QUBRID_BASE_URL
)

delivery_agent = Agent(
    name="email_delivery",
    model=qubrid_gpt,
    instruction=DELIVERY_PROMPT,
)

"""
agents/research.py

Two research agents run in PARALLEL using ADK's ParallelAgent:
- news_agent_1: searches for latest news and breaking announcements
- news_agent_2: searches for expert analysis and trends

Both fire simultaneously, their outputs are merged, then passed to the Filter.
The rest of the pipeline (Filter → Write → Format → Deliver) remains sequential.
"""

from google.adk.agents import Agent, ParallelAgent  # type: ignore
from google.adk.models.lite_llm import LiteLlm  # type: ignore

from config.settings import QUBRID_MODEL_GPT, QUBRID_API_KEY, QUBRID_BASE_URL, RESEARCH_PROMPT
from tools.search_tools import web_search_tool

qubrid_gpt = LiteLlm(
    model=QUBRID_MODEL_GPT,
    api_key=QUBRID_API_KEY,
    api_base=QUBRID_BASE_URL
)

# ── Two parallel searchers ─────────────────────────────────────────────────────

news_agent_1 = Agent(
    name="news_searcher_1",
    model=qubrid_gpt,
    instruction=RESEARCH_PROMPT + "\n\nFocus on: latest news and breaking announcements.",
    tools=[web_search_tool],
)

news_agent_2 = Agent(
    name="news_searcher_2",
    model=qubrid_gpt,
    instruction=RESEARCH_PROMPT + "\n\nFocus on: expert analysis, opinions, and future trends.",
    tools=[web_search_tool],
)

# ── ParallelAgent — both searchers fire at the same time ──────────────────────

research_agent = ParallelAgent(
    name="research_team",
    sub_agents=[news_agent_1, news_agent_2],
)

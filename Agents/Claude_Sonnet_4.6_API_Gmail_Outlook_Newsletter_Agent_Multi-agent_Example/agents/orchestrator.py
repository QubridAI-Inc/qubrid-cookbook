"""
agents/orchestrator.py

Root SequentialAgent that chains all five pipeline stages:
Research → Filter → Write → Format → Deliver.
This is the entry point for the ADK pipeline.
"""

from google.adk.agents import SequentialAgent  # type: ignore

from agents.research import research_agent
from agents.filter import filter_agent
from agents.writer import writer_agent
from agents.formatter import formatter_agent
from agents.delivery import delivery_agent

root_agent = SequentialAgent(
    name="newsletter_orchestrator",
    sub_agents=[
        research_agent,
        filter_agent,
        writer_agent,
        formatter_agent,
        delivery_agent,
    ],
)

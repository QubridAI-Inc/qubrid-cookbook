"""
ReVive AI — CrewAI agent definitions.

All 6 agents are defined here with roles, goals, and backstories.
Vision agents (historian, analyst, inspector) use QubridVisionLLM.
Reasoning agents (strategist, colorizer) use QubridReasoningLLM.
The restorer agent uses tools directly and needs no LLM call.
"""

from __future__ import annotations

from typing import Any

from crewai import Agent

from config.settings import (
    VISION_MODEL,
    REASONING_MODEL,
    QUBRID_BASE_URL,
    MAX_TOKENS_VISION,
    MAX_TOKENS_REASONING,
    TEMPERATURE_VISION,
    TEMPERATURE_REASONING,
)


# ── Custom LLM wrappers ───────────────────────────────────────────────────────
# CrewAI 0.80+ accepts any callable/object with a `call` method or an LLM
# instance. We use a lightweight wrapper that routes to our backend clients.

class QubridVisionLLM:
    """LLM wrapper routing vision tasks to Qwen3.5-397B-A17B."""

    def __init__(self, model: str = VISION_MODEL) -> None:
        self.model = model

    def call(self, messages: list[dict], **kwargs: Any) -> str:
        """
        Forward a message list to the Qwen vision API.
        Image data must be embedded in the last user message content list.
        Returns raw string response.
        """
        import os
        from openai import OpenAI

        api_key = os.getenv("QUBRID_API_KEY", "")
        client = OpenAI(base_url=QUBRID_BASE_URL, api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=MAX_TOKENS_VISION,
            temperature=TEMPERATURE_VISION,
            stream=False,
        )
        return response.choices[0].message.content or ""


class QubridReasoningLLM:
    """LLM wrapper routing reasoning tasks to Nemotron-120B."""

    def __init__(self, model: str = REASONING_MODEL) -> None:
        self.model = model

    def call(self, messages: list[dict], **kwargs: Any) -> str:
        """Forward a message list to the Nemotron reasoning API."""
        import os
        from openai import OpenAI

        api_key = os.getenv("QUBRID_API_KEY", "")
        client = OpenAI(base_url=QUBRID_BASE_URL, api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=MAX_TOKENS_REASONING,
            temperature=TEMPERATURE_REASONING,
            top_p=0.95,
            stream=False,
        )
        return response.choices[0].message.content or ""


# ── Agent definitions ─────────────────────────────────────────────────────────

def build_agents() -> dict[str, Agent]:
    """Construct and return all 6 ReVive AI agents."""
    from crew.tools import (
        DenoiseImageTool,
        ContrastEnhanceTool,
        SharpenImageTool,
        InpaintRegionTool,
        ColorCorrectTool,
        ApplyColorizationTool,
        SaveRestoredImageTool,
    )

    vision_llm = QubridVisionLLM()
    reasoning_llm = QubridReasoningLLM()

    restorer_tools = [
        DenoiseImageTool(),
        ContrastEnhanceTool(),
        SharpenImageTool(),
        InpaintRegionTool(),
        ColorCorrectTool(),
        ApplyColorizationTool(),
        SaveRestoredImageTool(),
    ]

    photo_historian = Agent(
        role="Photo Historian",
        goal=(
            "Determine the historical context, era, and cultural setting "
            "of the photograph to guide all downstream agents"
        ),
        backstory=(
            "You are a world-renowned photo historian who has catalogued over "
            "500,000 historical photographs. You can identify an era within a "
            "decade just from composition, attire, and photographic technique. "
            "Your context reports are the foundation of every restoration."
        ),
        verbose=True,
        allow_delegation=False,
    )

    damage_analyst = Agent(
        role="Damage Analyst",
        goal=(
            "Produce a precise, comprehensive damage assessment of the "
            "photograph informed by its historical context"
        ),
        backstory=(
            "You are a senior conservator from the Library of Congress with "
            "20 years of photographic damage assessment. You see damage others "
            "miss — the faint scratch, the subtle yellowing, the microscopic tear."
        ),
        verbose=True,
        allow_delegation=False,
    )

    restoration_strategist = Agent(
        role="Restoration Strategist",
        goal=(
            "Create a precise, technically accurate restoration brief that the "
            "Image Restorer can execute step by step"
        ),
        backstory=(
            "You are a master restoration engineer trained at the Getty "
            "Conservation Institute. You translate damage reports into flawless "
            "technical restoration briefs. Your instructions are so precise that "
            "automated systems execute them perfectly."
        ),
        verbose=True,
        allow_delegation=False,
    )

    image_restorer = Agent(
        role="Image Restorer",
        goal=(
            "Execute the restoration brief precisely using available image "
            "processing tools"
        ),
        backstory=(
            "You are a digital restoration technician who executes restoration "
            "plans with surgical precision using PIL and OpenCV tools. You follow "
            "the strategist's brief exactly."
        ),
        verbose=True,
        allow_delegation=False,
        tools=restorer_tools,
    )

    colorization_specialist = Agent(
        role="Colorization Specialist",
        goal=(
            "Apply historically accurate, emotionally resonant colorization "
            "to black and white photographs"
        ),
        backstory=(
            "You studied under the world's best photo colorization artists. "
            "You have colorized over 10,000 historical photographs for museums "
            "and archives. Your colorizations are indistinguishable from original "
            "color photography."
        ),
        verbose=True,
        allow_delegation=False,
    )

    qa_inspector = Agent(
        role="QA Inspector",
        goal=(
            "Objectively evaluate the restoration quality by comparing original "
            "and restored images, scoring and approving the result"
        ),
        backstory=(
            "You are the final gatekeeper at a prestigious photo archive. "
            "Nothing leaves your lab below a 75/100 quality score. You have an "
            "eagle eye for restoration artifacts, color bleeding, and unnatural edits."
        ),
        verbose=True,
        allow_delegation=False,
    )

    return {
        "historian": photo_historian,
        "analyst": damage_analyst,
        "strategist": restoration_strategist,
        "restorer": image_restorer,
        "colorizer": colorization_specialist,
        "inspector": qa_inspector,
    }

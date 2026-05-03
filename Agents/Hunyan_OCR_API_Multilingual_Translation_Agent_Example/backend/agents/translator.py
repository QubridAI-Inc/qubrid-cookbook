"""
Translation agent using Agno.
Explicitly configured with Qubrid GPT-OSS-20B model.
"""
from agno.agent import Agent
from backend.llm.agno_qubrid_model import QubridModel


def create_translation_agent() -> Agent:
    """
    Create an Agno agent for translation.
    
    Uses Qubrid's GPT-OSS-20B model with explicit configuration.
    No implicit OpenAI dependencies.
    
    Returns:
        Configured Agno Agent
    """
    # Use custom Qubrid model wrapper
    qubrid_model = QubridModel(
        id="openai/gpt-oss-20b",
    )
    
    return Agent(
        name="Translation Specialist",
        model=qubrid_model,
        instructions=[
            "You are a professional translator.",
            "Translate the given text to the specified target language.",
            "Return ONLY the translated text.",
            "Preserve the original meaning and tone.",
            "Do not add explanations or notes.",
        ],
        markdown=False,
        debug_mode=True,  # Enable Agno execution logs
        stream=True,  # Enable streaming for proper response handling
    )



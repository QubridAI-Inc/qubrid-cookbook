"""
Language detection agent using Agno.
Explicitly configured with Qubrid GPT-OSS-20B model.
"""
from agno.agent import Agent
from backend.llm.agno_qubrid_model import QubridModel


def create_language_detection_agent() -> Agent:
    """
    Create an Agno agent for language detection.
    
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
        name="Language Detection Specialist",
        model=qubrid_model,
        instructions=[
            "You are a language detection specialist.",
            "Identify the language of the given text.",
            "Return ONLY the language name (e.g., 'English', 'Spanish', 'French').",
            "Do not provide explanations or additional information.",
        ],
        markdown=False,
        debug_mode=True,  # Enable Agno execution logs
        stream=True,  # Enable streaming for proper response handling
    )



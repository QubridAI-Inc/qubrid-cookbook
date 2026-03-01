from typing import TypedDict, Optional

class AgentState(TypedDict):
    session_id: str
    user_prompt: str
    style_preset: Optional[str]  # New: e.g., "Cinematic", "Anime"
    aspect_ratio: Optional[str]  # New: e.g., "16:9", "1:1"
    generated_image_url: Optional[str]
    error: Optional[str]
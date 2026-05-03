from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    audio_path:          str
    raw_response:        Dict[str, Any]
    transcript_segments: List[Dict[str, Any]]
    chapters:            List[Dict[str, Any]]
    episode_brief:       str
    key_moments:         List[Dict[str, Any]]
    energy_map:          List[Dict[str, Any]]
    topics:              List[Dict[str, Any]]
    status:              str

    # ── Agentic fields ────────────────────────────────────────────────────────
    audio_mode:          str          # "full" | "short_clip" — set by quality gate
    chapter_retries:     int          # how many times chapter_gen has been retried
    quality_flags:       List[str]    # warnings surfaced to the user
    confidence_scores:   Dict[str, Any]  # per-section confidence from self-eval node
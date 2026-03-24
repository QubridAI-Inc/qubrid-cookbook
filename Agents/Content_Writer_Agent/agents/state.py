"""
Shared state schema for all ToneCraft LangGraph agents.
All fields are optional (total=False) — nodes only return the fields they update.
"""

from typing import TypedDict


class ToneCraftState(TypedDict, total=False):
    # Input
    original_text: str
    target_tone: str

    # Analysis (from analyze_intent + recommend_tones nodes)
    content_type: str        # email, article, tweet, linkedin_post, report, other
    detected_tone: str       # casual, formal, neutral, aggressive, diplomatic, etc.
    recommended_tones: list  # [{"tone": "🎯 Executive", "reason": "..."}]

    # Rewrite loop
    draft_rewrite: str
    rewrite_attempt: int
    quality_score: float
    quality_issues: list     # specific problems found by quality checker

    # Final output
    final_rewrite: str
    explanation: str

    # Multi-turn chat
    messages: list           # [{"role": "user"|"assistant", "content": "..."}]

    # Accumulated stats across all agent calls
    total_tokens: int
    total_latency_ms: float
    agent_trace: list        # ["analyzed", "recommended", "rewritten", ...]

    # Error
    error: str

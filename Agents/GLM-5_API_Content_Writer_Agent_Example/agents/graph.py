"""
LangGraph graph definitions for ToneCraft AI.

Exports:
    rewrite_graph  — full pipeline: analyze → recommend → rewrite → quality_check → (refine?) → explain
    chat_graph     — single-node graph for follow-up refinements
"""

from langgraph.graph import END, START, StateGraph

from agents.nodes import (
    analyze_intent,
    check_quality,
    explain,
    recommend_tones,
    refine,
    rewrite,
    chat,
    should_refine,
)
from agents.state import ToneCraftState

# ── Analysis-only graph (fast pre-pass before user sees streaming) ────────────
_ab = StateGraph(ToneCraftState)
_ab.add_node("analyze_intent", analyze_intent)
_ab.add_node("recommend_tones", recommend_tones)
_ab.add_edge(START, "analyze_intent")
_ab.add_edge("analyze_intent", "recommend_tones")
_ab.add_edge("recommend_tones", END)
analysis_graph = _ab.compile()

# ── Rewrite graph ─────────────────────────────────────────────────────────────
_rb = StateGraph(ToneCraftState)

_rb.add_node("analyze_intent", analyze_intent)
_rb.add_node("recommend_tones", recommend_tones)
_rb.add_node("rewrite", rewrite)
_rb.add_node("check_quality", check_quality)
_rb.add_node("refine", refine)
_rb.add_node("explain", explain)

_rb.add_edge(START, "analyze_intent")
_rb.add_edge("analyze_intent", "recommend_tones")
_rb.add_edge("recommend_tones", "rewrite")
_rb.add_edge("rewrite", "check_quality")
_rb.add_conditional_edges(
    "check_quality",
    should_refine,
    {"refine": "refine", "explain": "explain"},
)
_rb.add_edge("refine", "check_quality")
_rb.add_edge("explain", END)

rewrite_graph = _rb.compile()

# ── Chat graph ────────────────────────────────────────────────────────────────
_cb = StateGraph(ToneCraftState)

_cb.add_node("chat", chat)
_cb.add_edge(START, "chat")
_cb.add_edge("chat", END)

chat_graph = _cb.compile()

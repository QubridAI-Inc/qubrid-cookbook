from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.nodes import (
    transcribe_node,
    format_segments_node,
    generate_chapters_node,
    generate_chapters_retry_node,
    generate_brief_node,
    extract_key_moments_node,
    analyze_energy_node,
    extract_topics_node,
    quality_gate_node,
    chapter_quality_check_node,
    self_evaluate_node,
)

# ── Routing functions (conditional edges) ─────────────────────────────────────

def route_after_quality_gate(state: AgentState) -> str:
    """
    Agentic branch 1: quality gate decides the analysis path.
    Short clips skip chapters/energy and go straight to key moments + brief.
    """
    if state.get("audio_mode") == "short_clip":
        return "short_clip_path"
    return "full_path"

def route_after_chapter_check(state: AgentState) -> str:
    """
    Agentic branch 2: if chapters are empty and retries remain, loop back.
    Otherwise continue to energy analysis.
    """
    chapters = state.get("chapters", [])
    retries  = state.get("chapter_retries", 0)
    if not chapters and retries <= 1:
        return "retry_chapters"
    return "continue"

# ── Build graph ────────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(AgentState)

    # Core nodes
    g.add_node("transcriber",       transcribe_node)
    g.add_node("formatter",         format_segments_node)
    g.add_node("quality_gate",      quality_gate_node)           # AGENTIC A

    # Full path nodes
    g.add_node("chapter_gen",       generate_chapters_node)
    g.add_node("chapter_check",     chapter_quality_check_node)  # AGENTIC B
    g.add_node("chapter_retry",     generate_chapters_retry_node)
    g.add_node("energy_gen",        analyze_energy_node)
    g.add_node("key_moments_gen",   extract_key_moments_node)
    g.add_node("topics_gen",        extract_topics_node)
    g.add_node("brief_gen",         generate_brief_node)
    g.add_node("self_evaluate",     self_evaluate_node)          # AGENTIC C

    g.set_entry_point("transcriber")

    # Linear: transcribe → format → quality gate
    g.add_edge("transcriber", "formatter")
    g.add_edge("formatter",   "quality_gate")

    # Conditional branch A: quality gate routes to full or short clip
    g.add_conditional_edges(
        "quality_gate",
        route_after_quality_gate,
        {
            "full_path":       "chapter_gen",
            "short_clip_path": "key_moments_gen",   # skip chapters/energy for short audio
        }
    )

    # Full path: chapters → self-correction check
    g.add_edge("chapter_gen", "chapter_check")

    # Conditional branch B: retry chapters if quality too low
    g.add_conditional_edges(
        "chapter_check",
        route_after_chapter_check,
        {
            "retry_chapters": "chapter_retry",
            "continue":       "energy_gen",
        }
    )
    g.add_edge("chapter_retry",   "energy_gen")   # after retry, continue normally
    g.add_edge("energy_gen",      "key_moments_gen")
    g.add_edge("key_moments_gen", "topics_gen")
    g.add_edge("topics_gen",      "brief_gen")
    g.add_edge("brief_gen",       "self_evaluate")  # AGENTIC C: evaluate before END
    g.add_edge("self_evaluate",   END)

    return g.compile()

app_graph = build_graph()
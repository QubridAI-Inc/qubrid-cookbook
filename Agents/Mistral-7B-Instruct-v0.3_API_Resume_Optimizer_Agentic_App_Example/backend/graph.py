"""LangGraph workflow for resume optimization."""

from langgraph.graph import StateGraph, END
from backend.state import ResumeState
from backend.nodes import (
    analyze_job_description,
    critique_resume,
    draft_suggestions_only,
    draft_tailored_resume,
    finalize_resume
)


def should_continue_iterating(state: ResumeState) -> str:
    """
    Decide whether to iterate or finalize.
    
    Returns: 'finalize' or 'draft'
    """
    critique = state.get("critique", {})
    iteration = state.get("iteration", 0)
    
    # Stop if max iterations reached
    if iteration >= 3:
        return "finalize"
    
    # Stop if approved
    if critique.get("approved", False):
        return "finalize"
    
    # Continue iterating
    return "draft"


def create_resume_workflow():
    """
    Create the resume optimization workflow graph.
    
    Workflow:
    analyze_jd → critique_original → suggest → END (wait for user)
    
    After user approval:
    draft → critique_draft → (iterate if needed) → finalize → END
    """
    graph = StateGraph(ResumeState)
    
    # Add nodes
    graph.add_node("analyze_jd", analyze_job_description)
    graph.add_node("critique_original", critique_resume)
    graph.add_node("suggest", draft_suggestions_only)
    graph.add_node("draft", draft_tailored_resume)
    graph.add_node("critique_draft", critique_resume)
    graph.add_node("finalize", finalize_resume)
    
    # First half: evaluation
    graph.set_entry_point("analyze_jd")
    graph.add_edge("analyze_jd", "critique_original")
    graph.add_edge("critique_original", "suggest")
    graph.add_edge("suggest", END)  # Pause for user approval
    
    # Second half: generation (after user clicks "Generate")
    graph.add_edge("draft", "critique_draft")
    
    # Conditional: iterate or finalize?
    graph.add_conditional_edges(
        "critique_draft",
        should_continue_iterating,
        {
            "finalize": "finalize",
            "draft": "draft"
        }
    )
    
    graph.add_edge("finalize", END)
    
    return graph.compile()
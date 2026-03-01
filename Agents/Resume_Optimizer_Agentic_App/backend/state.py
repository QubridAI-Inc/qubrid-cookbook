"""State definition for LangGraph resume tailoring workflow."""

from typing import TypedDict, Optional, Dict, List, Any


class ResumeState(TypedDict, total=False):
    """State object passed through the LangGraph workflow."""

    # Input data
    original_resume: str
    job_description: str
    resume_filename: str
    jd_source: str

    # Analysis outputs
    jd_analysis: Dict[str, Any]

    # NEW: Suggestions before full rewrite
    suggestions: List[Dict[str, str]]
    awaiting_approval: bool

    # Generation outputs
    draft_resume: str
    critique: Dict[str, Any]

    # Loop control
    iteration: int

    # Final outputs
    final_resume: str
    output_markdown: str
    output_pdf_path: str

    # Metadata
    metadata: Dict[str, Any]

    # Error handling
    error: Optional[str]
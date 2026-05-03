"""
Parser utilities for splitting, cleaning, and measuring reasoning/answer text.
"""
import re
import math

def clean_reasoning(raw: str) -> str:
    """
    Strip any leading/trailing whitespace, normalize multiple newlines to double,
    remove any <think> tags if present in the raw content.
    """
    if not raw:
        return ""
    
    # Remove <think> and </think> tags if present
    cleaned = re.sub(r'</?think>', '', raw, flags=re.IGNORECASE)
    
    # Normalize multiple newlines to double newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Remove consecutive duplicate paragraphs (model loop repetition)
    paragraphs = cleaned.split('\n\n')
    deduped = []
    for para in paragraphs:
        stripped = para.strip()
        if not stripped:
            continue
        if deduped and stripped.lower() == deduped[-1].lower():
            continue
        deduped.append(stripped)
    cleaned = '\n\n'.join(deduped)

    return cleaned.strip()


def clean_answer(raw: str) -> str:
    """
    Strip whitespace. If answer starts with "Final Answer:" or similar prefix,
    keep it. Return clean string.
    """
    if not raw:
        return ""
    
    cleaned = raw.strip()
    return cleaned


def count_reasoning_steps(reasoning: str) -> int:
    """
    Count logical steps by counting numbered patterns (1., 2., Step 1, etc.)
    or paragraph breaks. Returns estimated step count.
    """
    if not reasoning:
        return 0
    
    # Check for explicit numbered lists (e.g., "1.", "Step 1:")
    step_patterns = re.findall(r'(?m)^(?:\d+\.|Step\s+\d+:?|-|\*)\s+', reasoning, flags=re.IGNORECASE)
    if step_patterns and len(step_patterns) > 1:
        return len(step_patterns)
    
    # Fallback: estimate by paragraphs
    paragraphs = [p for p in reasoning.split('\n\n') if p.strip()]
    return len(paragraphs)


def estimate_reading_time(text: str) -> str:
    """
    Returns human-friendly string like "~2 min read" based on word count.
    Assumes average adult reading speed of ~238 words per minute.
    """
    if not text:
        return "~1 min read"
        
    word_count = len(text.split())
    minutes = math.ceil(word_count / 238)
    return f"~{minutes} min read"

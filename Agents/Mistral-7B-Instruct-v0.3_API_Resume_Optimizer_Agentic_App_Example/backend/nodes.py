"""AI processing nodes for resume optimization workflow."""

import json
import re
import time
import os
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

from backend.state import ResumeState
from backend.prompts import (
    JD_ANALYSIS_PROMPT,
    CRITIQUE_PROMPT,
    SUGGESTIONS_PROMPT,
    TAILORING_PROMPT,
    FINALIZATION_PROMPT
)

# Load environment variables
load_dotenv()

# API Configuration
QUBRID_API_KEY = os.getenv("QUBRID_API_KEY", "")
QUBRID_BASE_URL = os.getenv("QUBRID_BASE_URL", "https://platform.qubrid.com/v1")
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
MAX_TOKENS = 8192


# ===== HELPER FUNCTIONS =====


def call_llm_with_retry(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_retries: int = 3
) -> str:
    """
    Call Qubrid API with retry logic.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0=deterministic, 1=creative)
        max_retries: Maximum number of retry attempts
        
    Returns:
        Response text from the model
    """
    client = OpenAI(
        api_key=QUBRID_API_KEY,
        base_url=QUBRID_BASE_URL
    )
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=MAX_TOKENS,
                timeout=60
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"API call failed: {str(e)}")


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text that might have markdown code blocks."""
    # Try to find JSON in code blocks
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    
    # Try to find raw JSON
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    
    raise ValueError("No valid JSON found in response")


def analyze_job_description(state: ResumeState) -> ResumeState:
    """
    Extract structured information from job description.
    
    Returns: Updated state with jd_analysis
    """
    try:
        prompt = JD_ANALYSIS_PROMPT.format(
            job_description=state["job_description"]
        )
        
        messages = [{"role": "user", "content": prompt}]
        response = call_llm_with_retry(messages, temperature=0.3)
        
        # Parse JSON response
        try:
            jd_analysis = json.loads(response)
        except json.JSONDecodeError:
            jd_analysis = extract_json_from_text(response)
        
        return {**state, "jd_analysis": jd_analysis}
        
    except Exception as e:
        # Return state with error and fallback values
        return {
            **state,
            "jd_analysis": {
                "job_title": "Unknown",
                "company": "Unknown",
                "required_skills": [],
                "key_responsibilities": [],
                "ats_keywords": []
            },
            "error": f"JD Analysis failed: {str(e)}"
        }


def critique_resume(state: ResumeState) -> ResumeState:
    """
    Score resume against job requirements.
    
    Returns: Updated state with critique scores
    """
    try:
        # Determine which resume to score
        resume_to_score = state.get("draft_resume") or state["original_resume"]
        
        # Get JD analysis
        jd_analysis = state.get("jd_analysis", {})
        
        prompt = CRITIQUE_PROMPT.format(
            resume=resume_to_score,
            job_requirements=json.dumps(jd_analysis, indent=2)
        )
        
        messages = [{"role": "user", "content": prompt}]
        response = call_llm_with_retry(messages, temperature=0.1)
        
        # Parse JSON response
        try:
            critique = json.loads(response)
        except json.JSONDecodeError:
            critique = extract_json_from_text(response)
        
        # Add approval flag
        overall_score = critique.get("overall_score", 0)
        critique["approved"] = overall_score >= 8.5
        
        return {**state, "critique": critique}
        
    except Exception as e:
        # Return state with error and fallback critique
        return {
            **state,
            "critique": {
                "overall_score": 0,
                "keyword_score": 0,
                "experience_score": 0,
                "ats_score": 0,
                "formatting_score": 0,
                "feedback": f"Critique failed: {str(e)}",
                "improvements_needed": [],
                "approved": False
            },
            "error": f"Critique failed: {str(e)}"
        }


def draft_suggestions_only(state: ResumeState) -> ResumeState:
    """
    Generate improvement suggestions without rewriting resume.
    
    Returns: Updated state with suggestions list
    """
    try:
        jd_analysis = state.get("jd_analysis", {})
        critique = state.get("critique", {})
        
        prompt = SUGGESTIONS_PROMPT.format(
            original_resume=state["original_resume"],
            job_requirements=json.dumps(jd_analysis, indent=2),
            critique_scores=json.dumps(critique, indent=2)
        )
        
        messages = [{"role": "user", "content": prompt}]
        response = call_llm_with_retry(messages, temperature=0.6)
        
        # Parse JSON response
        try:
            suggestions_data = json.loads(response)
            suggestions = suggestions_data.get("suggestions", [])
        except json.JSONDecodeError:
            suggestions_data = extract_json_from_text(response)
            suggestions = suggestions_data.get("suggestions", [])
        
        return {
            **state,
            "suggestions": suggestions,
            "awaiting_approval": True
        }
        
    except Exception as e:
        return {
            **state,
            "suggestions": [],
            "awaiting_approval": True,
            "error": f"Suggestions generation failed: {str(e)}"
        }


def draft_tailored_resume(state: ResumeState) -> ResumeState:
    """
    Rewrite resume to match job requirements.
    
    Returns: Updated state with draft_resume
    """
    try:
        jd_analysis = state.get("jd_analysis", {})
        suggestions = state.get("suggestions", [])
        
        # Format suggestions as text
        suggestions_text = "\n".join([
            f"- {s.get('category', 'General')}: {s.get('suggestion', '')}"
            for s in suggestions
        ])
        
        prompt = TAILORING_PROMPT.format(
            original_resume=state["original_resume"],
            job_requirements=json.dumps(jd_analysis, indent=2),
            suggestions=suggestions_text,
            iteration=state.get("iteration", 0)
        )
        
        messages = [
            {"role": "system", "content": "You are an expert resume writer."},
            {"role": "user", "content": prompt}
        ]
        
        response = call_llm_with_retry(messages, temperature=0.7)
        
        # Increment iteration
        iteration = state.get("iteration", 0) + 1
        
        return {
            **state,
            "draft_resume": response,
            "iteration": iteration
        }
        
    except Exception as e:
        return {
            **state,
            "draft_resume": state["original_resume"],
            "error": f"Resume drafting failed: {str(e)}"
        }


def finalize_resume(state: ResumeState) -> ResumeState:
    """
    Polish and finalize the resume.
    
    Returns: Updated state with final_resume
    """
    try:
        draft = state.get("draft_resume", state["original_resume"])
        
        prompt = FINALIZATION_PROMPT.format(resume=draft)
        
        messages = [{"role": "user", "content": prompt}]
        response = call_llm_with_retry(messages, temperature=0.5)
        
        return {
            **state,
            "final_resume": response,
            "output_markdown": response
        }
        
    except Exception as e:
        # Fallback to draft resume
        draft = state.get("draft_resume", state["original_resume"])
        return {
            **state,
            "final_resume": draft,
            "output_markdown": draft,
            "error": f"Finalization failed: {str(e)}"
        }
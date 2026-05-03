"""AI prompts for resume optimization."""

JD_ANALYSIS_PROMPT = """
Analyze this job description and extract key information.

Job Description:
{job_description}

Return ONLY a JSON object with these exact keys:
{{
    "job_title": "the job title",
    "company": "company name",
    "required_skills": ["skill1", "skill2", "skill3"],
    "key_responsibilities": ["responsibility1", "responsibility2"],
    "ats_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

CRITIQUE_PROMPT = """
Score this resume against the job requirements.

Resume:
{resume}

Job Requirements:
{job_requirements}

Return ONLY a JSON object:
{{
    "overall_score": 8.5,
    "keyword_score": 9,
    "experience_score": 8,
    "ats_score": 9,
    "formatting_score": 8,
    "feedback": "detailed feedback here",
    "improvements_needed": ["improvement1", "improvement2"]
}}
"""

SUGGESTIONS_PROMPT = """
Generate specific improvement suggestions for this resume.

Original Resume:
{original_resume}

Job Requirements:
{job_requirements}

Current Scores:
{critique_scores}

Return ONLY a JSON object:
{{
    "suggestions": [
        {{"category": "Keywords", "suggestion": "Add Python, AWS, Docker"}},
        {{"category": "Experience", "suggestion": "Highlight project X"}}
    ]
}}
"""

TAILORING_PROMPT = """
Rewrite this resume to match the job requirements. Keep all information factual.

Original Resume:
{original_resume}

Job Requirements:
{job_requirements}

Apply These Suggestions:
{suggestions}

Return the improved resume in Markdown format.
"""

FINALIZATION_PROMPT = """
Polish and finalize this resume. Fix any formatting issues.

Resume:
{resume}

Return the final version in clean Markdown format.
"""
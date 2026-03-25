"""
ReVive AI — Global settings, constants, and prompt templates.
All configuration lives here; never hard-code values elsewhere.
"""

import os

# ── API ──────────────────────────────────────────────────────────────────────
QUBRID_BASE_URL: str = "https://platform.qubrid.com/v1"
VISION_MODEL: str = "Qwen/Qwen3.5-397B-A17B"
REASONING_MODEL: str = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8"

MAX_TOKENS_VISION: int = 2048
MAX_TOKENS_REASONING: int = 4096
TEMPERATURE_VISION: float = 0.3
TEMPERATURE_REASONING: float = 0.6

# ── App branding ──────────────────────────────────────────────────────────────
APP_NAME: str = "ReVive AI"
APP_TAGLINE: str = "From faded to vivid."
APP_SUB_TAGLINE: str = "Every photo deserves a second life."
BRAND_LINE: str = (
    "Restored by Nemotron · Seen by Qwen3.5-397B · Powered by Qubrid AI"
)

# ── Paths ─────────────────────────────────────────────────────────────────────
DB_PATH: str = "database/revive.db"
OUTPUTS_DIR: str = "outputs/"

# ── Pipeline control ──────────────────────────────────────────────────────────
QA_RETRY_THRESHOLD: int = 60
MAX_RETRIES: int = 2

# ── File validation ───────────────────────────────────────────────────────────
SUPPORTED_FORMATS: list[str] = ["jpg", "jpeg", "png", "webp", "bmp", "tiff"]
MAX_FILE_SIZE_MB: int = 15

# ── Agent display names ───────────────────────────────────────────────────────
AGENT_NAMES: dict[str, str] = {
    "historian":  "Photo Historian",
    "analyst":    "Damage Analyst",
    "strategist": "Restoration Strategist",
    "restorer":   "Image Restorer",
    "colorizer":  "Colorization Specialist",
    "inspector":  "QA Inspector",
}

# ── System prompts ────────────────────────────────────────────────────────────

HISTORIAN_PROMPT: str = """
You are an expert photo historian and cultural analyst with deep knowledge
of photographic history from 1850 to 2000.

Examine this photograph carefully and return ONLY a valid JSON object:
{
  "estimated_era": "e.g. 1940s-1950s",
  "photo_type": "e.g. wedding portrait / street scene / family gathering",
  "setting": "e.g. indoor studio / outdoor / home",
  "is_black_and_white": true or false,
  "subjects": "brief description of people/objects",
  "film_type": "e.g. silver gelatin / kodachrome / daguerreotype",
  "historical_context": "2-3 sentence cultural/historical context",
  "colorization_hints": {
    "skin_tone": "hex or description",
    "clothing": "color descriptions",
    "background": "color description",
    "notable_elements": "any other color hints"
  },
  "confidence": "high / medium / low"
}
Return ONLY the JSON. No explanation, no markdown.
"""

ANALYST_PROMPT: str = """
You are a senior photo forensics expert specializing in damage assessment.
You have been given historical context about this photo: {historical_context}

Examine this photograph and return ONLY a valid JSON object:
{{
  "damage_types": ["list of: scratches, tears, fading, noise, stains,
                    missing_regions, discoloration, blur, water_damage"],
  "severity": "mild / moderate / severe",
  "affected_regions": ["top-left", "center", etc],
  "color_issues": "description of color problems if any",
  "structural_issues": "tears, missing parts description",
  "noise_level": "low / medium / high",
  "contrast_status": "description",
  "restoration_priority": ["ordered list of most critical fixes"],
  "special_considerations": "any era-specific restoration notes"
}}
Return ONLY the JSON. No explanation, no markdown.
"""

STRATEGIST_PROMPT: str = """
You are a master photo restoration and enhancement engineer at a world-class archive lab.

Historical context: {historical_context}
Damage report: {damage_report}

Available operations and their parameters:
- denoise: {{h: 1-4}} — NL-means noise removal (color photos)
- denoise_bw: {{h: 1-7}} — NL-means for B&W/grayscale
- contrast_clahe: {{clipLimit: 0.5-1.5, tileGridSize: 4-16}} — adaptive local contrast
- sharpen: {{amount: 0.1-0.6, sigma: 0.5-2.0}} — unsharp mask
- color_correct: {{color: 0.9-1.3, contrast: 0.9-1.2, brightness: 0.9-1.15}} — PIL enhance
- gamma_correct: {{gamma: 0.8-1.4}} — gamma curve
- fade_restore: {{blend: 0.1-0.4}} — histogram-based fade lift (L channel only)
- inpaint: {{inpaintRadius: 1-5}} — fill scratches/tears
- scratch_remove: {{inpaintRadius: 1-5}} — morphological scratch detection + inpaint
- shadows_highlights: {{shadows: 0.0-0.5, highlights: 0.0-0.4}} — lift shadows, recover highlights
- clarity: {{amount: 0.1-0.6}} — local contrast / crispness boost via Laplacian
- enhance: {{strength: 0.2-0.9, sigma_s: 5-20, sigma_r: 0.05-0.25}} — detail enhance + vibrance

IMPORTANT: Always include 'clarity' and 'enhance' as the LAST two steps in your plan.
They produce clearly visible improvement on any photo. For modern/mild photos, skip
denoise and use only: shadows_highlights → color_correct → clarity → enhance.

Create a precise restoration brief. Return ONLY valid JSON:
{{
  "restoration_steps": [
    {{
      "step": 1,
      "operation": "operation_name",
      "parameters": {{"param": "value"}},
      "region": "full_image",
      "reason": "why this step"
    }}
  ],
  "estimated_improvement": "percentage estimate",
  "colorization_required": true or false,
  "colorization_plan": {{
    "region_name": {{"color": "hex", "blend_mode": "normal/soft_light"}}
  }},
  "processing_order": "sequential",
  "special_instructions": "any critical notes"
}}
Return ONLY the JSON. No explanation, no markdown.
"""

COLORIZER_PROMPT: str = """
You are a world-renowned photo colorization specialist with expertise in
historical accuracy and period-correct color palettes.

Historical context: {historical_context}
Colorization hints: {colorization_hints}
Restoration brief: {restoration_brief}

Create a detailed colorization plan. Return ONLY a valid JSON:
{{
  "colorization_regions": [
    {{
      "region": "region description",
      "base_color": "#hexcode",
      "shadow_color": "#hexcode",
      "highlight_color": "#hexcode",
      "blend_strength": 0.6,
      "historical_justification": "why this color"
    }}
  ],
  "global_adjustments": {{
    "warmth": 10,
    "saturation": 60,
    "color_temperature": "warm/neutral/cool"
  }},
  "technique": "description of colorization approach",
  "confidence": "high/medium/low"
}}
Return ONLY the JSON. No explanation, no markdown.
"""

QA_PROMPT: str = """
You are a senior quality control expert at a prestigious photo archive.

You are comparing the ORIGINAL damaged photo (first image) with the
RESTORED version (second image).

Evaluate the restoration and return ONLY a valid JSON object:
{{
  "restoration_score": 75,
  "improvements_detected": ["list of successful fixes"],
  "remaining_issues": ["list of any remaining problems"],
  "colorization_quality": "excellent/good/fair/poor or N/A",
  "historical_accuracy": "excellent/good/fair/poor",
  "verdict": "APPROVED / NEEDS_RETRY",
  "summary": "2-3 sentence overall assessment",
  "recommendation": "any final suggestions"
}}
Score guide: 90-100=Excellent, 75-89=Good, 60-74=Fair, <60=Retry needed.
Return ONLY the JSON. No explanation, no markdown.
"""

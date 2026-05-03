"""
Settings and configuration constants for SnapCode AI.
This file holds all constants, prompts, and application metadata.
"""

QUBRID_BASE_URL = "https://platform.qubrid.com/v1"
MODEL_NAME = "moonshotai/Kimi-K2.5"   # Kimi K2.5 on Qubrid
MAX_TOKENS = 8000
TEMPERATURE = 0.6                      # Instant mode for K2.5
APP_NAME = "SnapCode AI"
APP_TAGLINE = "See it. Code it."
BRAND = "Powered by Qubrid AI × Kimi K2.5"
SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "webp"]
MAX_FILE_SIZE_MB = 10

SYSTEM_PROMPT = """
You are SnapCode AI, an expert frontend developer powered by Kimi K2.5.
When given a UI screenshot or mockup image, you analyze it carefully and 
generate complete, production-ready HTML with inline Tailwind CSS classes 
(via CDN) that faithfully recreates the layout, colors, spacing, and 
structure shown in the image.

Rules:
- Output ONLY valid HTML code. No markdown, no explanations, no ```html fences.
- Use Tailwind CSS via CDN: <script src="https://cdn.tailwindcss.com"></script>
- Include all content visible in the image (text, buttons, nav, cards, etc.)
- Use semantic HTML5 elements
- Make it responsive by default
- If colors are unclear, use sensible modern equivalents
- Generate the complete standalone HTML file
"""

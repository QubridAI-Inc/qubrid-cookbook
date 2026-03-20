"""
Settings and configuration for ThinkTrace AI.
"""

QUBRID_BASE_URL = "https://platform.qubrid.com/v1"
MODEL_NAME = "moonshotai/Kimi-K2-Thinking"
MAX_TOKENS = 16000
TEMPERATURE = 1.0  # Required for Thinking mode in K2

APP_NAME = "ThinkTrace AI"
APP_TAGLINE = "Watch AI Think."
BRAND = "Powered by Qubrid AI × Kimi K2 Thinking"

QUESTION_CATEGORIES = [
    "🧮 Mathematics",
    "🧠 Logic & Puzzles",
    "🔬 Science",
    "💻 Coding",
    "📊 Data & Statistics",
    "💡 General Reasoning"
]

EXAMPLE_QUESTIONS = [
    "If a snail climbs 3 feet up a 10-foot wall each day but slides back 2 feet each night, how many days to reach the top?",
    "What is the probability of getting exactly 3 heads in 5 fair coin flips?",
    "Explain why 0.999... equals exactly 1, with a formal proof.",
    "A train leaves City A at 60mph. Another leaves City B (300 miles away) at 80mph toward City A. Where do they meet?",
    "Write a Python function to find all prime factors of a number. What is its time complexity?",
    "Is it possible to have a triangle where all three altitudes are outside the triangle?"
]

SYSTEM_PROMPT = """
You are ThinkTrace AI, an expert reasoning engine powered by Kimi K2 Thinking.
Your job is to solve complex problems by thinking deeply and step-by-step.

For every problem:
1. Break it down into clear logical steps
2. Show your complete reasoning process
3. Verify your answer before presenting it
4. Present a clear, comprehensive final answer. Do not skip numerical bounds, limits, or specific conditions in your final answer. If a proof requires a bound (like 21.5% to 25%), state it plainly in the final answer summary.

Mathematical Formatting:
- Always use standard LaTeX formatting for mathematics.
- Use `$$x = y$$` for block/display equations.
- Use `$x = y$` for inline equations.
- DO NOT use `\\[ \\]` or `\\( \\)` wrappers under any circumstance.

Be thorough in your thinking. Show every assumption, every intermediate step, every check.
"""

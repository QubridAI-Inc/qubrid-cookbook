import os
import json
import requests
from openai import OpenAI
from backend.state import AgentState
from config.settings import config

def _llm(prompt: str) -> str:
    """Single reusable LLM call via OpenAI-compatible client."""
    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.API_KEY)
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.7,
    )
    return response.choices[0].message.content

def _transcript_text(segments: list) -> str:
    return "\n".join(f"[{s['timestamp']}] {s['text']}" for s in segments)

def _safe_json(raw: str) -> list:
    """Strips markdown fences the LLM sometimes adds, then parses JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0].strip()
    return json.loads(raw)


# ── Node 1: Whisper ────────────────────────────────────────────────────────────

def transcribe_node(state: AgentState) -> dict:
    """Calls Whisper API. Returns raw verbose_json with segment timestamps."""
    try:
        with open(state["audio_path"], "rb") as f:
            response = requests.post(
                config.WHISPER_URL,
                headers={"Authorization": f"Bearer {config.API_KEY}"},
                files={"file": (os.path.basename(state["audio_path"]), f, "audio/wav")},
                data={
                    "model": config.WHISPER_MODEL,
                    "response_format": "verbose_json",
                    "timestamp_granularities[]": "segment"
                }
            )
        if response.status_code != 200:
            return {"status": f"Whisper Error: {response.text}"}
        return {"raw_response": response.json(), "status": "Transcribed"}
    except Exception as e:
        return {"status": f"Error: {str(e)}"}


# ── Node 2: Formatter ──────────────────────────────────────────────────────────

def format_segments_node(state: AgentState) -> dict:
    """
    Converts raw Whisper segments into readable transcript rows.
    Step 1 — merges micro-fragments into ~30-word sentences.
    Step 2 — deduplicates by word-overlap similarity (catches Whisper hallucination loops).
    """
    segments = state.get("raw_response", {}).get("segments", [])

    if not segments:
        text = state.get("raw_response", {}).get("text", "No speech detected.")
        return {"transcript_segments": [{"timestamp": "00:00", "start": 0, "end": 0, "text": text}]}

    # ── Step 1: merge short fragments into ~30-word chunks ─────────────────────
    merged, bucket_text, bucket_start, bucket_end = [], [], None, None

    for seg in segments:
        text = seg.get("text", "").strip()
        if not text:
            continue
        if bucket_start is None:
            bucket_start = seg.get("start", 0)
        bucket_text.append(text)
        bucket_end = seg.get("end", seg.get("start", 0))

        if sum(len(t.split()) for t in bucket_text) >= 30:
            merged.append({"start": bucket_start, "end": bucket_end, "text": " ".join(bucket_text)})
            bucket_text, bucket_start, bucket_end = [], None, None

    # flush any remaining
    if bucket_text:
        merged.append({"start": bucket_start, "end": bucket_end, "text": " ".join(bucket_text)})

    # ── Step 2: deduplicate — only drop near-identical consecutive chunks ─────────
    # Strategy: compare each chunk only to the immediately preceding one.
    # Two chunks must share >80% of their content words to be considered duplicates.
    # This avoids the false-positive problem of window-based approaches on long audio.
    STOP = {"the","a","an","and","or","but","is","it","in","on","at","to","of",
             "that","this","was","for","with","as","he","she","they","we","i",
             "you","so","just","like","have","be","are","were","has","had","not","do"}

    def _content_sim(a: str, b: str) -> float:
        wa = set(a.lower().split()) - STOP
        wb = set(b.lower().split()) - STOP
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)

    formatted, prev_text = [], ""

    for seg in merged:
        text = seg["text"]
        # Only compare to the single previous segment — no sliding window
        if _content_sim(text, prev_text) > 0.80:
            continue
        prev_text = text

        m, s = divmod(int(seg["start"]), 60)
        formatted.append({
            "timestamp": f"{m:02}:{s:02}",
            "start":     round(seg["start"], 2),
            "end":       round(seg["end"], 2),
            "text":      text
        })
    return {"transcript_segments": formatted, "status": "Formatted"}


# ── Nodes 3–6: Parallel LLM calls (all fan out from formatter) ─────────────────

def generate_chapters_node(state: AgentState) -> dict:
    """Groups transcript into 3–6 titled chapters with timestamps."""
    transcript = _transcript_text(state.get("transcript_segments", []))
    prompt = f"""Analyze this podcast transcript. Identify 3 to 6 key chapters.
Return ONLY a JSON array, no markdown, no extra text.
Format: [{{"title": "...", "timestamp": "MM:SS", "summary": "one sentence"}}]

Transcript:
{transcript}"""
    try:
        return {"chapters": _safe_json(_llm(prompt))}
    except Exception as e:
        return {"chapters": [], "status": f"Chapter Error: {str(e)}"}


def generate_brief_node(state: AgentState) -> dict:
    """Writes a 3-sentence episode brief: what it's about, who it's for, key takeaway."""
    transcript = _transcript_text(state.get("transcript_segments", []))
    prompt = f"""You are writing a podcast description.
Read this transcript and write exactly 3 sentences:
1. What this episode is about.
2. Who it is for.
3. The single most important takeaway.

Return plain text only. No bullet points.

Transcript:
{transcript}"""
    try:
        return {"episode_brief": _llm(prompt).strip()}
    except Exception as e:
        return {"episode_brief": f"Error: {str(e)}"}


def extract_key_moments_node(state: AgentState) -> dict:
    """Finds 4–6 standout moments worth clipping: strong arguments, stats, quotes."""
    transcript = _transcript_text(state.get("transcript_segments", []))
    prompt = f"""You are a podcast producer finding highlight clips.
Identify 4 to 6 key moments from this transcript — strong arguments, surprising stats, or quotable lines.
Return ONLY a JSON array, no markdown, no extra text.
Format: [{{"timestamp": "MM:SS", "quote": "exact short quote", "reason": "why this moment stands out"}}]

Transcript:
{transcript}"""
    try:
        return {"key_moments": _safe_json(_llm(prompt))}
    except Exception as e:
        return {"key_moments": [], "status": f"Key Moments Error: {str(e)}"}


def analyze_energy_node(state: AgentState) -> dict:
    """
    Scores each chapter's energy level 1–10.
    Sends both the text AND pace data (words/sec) so the LLM has audio-native signal.
    """
    segments  = state.get("transcript_segments", [])
    chapters  = state.get("chapters", [])

    # Build pace-aware chapter blocks for the prompt
    chapter_blocks = []
    for ch in chapters:
        # Find segments belonging to this chapter (rough match by timestamp)
        ch_segs = [s for s in segments if s["timestamp"] >= ch["timestamp"]]
        word_count = sum(len(s["text"].split()) for s in ch_segs[:10])
        duration   = sum((s["end"] - s["start"]) for s in ch_segs[:10]) or 1
        pace       = round(word_count / duration, 2)  # words per second
        chapter_blocks.append(
            f"Chapter: {ch['title']} @ {ch['timestamp']}\n"
            f"Pace: {pace} words/sec\n"
            f"Content: {ch['summary']}"
        )

    prompt = f"""You are analyzing podcast energy levels.
For each chapter below, assign an energy score from 1 (calm/slow) to 10 (heated/fast-paced).
Consider both the speaking pace AND the content mood.
Return ONLY a JSON array, no markdown, no extra text.
Format: [{{"chapter_title": "...", "timestamp": "MM:SS", "score": 7, "label": "Heated Debate"}}]

Chapters:
{"---".join(chapter_blocks)}"""
    try:
        return {"energy_map": _safe_json(_llm(prompt))}
    except Exception as e:
        return {"energy_map": [], "status": f"Energy Error: {str(e)}"}


def extract_topics_node(state: AgentState) -> dict:
    """Maps all distinct topics discussed and which chapters they appear in."""
    transcript = _transcript_text(state.get("transcript_segments", []))
    chapters   = [ch["title"] for ch in state.get("chapters", [])]
    prompt = f"""You are mapping topics across a podcast episode.
Identify 5 to 8 distinct topics discussed. For each, list which chapters cover it.
Return ONLY a JSON array, no markdown, no extra text.
Format: [{{"topic": "...", "chapters": ["Chapter Title 1", "Chapter Title 2"]}}]

Chapter titles: {json.dumps(chapters)}

Transcript:
{transcript}"""
    try:
        return {"topics": _safe_json(_llm(prompt))}
    except Exception as e:
        return {"topics": [], "status": f"Topics Error: {str(e)}"}


# ══════════════════════════════════════════════════════════════════════════════
# AGENTIC NODES
# ══════════════════════════════════════════════════════════════════════════════

# ── Agentic Node A: Quality Gate ──────────────────────────────────────────────
def quality_gate_node(state: AgentState) -> dict:
    """
    Decision node — inspects transcript quality and routes accordingly.
    Sets audio_mode = 'short_clip' if audio is too short for full analysis,
    or flags quality warnings (low segment count, suspected music/noise).
    This is what makes the graph agentic: the path forward depends on the data.
    """
    segments = state.get("transcript_segments", [])
    flags    = []
    mode     = "full"

    total_words = sum(len(s["text"].split()) for s in segments)
    duration_s  = segments[-1]["end"] if segments else 0

    if len(segments) < 5:
        flags.append("⚠️ Very few transcript segments detected — audio may be mostly music or noise.")
    if total_words < 100:
        flags.append("⚠️ Transcript is very short. Some analyses may be limited.")
        mode = "short_clip"
    if duration_s > 0 and total_words / max(duration_s, 1) < 0.5:
        flags.append("⚠️ Low speech density detected — long silences or music in audio.")

    return {"audio_mode": mode, "quality_flags": flags, "chapter_retries": 0}


# ── Agentic Node B: Chapter Retry Router ─────────────────────────────────────
def chapter_quality_check_node(state: AgentState) -> dict:
    """
    Self-correction node — checks if chapter output is usable.
    If fewer than 3 chapters were generated and we haven't retried yet,
    signals the graph to loop back and regenerate with a stricter prompt.
    Max 1 retry to avoid infinite loops.
    """
    chapters = state.get("chapters", [])
    retries  = state.get("chapter_retries", 0)

    if len(chapters) < 3 and retries < 1:
        # Force a retry: clear chapters and increment retry counter
        return {"chapters": [], "chapter_retries": retries + 1,
                "status": f"Chapter retry {retries + 1}: too few chapters generated, retrying..."}

    return {"chapter_retries": retries}


def generate_chapters_retry_node(state: AgentState) -> dict:
    """
    Stricter chapter generation used on retry — explicitly demands minimum 3 chapters
    and provides more structured output guidance.
    """
    transcript = _transcript_text(state.get("transcript_segments", []))
    prompt = f"""You are a podcast editor creating chapter markers.
The previous attempt produced too few chapters. Try harder to find natural topic breaks.
You MUST return at least 3 chapters, ideally 4-6.
Look for: topic shifts, new speakers, new arguments, or time transitions.
Return ONLY a JSON array, no markdown, no extra text.
Format: [{{"title": "...", "timestamp": "MM:SS", "summary": "1-2 sentence description"}}]

Transcript:
{transcript}"""
    try:
        return {"chapters": _safe_json(_llm(prompt))}
    except Exception as e:
        return {"chapters": [], "status": f"Chapter Retry Error: {str(e)}"}


# ── Agentic Node C: Confidence Self-Evaluator ─────────────────────────────────
def self_evaluate_node(state: AgentState) -> dict:
    """
    Meta-cognition node — the LLM grades its own outputs.
    Produces a confidence score per section and flags anything below threshold.
    Surfaces these scores to the user as transparency signals.
    """
    chapters = state.get("chapters", [])
    moments  = state.get("key_moments", [])
    topics   = state.get("topics", [])
    flags    = list(state.get("quality_flags", []))

    prompt = f"""You just analyzed a podcast. Evaluate the quality of your own outputs.
Rate each section 1-10 for confidence and accuracy. Be critical and honest.

Chapters generated: {len(chapters)} — titles: {[c.get("title","") for c in chapters]}
Key moments found: {len(moments)}
Topics mapped: {len(topics)}

Return ONLY a JSON object, no markdown:
{{
  "chapters_confidence": <1-10>,
  "moments_confidence": <1-10>,
  "topics_confidence": <1-10>,
  "overall": <1-10>,
  "notes": "<one sentence about what you're least confident in>"
}}"""

    try:
        scores = _safe_json(_llm(prompt))
        # Flag low-confidence outputs to the user
        if isinstance(scores, dict):
            if scores.get("chapters_confidence", 10) < 6:
                flags.append(f"🤖 AI confidence in chapters: {scores.get('chapters_confidence')}/10 — {scores.get('notes','')}")
            if scores.get("moments_confidence", 10) < 5:
                flags.append(f"🤖 AI confidence in key moments: {scores.get('moments_confidence')}/10")
        return {"confidence_scores": scores, "quality_flags": flags}
    except Exception as e:
        return {"confidence_scores": {}, "quality_flags": flags}
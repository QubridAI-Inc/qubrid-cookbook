"""
api/routes.py

FastAPI router for NewsletterAgent.
Exposes endpoints that trigger the ADK pipeline and query session state.
"""

import logging
import os
import re
import litellm
from datetime import datetime

# Configure LiteLLM: retry up to 6 times with exponential backoff on rate limit errors
litellm.num_retries = 6
litellm.retry_after = 15  # wait at least 15s before retrying a rate-limited request

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from config.settings import OUTPUTS_DIR, MAX_STORIES
from database import db
from tools.email_tools import get_gmail_status, get_outlook_status

router = APIRouter()

# In-memory queue per session_id for SSE streaming
import asyncio
_stream_queues: dict[int, asyncio.Queue] = {}


def _flatten_exception_messages(exc: BaseException, seen: set[int] | None = None) -> list[str]:
    """Extract the most useful leaf exception messages from nested exception groups."""
    if seen is None:
        seen = set()

    exc_id = id(exc)
    if exc_id in seen:
        return []
    seen.add(exc_id)

    if isinstance(exc, BaseExceptionGroup):
        messages: list[str] = []
        for sub_exc in exc.exceptions:
            messages.extend(_flatten_exception_messages(sub_exc, seen))
        return messages

    message = str(exc).strip()
    label = type(exc).__name__
    parts = [f"{label}: {message}" if message else label]

    for chained in (exc.__cause__, exc.__context__):
        if chained is not None:
            parts.extend(_flatten_exception_messages(chained, seen))

    return parts


def _summarize_exception(exc: BaseException, max_length: int = 400) -> str:
    """Collapse nested exceptions into a short, user-visible summary."""
    raw_messages = _flatten_exception_messages(exc)
    unique_messages: list[str] = []
    seen_messages: set[str] = set()

    for message in raw_messages:
        cleaned = " ".join(message.split())
        if cleaned and cleaned not in seen_messages:
            seen_messages.add(cleaned)
            unique_messages.append(cleaned)

    if not unique_messages:
        unique_messages = [str(exc).strip() or type(exc).__name__]

    summary = " | ".join(unique_messages)
    return summary[:max_length]


# ── Request / Response models ─────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Payload for POST /api/generate."""
    topic: str
    tone: str = "Professional"
    recipient: str
    platform: str = "gmail"   # gmail | outlook | draft
    length: str = "Medium (5 stories)"


class SendRequest(BaseModel):
    """Payload for POST /api/send/{session_id}."""
    platform: str
    recipient: str
    action_type: str = "send"


# ── Background pipeline runner ────────────────────────────────────────────────

async def _run_pipeline(session_id: int, request: GenerateRequest) -> None:
    """Execute the full ADK agent pipeline in the background."""
    try:
        # Import here to avoid circular imports at module load time
        from agents.orchestrator import root_agent
        from google.adk.runners import Runner  # type: ignore
        from google.adk.sessions import InMemorySessionService  # type: ignore
        from google.genai import types as genai_types  # type: ignore

        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name="NewsletterAgent",
            session_service=session_service,
        )

        # Determine story count from length
        length_map = {
            "Short (3 stories)": 3,
            "Medium (5 stories)": 5,
            "Long (7 stories)": 7,
        }
        num_stories = length_map.get(request.length, MAX_STORIES)

        user_message = (
            f"Generate a {request.tone} newsletter about '{request.topic}'. "
            f"Find {num_stories} stories. "
            f"Recipient: {request.recipient}. "
            f"Platform: {request.platform}. "
            f"Topic for filter: {request.topic}. "
            f"Max stories: {num_stories}."
        )

        adk_session = await session_service.create_session(
            app_name="NewsletterAgent",
            user_id=str(session_id),
        )

        final_html = ""
        agent_names = [
            "research_team",
            "content_filter",
            "newsletter_writer",
            "html_formatter",
            "email_delivery",
        ]
        event_to_step = {
            "news_searcher_1": "research_team",
            "news_searcher_2": "research_team",
            "news_searcher_3": "research_team",
            "research_team": "research_team",
            "content_filter": "content_filter",
            "newsletter_writer": "newsletter_writer",
            "html_formatter": "html_formatter",
            "email_delivery": "email_delivery",
        }
        log_ids: dict[str, int] = {}

        for agent_name in agent_names:
            log_ids[agent_name] = db.log_agent(session_id, agent_name, status="waiting")

        async for event in runner.run_async(
            user_id=str(session_id),
            session_id=adk_session.id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=user_message)],
            ),
        ):
            author = getattr(event, "author", "")
            step_name = event_to_step.get(author)

            # -- Emit partial text tokens for live streaming --
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        chunk = part.text
                        # Push to SSE queue if anyone is listening
                        q = _stream_queues.get(session_id)
                        if q:
                            await q.put({"agent": author or step_name or "agent", "text": chunk})

                        if step_name:
                            summary = chunk[:150]
                            db.complete_agent_log(log_ids[step_name], "done", summary)

                            # Capture HTML from formatter
                            if step_name == "html_formatter":
                                if "<html" in chunk.lower() or "<!doctype" in chunk.lower():
                                    final_html += chunk

        # Signal end of stream
        q = _stream_queues.get(session_id)
        if q:
            await q.put(None)

        if not final_html:
            raise RuntimeError("Pipeline completed without generating newsletter HTML.")

        # Save newsletter
        slug = re.sub(r"[^a-z0-9]+", "_", request.topic.lower())[:40]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}_{ts}.html"
        output_path = os.path.join(OUTPUTS_DIR, filename)
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(final_html)
        db.save_newsletter(session_id, final_html, output_path)

        # Mark any still-running logs as done after the HTML has been saved.
        for log in db.get_agent_logs_for_session(session_id):
            if log["status"] == "running":
                db.complete_agent_log(log["id"], "done", "Completed")

        db.complete_session(session_id, num_stories)

    except Exception as exc:
        logger.exception("Pipeline failed for session %s", session_id)
        db.update_session_status(session_id, "failed")
        conn_err_summary = f"Pipeline error: {_summarize_exception(exc)}"
        logs = db.get_agent_logs_for_session(session_id)
        for log in logs:
            if log["status"] != "done":
                db.complete_agent_log(log["id"], "error", conn_err_summary)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_newsletter(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Start the ADK pipeline for a new newsletter and return the session id."""
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")

    # Pre-flight: check required API keys are set
    from config.settings import GOOGLE_API_KEY, QUBRID_API_KEY
    missing = []
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")
    if not QUBRID_API_KEY:
        missing.append("QUBRID_API_KEY")
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing API keys in .env: {', '.join(missing)}. "
                   "Add them and restart the API server.",
        )

    session_id = db.create_session(
        topic=request.topic,
        tone=request.tone,
        recipient=request.recipient,
        platform=request.platform,
    )
    
    # Pre-initialize SSE queue to avoid race condition where pipeline starts 
    # and emits tokens before the frontend connects to /api/stream
    _stream_queues[session_id] = asyncio.Queue()

    background_tasks.add_task(_run_pipeline, session_id, request)
    return {"session_id": session_id, "status": "running"}


@router.get("/status/{session_id}")
async def get_status(session_id: int) -> dict:
    """Return current session status and agent log progress."""
    session = db.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    logs = db.get_agent_logs_for_session(session_id)
    return {"session": session, "agent_logs": logs}


@router.get("/newsletter/{session_id}")
async def get_newsletter(session_id: int) -> dict:
    """Return the generated HTML newsletter for a completed session."""
    newsletter = db.get_newsletter_by_session(session_id)
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    return {"newsletter": newsletter}


@router.post("/send/{session_id}")
async def send_newsletter(session_id: int, request: SendRequest) -> dict:
    """Trigger delivery-only for an already-generated newsletter."""
    newsletter = db.get_newsletter_by_session(session_id)
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    from tools.email_tools import (
        send_gmail,
        send_outlook,
        create_gmail_draft,
        create_outlook_draft,
    )

    session = db.get_session_by_id(session_id)
    subject = f"Newsletter: {session['topic']}" if session else "Your Newsletter"
    html = newsletter["html_content"]

    if request.action_type == "draft":
        if request.platform == "gmail":
            result = create_gmail_draft(request.recipient, subject, html)
        elif request.platform == "outlook":
            result = create_outlook_draft(request.recipient, subject, html)
        else:
            raise HTTPException(status_code=400, detail="Unknown platform for draft")
    else:
        if request.platform == "gmail":
            result = send_gmail(request.recipient, subject, html)
        elif request.platform == "outlook":
            result = send_outlook(request.recipient, subject, html)
        else:
            raise HTTPException(status_code=400, detail="Unknown platform for sending")

    return result


@router.get("/health")
def health() -> dict:
    """Return API health and Composio connection status."""
    gmail_status = get_gmail_status()
    outlook_status = get_outlook_status()
    return {
        "status": "ok",
        "gmail": gmail_status,
        "outlook": outlook_status,
    }


@router.get("/stream/{session_id}")
async def stream_pipeline(session_id: int):
    """SSE endpoint — yields agent text tokens in real-time as they arrive."""
    # Use pre-existing queue or create if missing (defensive)
    if session_id not in _stream_queues:
        _stream_queues[session_id] = asyncio.Queue()
    q = _stream_queues[session_id]

    async def event_generator():
        try:
            # Yield a start sentinel
            yield "data: [START]\n\n"
            while True:
                item = await asyncio.wait_for(q.get(), timeout=120)
                if item is None:          # sentinel → pipeline done
                    yield "data: [DONE]\n\n"
                    break
                agent = item["agent"]
                text = item["text"].replace("\n", "\\n")
                yield f"data: {agent}|||{text}\n\n"
        except asyncio.TimeoutError:
            yield "data: [DONE]\n\n"
        finally:
            # We don't pop immediately, background task might still want to put None
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

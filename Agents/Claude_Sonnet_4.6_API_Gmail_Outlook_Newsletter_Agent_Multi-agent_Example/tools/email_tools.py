"""
tools/email_tools.py

Composio-backed email tool wrappers for NewsletterAgent.
Supports Gmail and Outlook send/draft actions.
All credentials are loaded from environment variables.
"""

import os

from config.settings import (
    COMPOSIO_API_KEY,
    COMPOSIO_CACHE_DIR,
    COMPOSIO_ENTITY_ID,
)

os.makedirs(COMPOSIO_CACHE_DIR, exist_ok=True)
os.environ.setdefault("COMPOSIO_CACHE_DIR", COMPOSIO_CACHE_DIR)

from composio import Action, Composio  # type: ignore


def _client() -> Composio:
    return Composio(api_key=COMPOSIO_API_KEY)


def _get_connected_account_id(app_name: str, entity_id: str = COMPOSIO_ENTITY_ID) -> str:
    """Helper to fetch the first active connected account ID for a given app."""
    try:
        entity = _client().get_entity(id=entity_id)
        for c in entity.get_connections():
            if getattr(c, "appName", "").lower() == app_name.lower() and getattr(c, "status", "") == "ACTIVE":
                return getattr(c, "id", "")
    except Exception:
        pass
    return ""


# ── Gmail ─────────────────────────────────────────────────────────────────────

def send_gmail(
    to: str,
    subject: str,
    body: str,
    user_id: str = COMPOSIO_ENTITY_ID,
) -> dict:
    """Send a newsletter via Gmail using the Composio GMAIL_SEND_EMAIL action."""
    try:
        account_id = _get_connected_account_id("gmail", user_id)
        if not account_id:
            return {"success": False, "message_id": "", "error": "No active Gmail connection found"}
            
        result = _client().actions.execute(
            action=Action.GMAIL_SEND_EMAIL,
            params={"recipient_email": to, "subject": subject, "body": body, "is_html": True},
            connected_account=account_id,
        )
        return {
            "success": True,
            "message_id": result.get("data", {}).get("messageId", ""),
            "error": "",
        }
    except Exception as exc:
        return {"success": False, "message_id": "", "error": str(exc)}


def create_gmail_draft(
    to: str,
    subject: str,
    body: str,
    user_id: str = COMPOSIO_ENTITY_ID,
) -> dict:
    """Save a newsletter as a Gmail draft via Composio GMAIL_CREATE_DRAFT."""
    try:
        account_id = _get_connected_account_id("gmail", user_id)
        if not account_id:
            return {"success": False, "draft_id": "", "error": "No active Gmail connection found"}
            
        result = _client().actions.execute(
            action=Action.GMAIL_CREATE_EMAIL_DRAFT,
            params={"recipient_email": to, "subject": subject, "body": body, "is_html": True},
            connected_account=account_id,
        )
        return {
            "success": True,
            "draft_id": result.get("data", {}).get("draftId", ""),
            "error": "",
        }
    except Exception as exc:
        return {"success": False, "draft_id": "", "error": str(exc)}


# ── Outlook ───────────────────────────────────────────────────────────────────

def send_outlook(
    to: str,
    subject: str,
    body: str,
    user_id: str = COMPOSIO_ENTITY_ID,
) -> dict:
    """Send a newsletter via Outlook using the Composio OUTLOOK_SEND_EMAIL action."""
    try:
        account_id = _get_connected_account_id("outlook", user_id)
        if not account_id:
            return {"success": False, "message_id": "", "error": "No active Outlook connection found"}
            
        result = _client().actions.execute(
            action=Action.OUTLOOK_OUTLOOK_SEND_EMAIL,
            params={"to_email": to, "subject": subject, "body": body, "body_type": "html"},
            connected_account=account_id,
        )
        data = result if isinstance(result, dict) else (result.data if hasattr(result, 'data') else {})
        if not data.get("successful", data.get("successfull", False)):
            raise Exception(data.get("error", "Unknown Outlook send error"))
        return {
            "success": True,
            "message_id": data.get("data", {}).get("messageId", ""),
            "error": "",
        }
    except Exception as exc:
        return {"success": False, "message_id": "", "error": str(exc)}


def create_outlook_draft(
    to: str,
    subject: str,
    body: str,
    user_id: str = COMPOSIO_ENTITY_ID,
) -> dict:
    """Save a newsletter as an Outlook draft via Composio OUTLOOK_CREATE_DRAFT."""
    try:
        account_id = _get_connected_account_id("outlook", user_id)
        if not account_id:
            return {"success": False, "draft_id": "", "error": "No active Outlook connection found"}
            
        result = _client().actions.execute(
            action=Action.OUTLOOK_OUTLOOK_CREATE_DRAFT,
            params={"to_email": to, "subject": subject, "body": body, "body_type": "html"},
            connected_account=account_id,
        )
        data = result if isinstance(result, dict) else (result.data if hasattr(result, 'data') else {})
        if not data.get("successful", data.get("successfull", False)):
            raise Exception(data.get("error", "Unknown Outlook draft error"))
        return {
            "success": True,
            "draft_id": data.get("data", {}).get("draftId", "created"),
            "error": "",
        }
    except Exception as exc:
        return {"success": False, "draft_id": "", "error": str(exc)}


# ── Status checks ─────────────────────────────────────────────────────────────

def get_gmail_status() -> dict:
    """Check whether a Gmail account is connected via Composio."""
    try:
        entity = _client().get_entity(id=COMPOSIO_ENTITY_ID)
        conns = entity.get_connections()
        for c in conns:
            if getattr(c, "appName", "").lower() == "gmail" and getattr(c, "status", "") == "ACTIVE":
                return {"connected": True, "email": getattr(c, "email", getattr(c, "id", ""))}
        return {"connected": False, "email": ""}
    except Exception:
        return {"connected": False, "email": ""}


def get_outlook_status() -> dict:
    """Check whether an Outlook account is connected via Composio."""
    try:
        entity = _client().get_entity(id=COMPOSIO_ENTITY_ID)
        conns = entity.get_connections()
        for c in conns:
            if getattr(c, "appName", "").lower() == "outlook" and getattr(c, "status", "") == "ACTIVE":
                return {"connected": True, "email": getattr(c, "email", getattr(c, "id", ""))}
        return {"connected": False, "email": ""}
    except Exception:
        return {"connected": False, "email": ""}

"""
database/db.py

SQLite database layer for NewsletterAgent.
Manages sessions, newsletters, and agent execution logs.
Auto-creates schema on startup via init_db().
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

from config.settings import DB_PATH


def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set to sqlite3.Row."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create all tables if they do not already exist."""
    conn = _get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                topic           TEXT NOT NULL,
                tone            TEXT,
                recipient       TEXT,
                platform        TEXT,
                status          TEXT DEFAULT 'running',
                total_stories   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS newsletters (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                html_content    TEXT,
                plain_summary   TEXT,
                output_path     TEXT
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                agent_name      TEXT,
                started_at      TIMESTAMP,
                completed_at    TIMESTAMP,
                status          TEXT DEFAULT 'running',
                output_summary  TEXT
            );
        """)
    conn.close()


def create_session(
    topic: str,
    tone: str,
    recipient: str,
    platform: str,
) -> int:
    """Insert a new session row and return its id."""
    conn = _get_connection()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO sessions (topic, tone, recipient, platform, status)
            VALUES (?, ?, ?, ?, 'running')
            """,
            (topic, tone, recipient, platform),
        )
        session_id = cur.lastrowid
    conn.close()
    return session_id


def update_session_status(session_id: int, status: str) -> None:
    """Update the status and updated_at timestamp for a session."""
    conn = _get_connection()
    with conn:
        conn.execute(
            """
            UPDATE sessions
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, session_id),
        )
    conn.close()


def complete_session(session_id: int, total_stories: int) -> None:
    """Mark session as complete and record total stories."""
    conn = _get_connection()
    with conn:
        conn.execute(
            """
            UPDATE sessions
            SET status = 'complete',
                total_stories = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (total_stories, session_id),
        )
    conn.close()


def save_newsletter(
    session_id: int,
    html_content: str,
    output_path: str,
) -> int:
    """Persist the generated HTML newsletter; return newsletter row id."""
    plain_summary = html_content[:200] if html_content else ""
    conn = _get_connection()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO newsletters (session_id, html_content, plain_summary, output_path)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, html_content, plain_summary, output_path),
        )
        newsletter_id = cur.lastrowid
    conn.close()
    return newsletter_id


def log_agent(session_id: int, agent_name: str, status: str = "running") -> int:
    """Create an agent_logs entry and return its id."""
    conn = _get_connection()
    with conn:
        if status == "running":
            cur = conn.execute(
                """
                INSERT INTO agent_logs (session_id, agent_name, started_at, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                """,
                (session_id, agent_name, status),
            )
        else:
            cur = conn.execute(
                """
                INSERT INTO agent_logs (session_id, agent_name, status)
                VALUES (?, ?, ?)
                """,
                (session_id, agent_name, status),
            )
        log_id = cur.lastrowid
    conn.close()
    return log_id


def complete_agent_log(
    log_id: int,
    status: str,
    output_summary: str,
) -> None:
    """Mark an agent log entry as done/error with a brief summary."""
    conn = _get_connection()
    with conn:
        conn.execute(
            """
            UPDATE agent_logs
            SET status = ?,
                completed_at = CURRENT_TIMESTAMP,
                output_summary = ?
            WHERE id = ?
            """,
            (status, output_summary[:400], log_id),
        )
    conn.close()


def get_recent_sessions(limit: int = 20) -> list[dict]:
    """Return the most recent sessions as plain dicts, newest first."""
    conn = _get_connection()
    rows = conn.execute(
        """
        SELECT * FROM sessions
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_by_id(session_id: int) -> Optional[dict]:
    """Return a single session dict or None."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_newsletter_by_session(session_id: int) -> Optional[dict]:
    """Return the newsletter row for a session or None."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM newsletters WHERE session_id = ? ORDER BY id DESC LIMIT 1",
        (session_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_agent_logs_for_session(session_id: int) -> list[dict]:
    """Return all agent logs for a session ordered by id."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM agent_logs WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_session(session_id: int) -> None:
    """Delete a session and cascade to newsletters and agent_logs."""
    conn = _get_connection()
    with conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.close()


def clear_all_sessions() -> None:
    """Delete every session (and their newsletters / agent_logs)."""
    conn = _get_connection()
    with conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM sessions")
    conn.close()


def get_global_stats() -> dict:
    """Return aggregate stats across all sessions."""
    conn = _get_connection()

    total_newsletters = conn.execute(
        "SELECT COUNT(*) FROM newsletters"
    ).fetchone()[0]

    total_sent = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE status = 'complete' AND platform != 'draft'"
    ).fetchone()[0]

    fav_row = conn.execute(
        """
        SELECT topic, COUNT(*) as cnt
        FROM sessions
        GROUP BY topic
        ORDER BY cnt DESC
        LIMIT 1
        """
    ).fetchone()
    favourite_topic = fav_row["topic"] if fav_row else "—"

    avg_stories = conn.execute(
        "SELECT COALESCE(AVG(total_stories), 0) FROM sessions WHERE total_stories > 0"
    ).fetchone()[0]

    conn.close()
    return {
        "total_newsletters": total_newsletters,
        "total_sent": total_sent,
        "favourite_topic": favourite_topic,
        "avg_stories": round(avg_stories, 1),
    }

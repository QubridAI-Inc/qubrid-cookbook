"""SQLite persistence layer for Recall AI sessions and messages."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from config.settings import DB_PATH


@contextmanager
def _connect() -> Generator[sqlite3.Connection, None, None]:
    """Context manager: open, yield, commit/rollback, and always close."""
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Create the SQLite schema if it does not already exist."""
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                persona TEXT NOT NULL,
                title TEXT,
                total_turns INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                api_content TEXT,
                tokens_used INTEGER,
                latency_ms REAL
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
            ON sessions(updated_at DESC);

            CREATE INDEX IF NOT EXISTS idx_messages_session_id
            ON messages(session_id, created_at, id);
            """
        )
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(messages)").fetchall()
        }
        if "api_content" not in columns:
            connection.execute("ALTER TABLE messages ADD COLUMN api_content TEXT")


def create_session(persona: str, title: str) -> int:
    """Insert a new session row and return its primary key."""
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO sessions (persona, title)
            VALUES (?, ?)
            """,
            (persona, title),
        )
        return int(cursor.lastrowid)


def update_session_title(session_id: int, title: str) -> None:
    """Update the stored title for a session."""
    with _connect() as connection:
        connection.execute(
            """
            UPDATE sessions
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, session_id),
        )


def save_message(
    session_id: int,
    role: str,
    content: str,
    tokens_used: int | None,
    latency_ms: float | None,
    api_content: str | None = None,
) -> int:
    """Persist a message and refresh aggregate session counters."""
    safe_tokens = int(tokens_used or 0)
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO messages (session_id, role, content, api_content, tokens_used, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                api_content,
                safe_tokens if tokens_used is not None else None,
                latency_ms,
            ),
        )
        connection.execute(
            """
            UPDATE sessions
            SET updated_at = CURRENT_TIMESTAMP,
                total_tokens = COALESCE(total_tokens, 0) + ?,
                total_turns = (
                    SELECT COUNT(*)
                    FROM messages
                    WHERE session_id = ? AND role = 'user'
                )
            WHERE id = ?
            """,
            (safe_tokens, session_id, session_id),
        )
        return int(cursor.lastrowid)


def get_session_messages(session_id: int) -> list[dict[str, Any]]:
    """Return all messages for a session ordered oldest to newest."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT role, content, api_content, created_at, tokens_used, latency_ms
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (session_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_all_sessions(limit: int = 15) -> list[dict[str, Any]]:
    """Return recent sessions for the history sidebar."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, persona, title, total_turns, total_tokens, updated_at
            FROM sessions
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_session_by_id(session_id: int) -> dict[str, Any] | None:
    """Return one session row by id if it exists."""
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, created_at, updated_at, persona, title, total_turns, total_tokens
            FROM sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
    return dict(row) if row else None


def delete_session(session_id: int) -> None:
    """Delete one session and all of its messages."""
    with _connect() as connection:
        connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


def clear_all_sessions() -> None:
    """Delete every stored session and message."""
    with _connect() as connection:
        connection.execute("DELETE FROM sessions")


def get_global_stats() -> dict[str, Any]:
    """Return aggregate usage statistics across all sessions."""
    with _connect() as connection:
        summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_sessions,
                COALESCE(SUM(total_turns), 0) AS total_turns,
                COALESCE(SUM(total_tokens), 0) AS total_tokens,
                COALESCE(MAX(total_turns), 0) AS longest_session_turns
            FROM sessions
            """
        ).fetchone()
        favourite = connection.execute(
            """
            SELECT persona
            FROM sessions
            GROUP BY persona
            ORDER BY COUNT(*) DESC, MAX(updated_at) DESC
            LIMIT 1
            """
        ).fetchone()

    return {
        "total_sessions": int(summary["total_sessions"]),
        "total_turns": int(summary["total_turns"]),
        "total_tokens": int(summary["total_tokens"]),
        "longest_session_turns": int(summary["longest_session_turns"]),
        "favourite_persona": favourite["persona"] if favourite else "N/A",
    }

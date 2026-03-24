"""
SQLite persistence layer for ToneCraft AI.
Auto-creates the database and schema on first run.
All public functions use context managers so connections are always closed cleanly.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator

from config.settings import DB_PATH


@contextmanager
def _connect() -> Generator[sqlite3.Connection, None, None]:
    """Yield a connected SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """
    Create tables and migrate schema if needed.
    Safe to call on every app startup — idempotent.
    """
    with _connect() as conn:
        # Core rewrites table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rewrites (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                original_text   TEXT NOT NULL,
                tone            TEXT NOT NULL,
                rewritten_text  TEXT NOT NULL,
                explanation     TEXT NOT NULL,
                tokens_used     INTEGER,
                latency_ms      REAL,
                word_change_pct REAL,
                quality_score   REAL,
                content_type    TEXT,
                detected_tone   TEXT,
                rewrite_attempts INTEGER DEFAULT 1
            )
            """
        )

        # Additive migrations for existing databases
        existing_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(rewrites)").fetchall()
        }
        for col, definition in [
            ("quality_score",    "REAL"),
            ("content_type",     "TEXT"),
            ("detected_tone",    "TEXT"),
            ("rewrite_attempts", "INTEGER DEFAULT 1"),
        ]:
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE rewrites ADD COLUMN {col} {definition}")

        # Chat messages table for multi-turn refinements
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                rewrite_id  INTEGER NOT NULL REFERENCES rewrites(id) ON DELETE CASCADE,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_rewrite(
    original: str,
    tone: str,
    rewritten: str,
    explanation: str,
    tokens: int,
    latency: float,
    word_change_pct: float,
    quality_score: float = 0.0,
    content_type: str = "",
    detected_tone: str = "",
    rewrite_attempts: int = 1,
) -> int:
    """
    Persist a completed rewrite to the database.

    Returns
    -------
    int — the auto-assigned row id of the new record.
    """
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO rewrites
                (original_text, tone, rewritten_text, explanation,
                 tokens_used, latency_ms, word_change_pct,
                 quality_score, content_type, detected_tone, rewrite_attempts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                original, tone, rewritten, explanation,
                tokens, latency, word_change_pct,
                quality_score, content_type, detected_tone, rewrite_attempts,
            ),
        )
        return cursor.lastrowid


def get_recent_rewrites(limit: int = 20) -> list[dict]:
    """
    Fetch the most recent rewrites ordered newest-first.

    Parameters
    ----------
    limit: Maximum number of records to return.

    Returns
    -------
    List of dicts, each representing one row.
    """
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM rewrites ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_rewrite_by_id(id: int) -> dict | None:
    """
    Fetch a single rewrite record by primary key.

    Returns
    -------
    dict if found, None otherwise.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM rewrites WHERE id = ?", (id,)
        ).fetchone()
    return dict(row) if row else None


def delete_rewrite(id: int) -> None:
    """Delete a single rewrite record by primary key."""
    with _connect() as conn:
        conn.execute("DELETE FROM rewrites WHERE id = ?", (id,))


def clear_all_rewrites() -> None:
    """Delete every record in the rewrites table."""
    with _connect() as conn:
        conn.execute("DELETE FROM rewrites")


def save_message(rewrite_id: int, role: str, content: str) -> None:
    """Persist a single chat message (user or assistant) for a rewrite thread."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages (rewrite_id, role, content) VALUES (?, ?, ?)",
            (rewrite_id, role, content),
        )


def get_messages_for_rewrite(rewrite_id: int) -> list[dict]:
    """Return all chat messages for a rewrite, ordered oldest-first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content FROM chat_messages WHERE rewrite_id = ? ORDER BY created_at ASC",
            (rewrite_id,),
        ).fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def get_session_stats() -> dict:
    """
    Compute aggregate statistics across all stored rewrites.

    Returns
    -------
    dict with keys:
        total_rewrites (int)
        most_used_tone (str)  — tone with the highest count, or "—" if empty
        avg_latency    (float)
        total_tokens   (int)
    """
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM rewrites").fetchone()[0]

        top_tone_row = conn.execute(
            """
            SELECT tone, COUNT(*) as cnt
            FROM rewrites
            GROUP BY tone
            ORDER BY cnt DESC
            LIMIT 1
            """
        ).fetchone()

        agg = conn.execute(
            "SELECT AVG(latency_ms), SUM(tokens_used) FROM rewrites"
        ).fetchone()

    most_used_tone = top_tone_row["tone"] if top_tone_row else "—"
    avg_latency = round((agg[0] or 0.0) / 1000, 1)  # convert ms → seconds
    total_tokens = int(agg[1] or 0)

    return {
        "total_rewrites": total,
        "most_used_tone": most_used_tone,
        "avg_latency": avg_latency,
        "total_tokens": total_tokens,
    }

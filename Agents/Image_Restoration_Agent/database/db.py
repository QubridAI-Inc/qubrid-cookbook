"""
ReVive AI — SQLite database layer.
All read/write operations for restoration jobs and agent logs.
Database is auto-created on first call to init_db().
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Generator

from config.settings import DB_PATH


# ── Connection helper ─────────────────────────────────────────────────────────

@contextmanager
def _conn() -> Generator[sqlite3.Connection, None, None]:
    """Yield a sqlite3 connection with row_factory set to dict-like Row."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


# ── Schema ────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create tables if they don't already exist, and run any schema migrations."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS restoration_jobs (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                original_filename   TEXT,
                original_image_path TEXT,
                final_image_path    TEXT,
                is_black_and_white  BOOLEAN,
                estimated_era       TEXT,
                damage_severity     TEXT,
                qa_score            INTEGER,
                qa_verdict          TEXT,
                retry_count         INTEGER DEFAULT 0,
                total_latency_ms    REAL,
                status              TEXT DEFAULT 'pending',
                result_json         TEXT
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id          INTEGER REFERENCES restoration_jobs(id),
                agent_name      TEXT,
                model_used      TEXT,
                started_at      TIMESTAMP,
                completed_at    TIMESTAMP,
                tokens_used     INTEGER,
                latency_ms      REAL,
                output_summary  TEXT
            );
        """)
        # Migration: add result_json column to existing DBs that pre-date it
        cols = [r[1] for r in con.execute("PRAGMA table_info(restoration_jobs)").fetchall()]
        if "result_json" not in cols:
            con.execute("ALTER TABLE restoration_jobs ADD COLUMN result_json TEXT")


# ── Job CRUD ──────────────────────────────────────────────────────────────────

def create_job(filename: str, original_path: str) -> int:
    """
    Insert a new restoration job record and return its ID.

    Args:
        filename:      Original uploaded filename.
        original_path: Path where the original image was saved.

    Returns:
        Integer primary key of the new row.
    """
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO restoration_jobs
               (original_filename, original_image_path, status)
               VALUES (?, ?, 'pending')""",
            (filename, original_path),
        )
        return cur.lastrowid  # type: ignore[return-value]


def update_job_status(job_id: int, status: str) -> None:
    """Update the status field of an existing job."""
    with _conn() as con:
        con.execute(
            "UPDATE restoration_jobs SET status = ? WHERE id = ?",
            (status, job_id),
        )


def complete_job(job_id: int, result: dict[str, Any]) -> None:
    """
    Write all result fields to the job record and mark it complete.

    Args:
        job_id: Primary key of the job.
        result: Pipeline result dict from pipeline.run_restoration_pipeline().
    """
    hist = result.get("historical_context", {})
    dmg = result.get("damage_report", {})
    qa = result.get("qa_report", {})

    # Store full result as JSON for history replay (exclude large base64 fields)
    result_clean = {k: v for k, v in result.items()
                    if k not in ("image_base64", "original_b64", "final_b64")}
    with _conn() as con:
        con.execute(
            """UPDATE restoration_jobs SET
               final_image_path    = ?,
               is_black_and_white  = ?,
               estimated_era       = ?,
               damage_severity     = ?,
               qa_score            = ?,
               qa_verdict          = ?,
               retry_count         = ?,
               total_latency_ms    = ?,
               result_json         = ?,
               status              = 'complete'
               WHERE id = ?""",
            (
                result.get("final_image_path", ""),
                hist.get("is_black_and_white", False),
                hist.get("estimated_era", "Unknown"),
                dmg.get("severity", "unknown"),
                qa.get("restoration_score", 0),
                qa.get("verdict", ""),
                result.get("retry_count", 0),
                result.get("total_latency_ms", 0.0),
                json.dumps(result_clean),
                job_id,
            ),
        )


# ── Agent logs ────────────────────────────────────────────────────────────────

def save_agent_log(
    job_id: int,
    agent_name: str,
    model: str,
    tokens: int,
    latency: float,
    output_summary: str,
) -> None:
    """
    Persist a single agent execution record.

    Args:
        job_id:         Foreign key to restoration_jobs.
        agent_name:     Display name of the agent.
        model:          Model ID used.
        tokens:         Total tokens consumed.
        latency:        Execution time in milliseconds.
        output_summary: First 200 chars of agent output.
    """
    with _conn() as con:
        con.execute(
            """INSERT INTO agent_logs
               (job_id, agent_name, model_used, tokens_used,
                latency_ms, output_summary)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (job_id, agent_name, model, tokens, latency, output_summary[:200]),
        )


# ── Queries ───────────────────────────────────────────────────────────────────

def get_recent_jobs(limit: int = 15) -> list[dict[str, Any]]:
    """Return the most recent restoration jobs, newest first."""
    with _conn() as con:
        rows = con.execute(
            """SELECT * FROM restoration_jobs
               ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_job_by_id(job_id: int) -> dict[str, Any] | None:
    """Return a single job by primary key, or None if not found."""
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM restoration_jobs WHERE id = ?", (job_id,)
        ).fetchone()
    return dict(row) if row else None


def get_job_result(job_id: int) -> dict[str, Any] | None:
    """Return the full pipeline result dict for a completed job, or None."""
    job = get_job_by_id(job_id)
    if not job:
        return None
    raw = job.get("result_json")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def get_agent_logs_for_job(job_id: int) -> list[dict[str, Any]]:
    """Return all agent logs for a given job ID."""
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM agent_logs WHERE job_id = ? ORDER BY id ASC",
            (job_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_job(job_id: int) -> None:
    """Delete a job and its associated agent logs."""
    with _conn() as con:
        con.execute("DELETE FROM agent_logs WHERE job_id = ?", (job_id,))
        con.execute("DELETE FROM restoration_jobs WHERE id = ?", (job_id,))


def clear_all_jobs() -> None:
    """Truncate both tables."""
    with _conn() as con:
        con.execute("DELETE FROM agent_logs")
        con.execute("DELETE FROM restoration_jobs")


def get_global_stats() -> dict[str, Any]:
    """
    Compute aggregate stats across all completed jobs.

    Returns:
        Dict with total_jobs, avg_qa_score, total_tokens,
        best_restoration_score, favourite_era.
    """
    with _conn() as con:
        job_row = con.execute(
            """SELECT
                COUNT(*) AS total_jobs,
                ROUND(AVG(qa_score), 1) AS avg_qa_score,
                MAX(qa_score) AS best_restoration_score
               FROM restoration_jobs
               WHERE status = 'complete'"""
        ).fetchone()

        token_row = con.execute(
            "SELECT COALESCE(SUM(tokens_used), 0) AS total_tokens FROM agent_logs"
        ).fetchone()

        era_row = con.execute(
            """SELECT estimated_era, COUNT(*) AS cnt
               FROM restoration_jobs
               WHERE estimated_era IS NOT NULL AND estimated_era != 'Unknown'
               GROUP BY estimated_era
               ORDER BY cnt DESC LIMIT 1"""
        ).fetchone()

    return {
        "total_jobs": job_row["total_jobs"] or 0,
        "avg_qa_score": job_row["avg_qa_score"] or 0,
        "best_restoration_score": job_row["best_restoration_score"] or 0,
        "total_tokens": token_row["total_tokens"] or 0,
        "favourite_era": era_row["estimated_era"] if era_row else "—",
    }

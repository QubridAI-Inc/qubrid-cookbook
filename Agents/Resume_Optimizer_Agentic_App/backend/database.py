"""SQLite database operations for resume history."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Database path
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "career_sync.db"


def init_database():
    """Initialize database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            job_title TEXT,
            company TEXT,
            original_resume TEXT NOT NULL,
            job_description TEXT NOT NULL,
            jd_analysis TEXT,
            initial_critique TEXT,
            suggestions TEXT,
            final_resume TEXT NOT NULL,
            final_critique TEXT,
            iterations INTEGER,
            final_score REAL,
            markdown_path TEXT,
            pdf_path TEXT,
            metadata TEXT
        )
    """)
    
    # Index for fast queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON generations(timestamp DESC)
    """)
    
    conn.commit()
    conn.close()


def save_generation(state: Dict[str, Any], output_paths: Dict[str, str]) -> int:
    """
    Save generation to database.
    
    Args:
        state: Resume state dictionary
        output_paths: Dict with 'markdown' and 'pdf' keys
        
    Returns:
        generation_id
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract data with safe defaults
    jd_analysis = state.get("jd_analysis", {})
    initial_critique = state.get("initial_critique", {})
    final_critique = state.get("critique", {})
    suggestions = state.get("suggestions", [])
    
    # Ensure paths are strings, not None
    markdown_path = output_paths.get("markdown") or ""
    pdf_path = output_paths.get("pdf") or ""
    
    cursor.execute("""
        INSERT INTO generations (
            timestamp, job_title, company, original_resume, job_description,
            jd_analysis, initial_critique, suggestions, final_resume, final_critique,
            iterations, final_score, markdown_path, pdf_path, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        jd_analysis.get("job_title", "Unknown"),
        jd_analysis.get("company", "Unknown"),
        state.get("original_resume", ""),
        state.get("job_description", ""),
        json.dumps(jd_analysis),
        json.dumps(initial_critique),
        json.dumps(suggestions),
        state.get("final_resume", ""),
        json.dumps(final_critique),
        state.get("iteration", 0),
        final_critique.get("overall_score", 0),
        str(markdown_path),
        str(pdf_path),
        json.dumps(state.get("metadata", {}))
    ))
    
    generation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return generation_id


def get_all_generations() -> List[Dict[str, Any]]:
    """
    Get all generations ordered by timestamp (newest first).
    
    Returns:
        List of generation dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM generations 
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_generation_by_id(generation_id: int) -> Optional[Dict[str, Any]]:
    """
    Get specific generation by ID.
    
    Args:
        generation_id: Database ID
        
    Returns:
        Generation dictionary or None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM generations WHERE id = ?", (generation_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def delete_generation(generation_id: int):
    """Delete a generation from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM generations WHERE id = ?", (generation_id,))
    conn.commit()
    conn.close()
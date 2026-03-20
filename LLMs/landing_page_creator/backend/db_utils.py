"""
SQLite database utilities for SnapCode AI history tracking.
"""
import sqlite3
import datetime
from pathlib import Path

# Database path in the root purely for simplicity
DB_PATH = Path("history.db")

def init_db():
    """Initializes the SQLite database and creates the history table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                preview_text TEXT,
                html_code TEXT,
                user_note TEXT
            )
        """)
        # Schema migration
        try:
            conn.execute("ALTER TABLE history ADD COLUMN title TEXT")
        except sqlite3.OperationalError:
            pass

def save_generation(preview_text: str, html_code: str, user_note: str):
    """Saves a successfully generated HTML code to the history table."""
    with sqlite3.connect(DB_PATH) as conn:
        timestamp = datetime.datetime.now().strftime("%b %d, %I:%M %p")
        conn.execute("""
            INSERT INTO history (timestamp, preview_text, html_code, user_note)
            VALUES (?, ?, ?, ?)
        """, (timestamp, preview_text, html_code, user_note))

def rename_history_item(item_id: int, new_title: str):
    """Updates the explicit custom title for a specific history generation."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE history SET title = ? WHERE id = ?", (new_title, item_id))

def get_history():
    """Fetches all history items ordered by most recent first."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT id, timestamp, preview_text, html_code, user_note, title FROM history ORDER BY id DESC")
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "preview_text": row[2],
                "html_code": row[3],
                "user_note": row[4],
                "title": row[5] if len(row) > 5 else None
            }
            for row in cursor.fetchall()
        ]

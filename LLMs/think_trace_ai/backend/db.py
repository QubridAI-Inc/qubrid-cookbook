"""
SQLite database logic for ThinkTrace AI history sessions.
"""
import sqlite3
import os

# Store DB in the project root
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'thinktrace.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the SQLite database and creates the sessions table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                question TEXT NOT NULL,
                category TEXT NOT NULL,
                reasoning TEXT,
                answer TEXT,
                tokens_used INTEGER,
                latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def save_session(question: str, category: str, reasoning: str, answer: str, tokens: int, latency: float) -> int:
    """Saves a new session to the database and returns its ID."""
    # Create a short title from the question
    title = question[:30] + '...' if len(question) > 30 else question
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions 
            (title, question, category, reasoning, answer, tokens_used, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, question, category, reasoning, answer, tokens, latency))
        return cursor.lastrowid

def get_all_sessions() -> list[dict]:
    """Retrieves all sessions ordered by newest first."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, question, category, reasoning, answer, tokens_used, latency_ms, 
                   datetime(created_at, 'localtime') as created_at 
            FROM sessions 
            ORDER BY id DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_session(session_id: int) -> dict:
    """Retrieves a specific session by ID."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def rename_session(session_id: int, new_title: str):
    """Updates the title of a specific session."""
    with get_connection() as conn:
        conn.execute('UPDATE sessions SET title = ? WHERE id = ?', (new_title, session_id))

def delete_session(session_id: int):
    """Deletes a specific session."""
    with get_connection() as conn:
        conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))

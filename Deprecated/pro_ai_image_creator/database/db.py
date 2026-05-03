import sqlite3
import os

DB_PATH = "assets.db"

# NO "from database.db import ..." HERE!

def init_db():
    """Initializes the database and creates tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, title TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        session_id TEXT, role TEXT, content TEXT, image_url TEXT)''')
    conn.commit()
    conn.close()

def delete_session(session_id):
    """Permanently removes a session and its associated messages."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def create_session(title):
    """Creates a new session and returns the ID."""
    import uuid
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def get_sessions():
    """Retrieves all sessions, ensuring the latest appears at the top."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Use 'rowid DESC' to get the most recently inserted items first
    cursor.execute("SELECT * FROM sessions ORDER BY rowid DESC")
    
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def get_history(session_id):
    """Retrieves message history for a specific session."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, image_url FROM messages WHERE session_id = ?", (session_id,))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history

def add_message(session_id, role, content, image_url=None):
    """Adds a new message to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, role, content, image_url) VALUES (?, ?, ?, ?)", 
                   (session_id, role, content, image_url))
    conn.commit()
    conn.close()
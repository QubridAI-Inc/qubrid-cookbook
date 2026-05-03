import sqlite3  # Standard library for interacting with SQLite databases
import json  # Used to serialize dictionaries (like usage metrics) into text strings for storage
import os  # Used to check if files exist and remove them (for deleting images)
from datetime import datetime  # Used for timestamping (though SQLite handles defaults automatically)
from typing import List, Dict, Any  # Type hinting for better code readability

# The filename of the local SQLite database. It will be created in the root directory.
DB_NAME = "apex_industrial.db"

def init_db():
    """
    Initializes the database.
    This function runs on app startup. It creates the necessary tables ('sessions' and 'messages')
    if they do not already exist. This ensures the app doesn't crash on a fresh install.
    """
    conn = sqlite3.connect(DB_NAME)  # Connect to the file (creates it if missing)
    c = conn.cursor()  # A cursor allows us to execute SQL commands
    
    # Table 1: Sessions
    # This table stores the high-level metadata for each chat session.
    # - id: The unique UUID string.
    # - title: The name of the chat (e.g., "Cracked Pipe Analysis").
    # - image_path: Local file path to the uploaded image.
    # - mode: The selected protocol (e.g., 'Defect Inspection').
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            image_path TEXT,
            mode TEXT DEFAULT 'General Analysis', 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: Messages
    # This table stores the actual conversation history.
    # - session_id: Links the message to a specific session in the table above (Foreign Key).
    # - role: 'user' or 'assistant'.
    # - content: The text text of the message.
    # - usage_data: A JSON string storing token counts and latency stats.
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            usage_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')
    conn.commit()  # Save changes
    conn.close()   # Close connection

def create_session(session_id: str, title: str = "New Inspection", mode: str = "General Analysis"):
    """
    Creates a new entry in the 'sessions' table.
    This is called when the app starts or when the user clicks 'New Inspection'.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # "INSERT OR IGNORE": If we accidentally try to create a session with an ID that already exists,
    # this command silently fails instead of crashing the app.
    c.execute("INSERT OR IGNORE INTO sessions (id, title, mode) VALUES (?, ?, ?)", (session_id, title, mode))
    conn.commit()
    conn.close()

def update_session_mode(session_id: str, mode: str):
    """
    Updates the analysis protocol (e.g., changing from 'General' to 'Defect')
    for a specific session. This ensures the app 'remembers' your settings.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # This try-except block handles a specific edge case called a "Schema Migration".
    # If a user has an old version of the database without the 'mode' column,
    # the first command will fail. The 'except' block catches that failure,
    # adds the missing column, and then tries the update again.
    try:
        c.execute("UPDATE sessions SET mode = ? WHERE id = ?", (mode, session_id))
    except sqlite3.OperationalError:
        try:
            c.execute("ALTER TABLE sessions ADD COLUMN mode TEXT DEFAULT 'General Analysis'")
            c.execute("UPDATE sessions SET mode = ? WHERE id = ?", (mode, session_id))
        except:
            pass  # If it still fails, we ignore it to prevent a crash
    conn.commit()
    conn.close()

def update_session_image(session_id: str, image_path: str):
    """
    Links an uploaded image file path to a specific session ID.
    This allows us to reload the image if the user comes back to this chat later.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE sessions SET image_path = ? WHERE id = ?", (image_path, session_id))
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def get_session_meta(session_id: str) -> Dict:
    """
    Retrieves the metadata (Title, Mode, Image Path) for a single session.
    Used by app.py to set up the UI state when loading a chat.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Crucial: Allows accessing columns by name (row['title']) instead of index (row[1])
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None  # Convert SQLite Row object to a standard Python Dictionary

def add_message(session_id: str, role: str, content: str, usage: Dict = None):
    """
    Saves a single message (User or AI) to the database.
    Also handles the 'Auto-Renaming' feature.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Convert the usage dictionary (tokens, latency) into a JSON string because SQLite cannot store dictionaries directly.
    usage_json = json.dumps(usage) if usage else None
    
    c.execute(
        "INSERT INTO messages (session_id, role, content, usage_data) VALUES (?, ?, ?, ?)",
        (session_id, role, content, usage_json)
    )
    
    # Auto-Renaming Logic:
    # If the user sends a message and the title is still the default "New Inspection",
    # we update the title to be the first ~30 characters of their message.
    # This helps users find chats easily in the sidebar.
    if role == "user":
        new_title = (content[:30] + '...') if len(content) > 30 else content
        c.execute("UPDATE sessions SET title = ? WHERE id = ? AND title = 'New Inspection'", (new_title, session_id))
        
    conn.commit()
    conn.close()

def get_all_sessions() -> List[Dict]:
    """
    Fetches all sessions to display in the Sidebar History list.
    It includes logic to filter out 'Ghost Sessions' (empty sessions created by accident).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Complex Query Explanation:
    # We want sessions that match ANY of these criteria:
    # 1. Have at least one message (m.id IS NOT NULL)
    # 2. Have an image uploaded (s.image_path IS NOT NULL)
    # 3. Have been renamed by the user (s.title != 'New Inspection')
    # This filters out empty "New Inspection" sessions that happen when you refresh the page.
    c.execute("""
        SELECT DISTINCT s.*
        FROM sessions s
        LEFT JOIN messages m ON s.id = m.session_id
        WHERE m.id IS NOT NULL 
           OR s.image_path IS NOT NULL 
           OR s.title != 'New Inspection'
        ORDER BY s.created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_session_history(session_id: str) -> List[Dict]:
    """
    Fetches the full chat history for the main chat window.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        msg = {"role": row["role"], "content": row["content"]}
        # Parse the JSON string back into a Python dictionary for the frontend to use
        if row["usage_data"]:
            msg["usage"] = json.loads(row["usage_data"])
        history.append(msg)
    return history

def update_session_title(session_id: str, new_title: str):
    """
    Manually renames a session.
    Triggered when the user types a new name in the Sidebar 'Session Options'.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id: str):
    """
    Deletes a session completely.
    Crucially, this also cleans up the local storage by deleting the image file.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Step 1: Find the image path associated with this session
    c.execute("SELECT image_path FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    
    # Step 2: Delete the actual file from the computer's hard drive
    if row and row[0]:
        image_path = row[0]
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting file: {e}")

    # Step 3: Delete all messages belonging to this session
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    # Step 4: Delete the session record itself
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
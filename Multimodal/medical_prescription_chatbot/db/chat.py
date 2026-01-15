import uuid
from db.connection import get_connection

def save_chat_message(prescription_id, role, content):
    """Save a single chat message linked to a prescription."""
    message_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                INSERT INTO chat_messages (id, prescription_id, role, content)
                VALUES (?, ?, ?, ?)
            """, (message_id, prescription_id, role, content))
        return message_id
    finally:
        conn.close()

def get_chat_history(prescription_id):
    """Retrieve all chat messages for a specific prescription."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT id, role, content, created_at 
            FROM chat_messages 
            WHERE prescription_id = ?
            ORDER BY created_at ASC
        """, (prescription_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def clear_chat_history(prescription_id):
    """Clear all chat messages for a prescription (Reset Chat)."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM chat_messages WHERE prescription_id = ?", (prescription_id,))
    finally:
        conn.close()

import sqlite3
import os
from pathlib import Path

DB_PATH = Path("medical_ai.db")

def get_connection():
    """Create a database connection and initialize schema if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for better concurrency in Streamlit
    conn.execute("PRAGMA journal_mode=WAL;")
    
    _init_schema(conn)
    return conn

def _init_schema(conn):
    """Initialize the database schema."""
    with conn:
        # Prescriptions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id TEXT PRIMARY KEY,
                image_hash TEXT UNIQUE NOT NULL,
                image_data BLOB NOT NULL,
                extraction_json TEXT NOT NULL,
                audit_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chat messages table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                prescription_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions (id) ON DELETE CASCADE
            )
        """)
        
        # Index for faster lookup
        conn.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_hash ON prescriptions(image_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_prescription_id ON chat_messages(prescription_id)")

if __name__ == "__main__":
    # Test initialization
    get_connection().close()
    print("Database initialized successfully.")

import sqlite3
import json
from datetime import datetime
from config.settings import config

def _conn():
    return sqlite3.connect(config.DB_PATH)

def init_db():
    with _conn() as c:
        c.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                filename    TEXT,
                created_at  TEXT,
                result_json TEXT
            )
        ''')

def save_result(filename: str, result: dict):
    with _conn() as c:
        c.execute(
            'INSERT INTO history (filename, created_at, result_json) VALUES (?, ?, ?)',
            (filename, datetime.now().strftime("%b %d, %H:%M"), json.dumps(result))
        )

def get_history():
    """Returns [(id, filename, created_at), ...] newest first."""
    with _conn() as c:
        return c.execute(
            'SELECT id, filename, created_at FROM history ORDER BY id DESC'
        ).fetchall()

def get_by_id(row_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute(
            'SELECT filename, result_json FROM history WHERE id = ?', (row_id,)
        ).fetchone()
    return {"filename": row[0], "result": json.loads(row[1])} if row else None

def delete_by_id(row_id: int):
    with _conn() as c:
        c.execute('DELETE FROM history WHERE id = ?', (row_id,))
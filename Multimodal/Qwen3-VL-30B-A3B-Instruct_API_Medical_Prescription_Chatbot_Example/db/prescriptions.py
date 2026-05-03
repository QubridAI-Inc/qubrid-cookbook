import json
import uuid
from db.connection import get_connection

def save_prescription(image_hash, image_data, extraction_dict, audit_dict):
    """Save a new prescription record."""
    prescription_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                INSERT INTO prescriptions (id, image_hash, image_data, extraction_json, audit_json)
                VALUES (?, ?, ?, ?, ?)
            """, (
                prescription_id,
                image_hash,
                image_data,
                json.dumps(extraction_dict),
                json.dumps(audit_dict)
            ))
        return prescription_id
    finally:
        conn.close()

def get_prescription_by_hash(image_hash):
    """Retrieve a prescription by its image hash."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT id, image_data, extraction_json, audit_json, created_at 
            FROM prescriptions 
            WHERE image_hash = ?
        """, (image_hash,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["extraction"] = json.loads(data["extraction_json"])
            data["audit"] = json.loads(data["audit_json"])
            return data
        return None
    finally:
        conn.close()

def get_all_prescriptions():
    """Retrieve all prescription metadata for the sidebar."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT id, image_hash, extraction_json, created_at 
            FROM prescriptions 
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def update_prescription_data(prescription_id, extraction_dict, audit_dict):
    """Update extraction and audit data (e.g., after ambiguity resolution)."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE prescriptions 
                SET extraction_json = ?, audit_json = ?
                WHERE id = ?
            """, (
                json.dumps(extraction_dict),
                json.dumps(audit_dict),
                prescription_id
            ))
    finally:
        conn.close()

def delete_prescription(prescription_id):
    """Delete a prescription and its associated chat history."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
    finally:
        conn.close()

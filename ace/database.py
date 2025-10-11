import sqlite3
import json
from typing import List, Dict, Optional

DATABASE_PATH = "ace_playbook.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database by creating the playbook_entries table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS playbook_entries (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL UNIQUE,
            metadata TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_playbook_entry(entry_id: str, content: str, metadata: Dict):
    """Adds a new entry to the playbook_entries table."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO playbook_entries (id, content, metadata) VALUES (?, ?, ?)",
        (entry_id, content, json.dumps(metadata))
    )
    conn.commit()
    conn.close()

def get_all_playbook_entries() -> List[Dict]:
    """Retrieves all entries from the playbook_entries table."""
    conn = get_db_connection()
    entries_cursor = conn.execute("SELECT * FROM playbook_entries").fetchall()
    conn.close()

    entries = []
    for row in entries_cursor:
        entry = dict(row)
        entry['metadata'] = json.loads(entry['metadata'])
        entries.append(entry)
    return entries

def content_exists(content: str) -> bool:
    """Checks if an entry with the given content already exists."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT 1 FROM playbook_entries WHERE content = ?", (content,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

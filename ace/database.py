import aiosqlite
import json
from typing import List, Dict

DATABASE_PATH = "ace_playbook.db"

async def initialize_database():
    """Initializes the database by creating the tables if they don't exist."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS playbook_entries (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL UNIQUE,
                metadata TEXT,
                embedding BLOB
            )
        """)
        await db.commit()

async def add_playbook_entry(entry_id: str, content: str, metadata: Dict, embedding: bytes):
    """Adds a new entry to the playbook_entries table."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO playbook_entries (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
            (entry_id, content, json.dumps(metadata), embedding)
        )
        await db.commit()

async def get_all_playbook_entries() -> List[Dict]:
    """Retrieves all entries and their embeddings from the playbook_entries table."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, content, metadata, embedding FROM playbook_entries") as cursor:
            rows = await cursor.fetchall()

    entries = []
    for row in rows:
        entry = dict(row)
        entry['metadata'] = json.loads(entry['metadata'])
        entries.append(entry)
    return entries

async def content_exists(content: str) -> bool:
    """Checks if an entry with the given content already exists."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT 1 FROM playbook_entries WHERE content = ?", (content,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

import aiosqlite
import json
from typing import List, Dict
import collections

DATABASE_PATH = "ace_playbook.db"

async def initialize_database():
    """Initializes the database by creating the tables if they don't exist."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS playbook_entries (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL UNIQUE,
                metadata TEXT,
                embedding BLOB,
                cluster_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY,
                summary TEXT
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

async def update_entry_cluster(entry_id: str, cluster_id: int):
    """Updates the cluster ID for a specific playbook entry."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE playbook_entries SET cluster_id = ? WHERE id = ?", (cluster_id, entry_id))
        await db.commit()

async def add_or_update_cluster_summary(cluster_id: int, summary: str):
    """Adds a new cluster summary or updates an existing one."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO clusters (id, summary) VALUES (?, ?)", (cluster_id, summary))
        await db.commit()

async def get_all_clusters_with_entries() -> Dict[int, Dict]:
    """Retrieves all clusters, their summaries, and their associated entries."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, summary FROM clusters") as cursor:
            clusters_rows = await cursor.fetchall()

        clusters = collections.defaultdict(lambda: {"summary": "", "entries": []})
        for row in clusters_rows:
            clusters[row['id']]['summary'] = row['summary']

        async with db.execute("SELECT id, content, metadata, cluster_id FROM playbook_entries WHERE cluster_id IS NOT NULL") as cursor:
            entries_rows = await cursor.fetchall()

        for row in entries_rows:
            entry = dict(row)
            entry['metadata'] = json.loads(entry['metadata'])
            clusters[row['cluster_id']]['entries'].append(entry)

    return dict(clusters)

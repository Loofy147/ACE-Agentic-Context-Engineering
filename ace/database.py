import aiosqlite
import json
from typing import List, Dict, Any, TYPE_CHECKING
import collections
import numpy as np

if TYPE_CHECKING:
    from ace.similarity import SimilarityService

DATABASE_PATH = "ace_playbook.db"

async def initialize_database():
    """
    Initializes the database by creating the necessary tables.

    This function sets up the database schema, creating the `playbook_entries`
    and `clusters` tables if they do not already exist. It should be called
    at the application's startup to ensure the database is ready for use.
    """
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

async def add_or_update_playbook_entry(entry_id: str, content: str, metadata: Dict[str, Any], embedding: bytes):
    """
    Adds a new entry to the playbook or updates an existing one.

    Inserts a new record into the `playbook_entries` table with the provided
    data. If an entry with the same ID already exists, it will be updated.
    The metadata dictionary is serialized to a JSON string before storage.

    Args:
        entry_id: The unique identifier for the new entry.
        content: The text content of the entry.
        metadata: A dictionary of metadata associated with the entry.
        embedding: The vector embedding of the content, as a byte string.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO playbook_entries (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
            (entry_id, content, json.dumps(metadata), embedding)
        )
        await db.commit()

async def get_all_playbook_entries() -> List[Dict[str, Any]]:
    """
    Retrieves all entries from the playbook.

    Fetches all records from the `playbook_entries` table and returns them as
    a list of dictionaries. The `metadata` field is deserialized from a JSON
    string back into a dictionary.

    Returns:
        A list of dictionaries, where each dictionary represents a playbook
        entry.
    """
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
    """
    Checks if an entry with the given content already exists in the playbook.

    Args:
        content: The content to check for.

    Returns:
        True if an entry with the specified content exists, False otherwise.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT 1 FROM playbook_entries WHERE content = ?", (content,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def update_entry_cluster(entry_id: str, cluster_id: int):
    """
    Updates the cluster ID for a specific playbook entry.

    Args:
        entry_id: The ID of the playbook entry to update.
        cluster_id: The new cluster ID to assign to the entry.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE playbook_entries SET cluster_id = ? WHERE id = ?", (cluster_id, entry_id))
        await db.commit()

async def add_or_update_cluster_summary(cluster_id: int, summary: str):
    """
    Adds a new cluster summary or updates an existing one.

    This function uses `INSERT OR REPLACE` to either create a new cluster
    summary or update the summary of an existing cluster.

    Args:
        cluster_id: The ID of the cluster.
        summary: The new summary for the cluster.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO clusters (id, summary) VALUES (?, ?)", (cluster_id, summary))
        await db.commit()

async def is_similar_embedding_present(
    similarity_service: 'SimilarityService',
    embedding: np.ndarray,
    batch_size: int = 100
) -> bool:
    """
    Checks if a similar embedding exists in the database, processing in batches.

    This function is designed to be memory-efficient by fetching and comparing
    embeddings in smaller batches rather than loading all of them into memory
    at once.

    Args:
        similarity_service: The similarity service to use for the check.
        embedding: The embedding to check for similarity.
        batch_size: The number of embeddings to fetch from the database at a time.

    Returns:
        True if a similar embedding is found, False otherwise.
    """
    offset = 0
    while True:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT embedding FROM playbook_entries WHERE embedding IS NOT NULL LIMIT ? OFFSET ?",
                (batch_size, offset)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            break

        existing_embeddings = [np.frombuffer(row['embedding'], dtype=np.float32) for row in rows]
        if similarity_service.is_similar(embedding, existing_embeddings):
            return True

        offset += batch_size

    return False

async def get_all_clusters_with_entries() -> Dict[int, Dict[str, Any]]:
    """
    Retrieves all clusters, their summaries, and their associated entries.

    This function queries the database to build a nested dictionary that maps
    cluster IDs to their summaries and a list of their member entries.

    Returns:
        A dictionary where keys are cluster IDs and values are dictionaries
        containing the cluster's summary and a list of its entries.
    """
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

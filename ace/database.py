import aiosqlite
import asyncpg
import json
from typing import List, Dict, Any, TYPE_CHECKING
import collections
import numpy as np

from ace.config import settings

if TYPE_CHECKING:
    from ace.similarity import SimilarityService

# Global variables for the database connections/pools
_pool = None
_sqlite_conn = None

async def db_connect():
    """Initializes the database connection."""
    global _pool, _sqlite_conn
    db_type = settings['database']['type']

    if db_type == "postgres" and _pool is None:
        db_settings = settings['database']['postgres']
        _pool = await asyncpg.create_pool(
            user=db_settings['user'],
            password=db_settings['password'],
            host=db_settings['host'],
            port=db_settings['port'],
            database=db_settings['database']
        )
    elif db_type == "sqlite" and _sqlite_conn is None:
        _sqlite_conn = await aiosqlite.connect(settings['database']['sqlite']['path'])

async def db_close():
    """Closes the database connection."""
    global _pool, _sqlite_conn
    if _pool:
        await _pool.close()
        _pool = None
    if _sqlite_conn:
        await _sqlite_conn.close()
        _sqlite_conn = None


async def initialize_database():
    """Initializes the database by creating the necessary tables."""
    db_type = settings['database']['type']
    if db_type == "sqlite":
        await _sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS playbook_entries (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL UNIQUE,
                metadata TEXT,
                embedding BLOB,
                cluster_id INTEGER
            )
        """)
        await _sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY,
                summary TEXT
            )
        """)
        await _sqlite_conn.commit()
    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS playbook_entries (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL UNIQUE,
                    metadata JSONB,
                    embedding BYTEA,
                    cluster_id INTEGER
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    id INTEGER PRIMARY KEY,
                    summary TEXT
                )
            """)

async def add_or_update_playbook_entry(entry_id: str, content: str, metadata: Dict[str, Any], embedding: bytes):
    """Adds a new entry to the playbook or updates an existing one."""
    db_type = settings['database']['type']
    if db_type == "sqlite":
        await _sqlite_conn.execute(
            "INSERT OR REPLACE INTO playbook_entries (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
            (entry_id, content, json.dumps(metadata), embedding)
        )
        await _sqlite_conn.commit()
    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO playbook_entries (id, content, metadata, embedding)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    embedding = EXCLUDED.embedding
            """, entry_id, content, json.dumps(metadata), embedding)


async def get_all_playbook_entries() -> List[Dict[str, Any]]:
    """Retrieves all entries from the playbook."""
    db_type = settings['database']['type']
    entries = []
    if db_type == "sqlite":
        _sqlite_conn.row_factory = aiosqlite.Row
        async with _sqlite_conn.execute("SELECT id, content, metadata, embedding FROM playbook_entries") as cursor:
            rows = await cursor.fetchall()
        for row in rows:
            entry = dict(row)
            entry['metadata'] = json.loads(entry['metadata'])
            entries.append(entry)
    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, content, metadata, embedding FROM playbook_entries")
        for row in rows:
            entry = dict(row)
            entries.append(entry)
    return entries

async def content_exists(content: str) -> bool:
    """Checks if an entry with the given content already exists in the playbook."""
    db_type = settings['database']['type']
    if db_type == "sqlite":
        async with _sqlite_conn.execute("SELECT 1 FROM playbook_entries WHERE content = ?", (content,)) as cursor:
            row = await cursor.fetchone()
            return row is not None
    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 FROM playbook_entries WHERE content = $1", content)
            return row is not None


async def update_entry_cluster(entry_id: str, cluster_id: int):
    """Updates the cluster ID for a specific playbook entry."""
    db_type = settings['database']['type']
    if db_type == "sqlite":
        await _sqlite_conn.execute("UPDATE playbook_entries SET cluster_id = ? WHERE id = ?", (cluster_id, entry_id))
        await _sqlite_conn.commit()
    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            await conn.execute("UPDATE playbook_entries SET cluster_id = $1 WHERE id = $2", cluster_id, entry_id)


async def add_or_update_cluster_summary(cluster_id: int, summary: str):
    """Adds a new cluster summary or updates an existing one."""
    db_type = settings['database']['type']
    if db_type == "sqlite":
        await _sqlite_conn.execute("INSERT OR REPLACE INTO clusters (id, summary) VALUES (?, ?)", (cluster_id, summary))
        await _sqlite_conn.commit()
    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO clusters (id, summary) VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE SET summary = EXCLUDED.summary
            """, cluster_id, summary)


async def is_similar_embedding_present(
    similarity_service: 'SimilarityService',
    embedding: np.ndarray,
    batch_size: int = 100
) -> bool:
    """Checks if a similar embedding exists in the database, processing in batches."""
    db_type = settings['database']['type']
    offset = 0
    while True:
        rows = []
        if db_type == "sqlite":
            _sqlite_conn.row_factory = aiosqlite.Row
            async with _sqlite_conn.execute(
                "SELECT embedding FROM playbook_entries WHERE embedding IS NOT NULL LIMIT ? OFFSET ?",
                (batch_size, offset)
            ) as cursor:
                rows = await cursor.fetchall()
        elif db_type == "postgres":
            async with _pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT embedding FROM playbook_entries WHERE embedding IS NOT NULL LIMIT $1 OFFSET $2",
                    batch_size, offset
                )

        if not rows:
            break

        existing_embeddings = [np.frombuffer(row['embedding'], dtype=np.float32) for row in rows]
        if similarity_service.is_similar(embedding, existing_embeddings):
            return True

        offset += batch_size

    return False

async def get_all_clusters_with_entries() -> Dict[int, Dict[str, Any]]:
    """Retrieves all clusters, their summaries, and their associated entries."""
    db_type = settings['database']['type']
    clusters = collections.defaultdict(lambda: {"summary": "", "entries": []})

    if db_type == "sqlite":
        _sqlite_conn.row_factory = aiosqlite.Row
        async with _sqlite_conn.execute("SELECT id, summary FROM clusters") as cursor:
            clusters_rows = await cursor.fetchall()
        for row in clusters_rows:
            clusters[row['id']]['summary'] = row['summary']

        async with _sqlite_conn.execute("SELECT id, content, metadata, cluster_id FROM playbook_entries WHERE cluster_id IS NOT NULL") as cursor:
            entries_rows = await cursor.fetchall()
        for row in entries_rows:
            entry = dict(row)
            entry['metadata'] = json.loads(entry['metadata'])
            clusters[row['cluster_id']]['entries'].append(entry)

    elif db_type == "postgres":
        async with _pool.acquire() as conn:
            clusters_rows = await conn.fetch("SELECT id, summary FROM clusters")
            for row in clusters_rows:
                clusters[row['id']]['summary'] = row['summary']

            entries_rows = await conn.fetch("SELECT id, content, metadata, cluster_id FROM playbook_entries WHERE cluster_id IS NOT NULL")
            for row in entries_rows:
                entry = dict(row)
                clusters[row['cluster_id']]['entries'].append(entry)

    return dict(clusters)

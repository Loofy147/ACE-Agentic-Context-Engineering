import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from ace import database

@dataclass
class PlaybookEntry:
    """
    Represents a single, atomic piece of knowledge or strategy in the playbook.

    This dataclass serves as the fundamental unit of information within the ACE
    framework. Each entry encapsulates a piece of content, which could be a
    strategy, a piece of code, a configuration setting, or any other form of
    knowledge.

    Attributes:
        id: A unique identifier for the entry, generated automatically.
        content: The text content of the entry.
        metadata: A dictionary for storing arbitrary metadata associated with
                  the entry, such as its source, type, or creation time.
        embedding: An optional byte string representing the vector embedding of
                   the content. This is used for semantic similarity checks.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[bytes] = None

class Playbook:
    """
    Represents the entire playbook, which is a collection of PlaybookEntry
    objects stored in a persistent database.

    The playbook acts as the central knowledge repository for the ACE framework.
    It is a dynamic entity, continuously updated and refined by the Curator.
    This class provides an asynchronous interface for interacting with the
    playbook data stored in the database.
    """

    def __init__(self):
        """
        Initializes the playbook.

        Note: The database connection and table creation should be handled
        separately at the application's startup.
        """
        pass

    async def add_entry(self, content: str, metadata: Optional[Dict[str, Any]] = None, embedding: Optional[bytes] = None, entry_id: Optional[str] = None) -> PlaybookEntry:
        """
        Asynchronously adds or updates an entry in the playbook.

        This method creates a new `PlaybookEntry` and persists it to the
        database. If an `entry_id` is provided, it will update the existing
        entry.

        Args:
            content: The text content of the new entry.
            metadata: An optional dictionary of metadata for the new entry.
            embedding: An optional byte string representing the vector
                       embedding of the content.
            entry_id: An optional string representing the ID of the entry to
                      update.

        Returns:
            The newly created or updated and persisted `PlaybookEntry` object.
        """
        if metadata is None:
            metadata = {}
        if entry_id is None:
            entry_id = str(uuid.uuid4())
        entry = PlaybookEntry(id=entry_id, content=content, metadata=metadata, embedding=embedding)
        await database.add_or_update_playbook_entry(entry.id, entry.content, entry.metadata, entry.embedding)
        return entry

    async def get_all_entries(self) -> List[PlaybookEntry]:
        """
        Asynchronously retrieves all entries from the playbook.

        Returns:
            A list of `PlaybookEntry` objects, representing all the entries
            currently stored in the database.
        """
        all_entries_data = await database.get_all_playbook_entries()
        return [PlaybookEntry(**data) for data in all_entries_data]

    async def get_entry(self, entry_id: str) -> Optional[PlaybookEntry]:
        """
        Asynchronously retrieves a specific entry from the playbook by its ID.

        Args:
            entry_id: The unique identifier of the entry to retrieve.

        Returns:
            The `PlaybookEntry` object if found, otherwise `None`.
        """
        # This is not the most efficient way to get a single entry.
        # A direct database query would be better.
        # For now, we'll keep it simple.
        all_entries = await self.get_all_entries()
        for entry in all_entries:
            if entry.id == entry_id:
                return entry
        return None

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ace import database

@dataclass
class PlaybookEntry:
    """
    Represents a single, atomic piece of knowledge or strategy in the playbook.

    Each entry has a unique ID, the content of the entry, and a dictionary for
    storing arbitrary metadata.

    Attributes:
        id: A unique identifier for the entry.
        content: The text content of the entry.
        metadata: A dictionary for storing metadata associated with the entry.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, any] = field(default_factory=dict)

class Playbook:
    """
    Represents the entire playbook, which is a collection of PlaybookEntry objects
    stored in a persistent database.

    The playbook is the central knowledge base for the ACE framework. It is
    dynamically updated by the Curator.
    """
    def __init__(self):
        """Initializes the playbook by ensuring the database is set up."""
        database.initialize_database()

    def add_entry(self, content: str, metadata: Optional[Dict[str, any]] = None) -> PlaybookEntry:
        """
        Adds a new entry to the playbook database.

        Args:
            content: The content of the new entry.
            metadata: An optional dictionary of metadata for the new entry.

        Returns:
            The newly created PlaybookEntry object.
        """
        if metadata is None:
            metadata = {}
        entry = PlaybookEntry(content=content, metadata=metadata)
        database.add_playbook_entry(entry.id, entry.content, entry.metadata)
        return entry

    def get_all_entries(self) -> List[PlaybookEntry]:
        """
        Retrieves all entries from the playbook database.

        Returns:
            A list of all PlaybookEntry objects from the database.
        """
        all_entries_data = database.get_all_playbook_entries()
        return [PlaybookEntry(**data) for data in all_entries_data]

    def get_entry(self, entry_id: str) -> Optional[PlaybookEntry]:
        """
        Retrieves an entry from the playbook by its ID.

        Args:
            entry_id: The ID of the entry to retrieve.

        Returns:
            The PlaybookEntry object if found, otherwise None.
        """
        all_entries = self.get_all_entries()
        for entry in all_entries:
            if entry.id == entry_id:
                return entry
        return None

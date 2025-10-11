import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

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

@dataclass
class Playbook:
    """
    Represents the entire playbook, which is a collection of PlaybookEntry objects.

    The playbook is the central knowledge base for the ACE framework. It is
    dynamically updated by the Curator.

    Attributes:
        entries: A list of PlaybookEntry objects.
    """
    entries: List[PlaybookEntry] = field(default_factory=list)

    def add_entry(self, content: str, metadata: Optional[Dict[str, any]] = None) -> PlaybookEntry:
        """
        Adds a new entry to the playbook.

        Args:
            content: The content of the new entry.
            metadata: An optional dictionary of metadata for the new entry.

        Returns:
            The newly created PlaybookEntry object.
        """
        if metadata is None:
            metadata = {}
        entry = PlaybookEntry(content=content, metadata=metadata)
        self.entries.append(entry)
        return entry

    def get_entry(self, entry_id: str) -> Optional[PlaybookEntry]:
        """
        Retrieves an entry from the playbook by its ID.

        Args:
            entry_id: The ID of the entry to retrieve.

        Returns:
            The PlaybookEntry object if found, otherwise None.
        """
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

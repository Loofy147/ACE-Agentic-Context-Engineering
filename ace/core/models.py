import uuid
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class PlaybookEntry:
    """Represents a single entry in the playbook."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, any] = field(default_factory=dict)

@dataclass
class Playbook:
    """Represents the entire playbook, a collection of entries."""
    entries: List[PlaybookEntry] = field(default_factory=list)

    def add_entry(self, content: str, metadata: Dict[str, any] = None):
        """Adds a new entry to the playbook."""
        if metadata is None:
            metadata = {}
        entry = PlaybookEntry(content=content, metadata=metadata)
        self.entries.append(entry)
        return entry

    def get_entry(self, entry_id: str) -> PlaybookEntry | None:
        """Retrieves an entry by its ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

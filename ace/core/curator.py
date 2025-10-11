from typing import Dict, List
from ace.core.models import Playbook
from ace import database

class Curator:
    """
    The Curator component of the ACE framework.

    The Curator is responsible for integrating insights from the Reflector into
    the playbook. It also handles tasks such as deduplication to maintain the
    quality and integrity of the playbook.
    """

    def curate(self, playbook: Playbook, insights: List[Dict[str, any]]):
        """
        Integrates a list of insights into the playbook, avoiding duplicates.

        This method iterates through a list of insights and adds them to the
        playbook, but only if an entry with the same content does not already
        exist in the database.

        Args:
            playbook: The playbook to be updated.
            insights: A list of insights to be added to the playbook. Each
                      insight is a dictionary with 'content' and 'metadata'.
        """
        for insight in insights:
            content = insight.get("content", "")
            if content and not database.content_exists(content):
                playbook.add_entry(
                    content=content,
                    metadata=insight.get("metadata", {})
                )

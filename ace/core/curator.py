from typing import Dict, List
from ace.core.models import Playbook

class Curator:
    """Integrates insights into the playbook."""

    def curate(self, playbook: Playbook, insights: List[Dict[str, any]]):
        """
        Integrates a list of insights into the playbook.

        Args:
            playbook: The playbook to update.
            insights: A list of insights to add to the playbook.
        """
        for insight in insights:
            playbook.add_entry(
                content=insight.get("content", ""),
                metadata=insight.get("metadata", {})
            )

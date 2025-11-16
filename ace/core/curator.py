import asyncio
from typing import Dict, List
from ace.core.models import Playbook
from ace import database
from ace.similarity import get_similarity_service
import numpy as np

class Curator:
    """
    The Curator component of the ACE framework.

    The Curator is responsible for integrating insights from the Reflector into
    the playbook. It also handles tasks such as deduplication to maintain the
    quality and integrity of the playbook.
    """

    def __init__(self, config: dict):
        """
        Initializes the Curator with a configuration.

        Args:
            config: A dictionary containing the application configuration.
        """
        self.similarity_service = get_similarity_service(config)
        self.lock = asyncio.Lock()

    async def curate(self, playbook: Playbook, insights: List[Dict[str, any]]):
        """
        Asynchronously integrates a list of insights into the playbook, using
        semantic deduplication to avoid conceptually similar entries.

        Args:
            playbook: The playbook to be updated.
            insights: A list of insights to be added to the playbook. Each
                      insight is a dictionary with 'content' and 'metadata'.
        """
        async with self.lock:
            all_entries = await playbook.get_all_entries()
            existing_embeddings = [np.frombuffer(e.embedding, dtype=np.float32) for e in all_entries if e.embedding]

            for insight in insights:
                content = insight.get("content", "")
                if content and not await database.content_exists(content):
                    embedding = self.similarity_service.get_embedding(content)
                    if not self.similarity_service.is_similar(embedding, existing_embeddings):
                        await playbook.add_entry(
                            content=content,
                            metadata=insight.get("metadata", {}),
                            embedding=embedding.tobytes()
                        )
                        existing_embeddings.append(embedding)

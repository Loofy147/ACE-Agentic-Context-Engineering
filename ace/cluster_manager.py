from typing import List, Dict
from ace import database
from ace.clustering import get_clustering_service
from ace.summarization import get_summarization_service
from ace.llm import LanguageModel
import collections

class ClusterManager:
    """
    Manages the clustering and summarization of playbook entries.
    """

    def __init__(self, config: dict, llm: LanguageModel):
        """
        Initializes the ClusterManager.

        Args:
            config: A dictionary containing the application configuration.
            llm: An instance of a class that implements the LanguageModel interface.
        """
        self.config = config
        self.clustering_service = get_clustering_service(config)
        self.summarization_service = get_summarization_service(llm)

    async def run_clustering(self):
        """
        Runs the clustering and summarization process.
        """
        entries = await database.get_all_playbook_entries()
        if not entries:
            return

        labels = self.clustering_service.cluster_entries(entries)

        # Group entries by cluster label
        clusters = collections.defaultdict(list)
        for i, entry in enumerate(entries):
            clusters[labels[i]].append(entry)

        # Update cluster IDs in the database
        for label, cluster_entries in clusters.items():
            # Convert numpy int to Python int for SQLite compatibility
            cluster_id = int(label)
            for entry in cluster_entries:
                await database.update_entry_cluster(entry['id'], cluster_id)

            # Summarize each cluster
            texts = [e['content'] for e in cluster_entries]
            summary = await self.summarization_service.summarize_cluster(texts)
            await database.add_or_update_cluster_summary(cluster_id, summary)

    async def get_clusters(self) -> Dict[int, Dict]:
        """
        Retrieves all clusters and their summaries.

        Returns:
            A dictionary where keys are cluster IDs and values are dictionaries
            containing the cluster's summary and its entries.
        """
        clusters_data = await database.get_all_clusters_with_entries()
        return clusters_data

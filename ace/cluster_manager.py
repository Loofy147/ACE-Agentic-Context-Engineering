from typing import List, Dict, Any
from ace import database
from ace.clustering import get_clustering_service
from ace.summarization import get_summarization_service
from ace.llm import LanguageModel
import collections

class ClusterManager:
    """
    Manages the clustering and summarization of playbook entries.

    This class orchestrates the process of grouping playbook entries into
    meaningful clusters and then generating a summary for each cluster. It
    uses the `ClusteringService` to perform the clustering and the
    `SummarizationService` to create the summaries.
    """

    def __init__(self, config: Dict[str, Any], llm: LanguageModel):
        """
        Initializes the ClusterManager.

        Args:
            config: A dictionary containing the application configuration.
            llm: An instance of a class that implements the `LanguageModel`
                 interface, to be used for summarization.
        """
        self.config = config
        self.clustering_service = get_clustering_service(config)
        self.summarization_service = get_summarization_service(llm)

    async def run_clustering(self):
        """
        Runs the full clustering and summarization process.

        This method fetches all playbook entries, clusters them based on their
        embeddings, and then generates and stores a summary for each cluster.
        The cluster assignments and summaries are updated in the database.
        """
        entries = await database.get_all_playbook_entries()
        if not entries:
            return

        labels = self.clustering_service.cluster_entries(entries)

        # Group entries by cluster label
        clusters = collections.defaultdict(list)
        for i, entry in enumerate(entries):
            clusters[labels[i]].append(entry)

        # Update cluster IDs and summarize each cluster
        for label, cluster_entries in clusters.items():
            # Ensure the cluster ID is a standard Python int for database compatibility
            cluster_id = int(label)

            # Update the cluster ID for each entry in the current cluster
            for entry in cluster_entries:
                await database.update_entry_cluster(entry['id'], cluster_id)

            # Generate and store the summary for the current cluster
            texts = [e['content'] for e in cluster_entries]
            summary = await self.summarization_service.summarize_cluster(texts)
            await database.add_or_update_cluster_summary(cluster_id, summary)

    async def get_clusters(self) -> Dict[int, Dict[str, Any]]:
        """
        Retrieves all clusters, their summaries, and their associated entries.

        This method queries the database to get a comprehensive view of all
        the clusters, including the summary of each cluster and the list of
        entries that belong to it.

        Returns:
            A dictionary where keys are cluster IDs and values are dictionaries
            containing the cluster's summary and its entries.
        """
        clusters_data = await database.get_all_clusters_with_entries()
        return clusters_data

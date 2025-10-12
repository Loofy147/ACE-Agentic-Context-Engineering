from sklearn.cluster import KMeans
import numpy as np
from typing import List, Dict

class ClusteringService:
    """
    A service for clustering playbook entries based on their vector embeddings.
    """

    def __init__(self, config: dict):
        """
        Initializes the ClusteringService.

        Args:
            config: A dictionary containing the application configuration.
        """
        self.config = config
        self.n_clusters = self.config.get('clustering', {}).get('n_clusters', 5)

    def cluster_entries(self, entries: List[Dict]) -> List[int]:
        """
        Clusters a list of playbook entries using KMeans.

        Args:
            entries: A list of playbook entries, where each entry has an 'embedding' key.

        Returns:
            A list of cluster labels corresponding to each entry.
        """
        embeddings = [np.frombuffer(e['embedding'], dtype=np.float32) for e in entries if e['embedding']]
        if not embeddings:
            return []

        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        return kmeans.labels_

clustering_service = None

def get_clustering_service(config: dict) -> ClusteringService:
    """
    Returns a singleton instance of the ClusteringService.
    """
    global clustering_service
    if clustering_service is None:
        clustering_service = ClusteringService(config)
    return clustering_service

from sklearn.cluster import KMeans
import numpy as np
from typing import List, Dict, Any

class ClusteringService:
    """
    A service for clustering playbook entries based on their vector embeddings.

    This class uses the KMeans algorithm from scikit-learn to group playbook
    entries into a pre-defined number of clusters. The clustering is performed
    based on the semantic similarity of the entries, as captured by their
    vector embeddings.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the ClusteringService.

        The number of clusters is determined by the `n_clusters` setting in the
        application's configuration. If not specified, it defaults to 5.

        Args:
            config: A dictionary containing the application configuration.
        """
        self.config = config
        self.n_clusters = self.config.get('clustering', {}).get('n_clusters', 5)

    def cluster_entries(self, entries: List[Dict[str, Any]]) -> List[int]:
        """
        Clusters a list of playbook entries using the KMeans algorithm.

        This method extracts the vector embeddings from the provided list of
        entries and then applies KMeans clustering to group them. If the number
        of entries with embeddings is less than the configured number of
        clusters, the number of clusters is adjusted to match the number of
        entries.

        Args:
            entries: A list of playbook entries, where each entry is a
                     dictionary that should contain an 'embedding' key.

        Returns:
            A list of cluster labels, where each label corresponds to an entry
            in the input list.
        """
        embeddings = [np.frombuffer(e['embedding'], dtype=np.float32) for e in entries if e['embedding']]
        if not embeddings:
            return []

        n_clusters = self.n_clusters
        if len(embeddings) < n_clusters:
            n_clusters = len(embeddings)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        return kmeans.labels_.tolist()

# A global singleton instance of the ClusteringService.
_clustering_service = None

def get_clustering_service(config: Dict[str, Any]) -> ClusteringService:
    """
    Returns a singleton instance of the ClusteringService.

    This function ensures that there is only one instance of the
    `ClusteringService` throughout the application's lifecycle.

    Args:
        config: The application's configuration dictionary.

    Returns:
        A singleton instance of the `ClusteringService`.
    """
    global _clustering_service
    if _clustering_service is None:
        _clustering_service = ClusteringService(config)
    return _clustering_service

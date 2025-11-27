import unittest
import numpy as np
import asyncio
import os
from ace.config import settings
from ace.clustering import ClusteringService
from ace.summarization import SummarizationService
from ace.cluster_manager import ClusterManager
from ace.llm import get_language_model
from ace import database
from ace.core.models import Playbook

class TestClusteringFeatures(unittest.TestCase):
    """
    Tests for the clustering and summarization features.

    This test suite covers the `ClusteringService`, `SummarizationService`,
    and the `ClusterManager` to ensure that playbook entries are correctly
    grouped and summarized.
    """

    def setUp(self):
        """
        Set up the test environment.

        Initializes a test database, a mock configuration, and the services
        needed for clustering and summarization.
        """
        database.DATABASE_PATH = "test_playbook.db"
        self.config = settings.copy()
        self.config.update({
            'clustering': {'n_clusters': 2},
            'language_model': {'name': 'mock', 'mock': {'responses': ['Summary of cluster']}}
        })
        self.clustering_service = ClusteringService(self.config)
        self.llm = get_language_model(self.config)
        self.summarization_service = SummarizationService(self.llm)
        self.playbook = Playbook()

    def tearDown(self):
        """
        Clean up the test environment.

        Removes the test database file after each test.
        """
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_clustering_service(self):
        """
        Tests the basic functionality of the ClusteringService.

        Verifies that entries with similar embeddings are grouped into the
        same cluster, and entries with dissimilar embeddings are in different
        clusters.
        """
        embeddings = [
            np.array([1.0, 1.0, 1.0]), np.array([1.1, 1.0, 1.1]),
            np.array([-1.0, -1.0, -1.0]), np.array([-1.1, -1.0, -1.1]),
        ]
        entries = [{'embedding': e.tobytes()} for e in embeddings]
        labels = self.clustering_service.cluster_entries(entries)
        self.assertEqual(len(labels), 4)
        self.assertEqual(labels[0], labels[1])
        self.assertEqual(labels[2], labels[3])
        self.assertNotEqual(labels[0], labels[2])

    def test_summarization_service(self):
        """
        Tests the basic functionality of the SummarizationService.

        Ensures that the service can generate a summary for a list of texts
        using the mock language model.
        """
        async def _test():
            texts = ["This is the first text.", "This is the second text."]
            summary = await self.summarization_service.summarize_cluster(texts)
            self.assertEqual(summary, "Summary of cluster")
        asyncio.run(_test())

    def test_clustering_with_fewer_entries_than_clusters(self):
        """
        Tests that clustering works correctly when there are fewer entries
        than the configured number of clusters.
        """
        embeddings = [np.array([1.0, 1.0, 1.0])]
        entries = [{'embedding': e.tobytes()} for e in embeddings]
        labels = self.clustering_service.cluster_entries(entries)
        self.assertEqual(len(labels), 1)

    def test_cluster_manager(self):
        """
        Tests the end-to-end clustering and summarization process.

        This test verifies that the `ClusterManager` can successfully
        orchestrate the clustering of playbook entries and the generation of
        summaries for each cluster.
        """
        async def _test():
            await database.initialize_database()

            # Add entries with distinct embeddings
            embedding1 = np.array([1.0, 1.0, 1.0]).tobytes()
            embedding2 = np.array([-1.0, -1.0, -1.0]).tobytes()
            await self.playbook.add_entry("Entry 1", {}, embedding1)
            await self.playbook.add_entry("Entry 2", {}, embedding2)

            # Run the clustering and summarization process
            manager = ClusterManager(self.config, self.llm)
            await manager.run_clustering()

            # Verify the results
            clusters = await manager.get_clusters()
            self.assertEqual(len(clusters), 2)
            self.assertEqual(len(clusters[0]['entries']), 1)
            self.assertEqual(len(clusters[1]['entries']), 1)
            self.assertEqual(clusters[0]['summary'], 'Summary of cluster')
            self.assertEqual(clusters[1]['summary'], 'Summary of cluster')

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np
import asyncio
import os
import yaml
from ace.clustering import ClusteringService
from ace.summarization import SummarizationService
from ace.cluster_manager import ClusterManager
from ace.llm import get_language_model
from ace import database
from ace.core.models import Playbook

class TestClusteringFeatures(unittest.TestCase):
    """Tests for the ClusteringService."""

    def setUp(self):
        """Set up a dummy config and clean database for each test."""
        database.DATABASE_PATH = "test_playbook.db"
        self.config = {
            'clustering': {'n_clusters': 2},
            'language_model': {'name': 'mock', 'mock': {'responses': ['Summary of cluster']}}
        }
        self.clustering_service = ClusteringService(self.config)
        self.llm = get_language_model(self.config)
        self.summarization_service = SummarizationService(self.llm)
        self.playbook = Playbook()

    def tearDown(self):
        """Remove the test database after each test."""
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_clustering_service(self):
        """Tests the clustering of entries."""
        # Create some dummy embeddings that are clearly separated
        embeddings = [
            np.array([1.0, 1.0, 1.0]),
            np.array([1.1, 1.0, 1.1]),
            np.array([-1.0, -1.0, -1.0]),
            np.array([-1.1, -1.0, -1.1]),
        ]
        entries = [{'embedding': e.tobytes()} for e in embeddings]

        labels = self.clustering_service.cluster_entries(entries)

        self.assertEqual(len(labels), 4)
        self.assertEqual(labels[0], labels[1])
        self.assertEqual(labels[2], labels[3])
        self.assertNotEqual(labels[0], labels[2])

    def test_summarization_service(self):
        """Tests the summarization of a cluster."""
        async def _test():
            texts = ["This is the first text.", "This is the second text."]
            summary = await self.summarization_service.summarize_cluster(texts)
            self.assertEqual(summary, "Summary of cluster")
        asyncio.run(_test())

    def test_cluster_manager(self):
        """Tests the full clustering and summarization process."""
        async def _test():
            await database.initialize_database()

            # Add some entries
            embedding1 = np.array([1.0, 1.0, 1.0]).tobytes()
            embedding2 = np.array([-1.0, -1.0, -1.0]).tobytes()
            await self.playbook.add_entry("Entry 1", {}, embedding1)
            await self.playbook.add_entry("Entry 2", {}, embedding2)

            manager = ClusterManager(self.config, self.llm)
            await manager.run_clustering()

            clusters = await manager.get_clusters()

            self.assertEqual(len(clusters), 2)
            # Check that each cluster has one entry
            self.assertEqual(len(clusters[0]['entries']), 1)
            self.assertEqual(len(clusters[1]['entries']), 1)
            self.assertEqual(clusters[0]['summary'], 'Summary of cluster')

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

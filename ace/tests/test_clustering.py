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
    """
    DB_PATH = "test_playbook.db"

    def setUp(self):
        """
        Set up the test environment.
        """
        settings['database'] = {
            'type': 'sqlite',
            'sqlite': {
                'path': self.DB_PATH
            }
        }
        settings.update({
            'clustering': {'n_clusters': 2},
            'language_model': {'name': 'mock', 'mock': {'responses': ['Summary of cluster']}}
        })
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

        asyncio.run(database.db_connect())
        asyncio.run(database.initialize_database())

        self.clustering_service = ClusteringService(settings)
        self.llm = get_language_model(settings)
        self.summarization_service = SummarizationService(self.llm)
        self.playbook = Playbook()

    def tearDown(self):
        """
        Clean up the test environment.
        """
        asyncio.run(database.db_close())
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

    def test_clustering_service(self):
        """
        Tests the basic functionality of the ClusteringService.
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
        """
        async def _test():
            # Add entries with distinct embeddings
            embedding1 = np.array([1.0, 1.0, 1.0]).tobytes()
            embedding2 = np.array([-1.0, -1.0, -1.0]).tobytes()
            await self.playbook.add_entry("Entry 1", {}, embedding1)
            await self.playbook.add_entry("Entry 2", {}, embedding2)

            # Run the clustering and summarization process
            manager = ClusterManager(settings, self.llm)
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

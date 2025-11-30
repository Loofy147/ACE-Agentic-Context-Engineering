import unittest
import os
import asyncio
from unittest.mock import patch, AsyncMock
from ace.config import settings
from ace.core.models import Playbook
from ace.core.curator import Curator
from ace import database

class TestCurator(unittest.TestCase):
    """
    Tests for the Curator component.
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
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

        asyncio.run(database.db_connect())
        asyncio.run(database.initialize_database())

        self.playbook = Playbook()
        self.curator = Curator(config=settings)

    def tearDown(self):
        """
        Clean up the test environment.
        """
        asyncio.run(database.db_close())
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

    def test_deduplication(self):
        """
        Ensures the Curator does not add semantically similar insights.
        """
        async def _test():
            # Define semantically similar and distinct insights
            insight1 = {"content": "How do I install Python?", "metadata": {}}
            insight2 = {"content": "What is the process for installing Python?", "metadata": {}}
            insight3 = {"content": "How do I write a function in Python?", "metadata": {}}
            insights = [insight1, insight2, insight3]

            # Curate the insights
            await self.curator.curate(self.playbook, insights)

            # Assert that only the non-similar insights were added
            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 2)
            self.assertEqual(all_entries[0].content, "How do I install Python?")
            self.assertEqual(all_entries[1].content, "How do I write a function in Python?")

        asyncio.run(_test())

    def test_empty_content(self):
        """
        Ensures the Curator does not add insights with empty content.
        """
        async def _test():
            insights = [{"content": "", "metadata": {}}, {"content": "A valid insight", "metadata": {}}]
            await self.curator.curate(self.playbook, insights)
            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)
            self.assertEqual(all_entries[0].content, "A valid insight")

        asyncio.run(_test())

    def test_curator_race_condition(self):
        """
        Tests that the Curator handles race conditions gracefully.
        """
        async def _test():
            # Define two semantically similar insights
            insight1 = [{"content": "How do I install Python?", "metadata": {}}]
            insight2 = [{"content": "What is the process for installing Python?", "metadata": {}}]

            # Run curate concurrently for both insights
            await asyncio.gather(
                self.curator.curate(self.playbook, insight1),
                self.curator.curate(self.playbook, insight2),
            )

            # Assert that only one of the insights was added
            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)

        asyncio.run(_test())

    @patch('ace.database.is_similar_embedding_present', new_callable=AsyncMock)
    def test_batched_similarity_check(self, mock_is_similar):
        """
        Tests that the Curator uses the optimized batched similarity check.
        """
        async def _test():
            # Mock the similarity check to control the outcome
            mock_is_similar.side_effect = [True, False]
            insights = [{"content": "Insight 1", "metadata": {}}, {"content": "Insight 2", "metadata": {}}]
            await self.curator.curate(self.playbook, insights)
            self.assertEqual(mock_is_similar.call_count, 2)
            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)
            self.assertEqual(all_entries[0].content, "Insight 2")

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

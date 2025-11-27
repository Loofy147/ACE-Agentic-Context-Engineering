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

    This suite validates the Curator's ability to manage the playbook,
    including its core functionality of semantic deduplication and handling
    of various edge cases.
    """

    def setUp(self):
        """
        Set up the test environment.

        Initializes a test database, configuration, and a Curator instance.
        """
        database.DATABASE_PATH = "test_playbook.db"
        self.config = settings
        self.playbook = Playbook()
        self.curator = Curator(config=self.config)

    def tearDown(self):
        """
        Clean up the test environment.

        Removes the test database file after each test.
        """
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_deduplication(self):
        """
        Ensures the Curator does not add semantically similar insights.

        This test verifies that if two insights are conceptually similar,
        only the first one is added to the playbook.
        """
        async def _test():
            await database.initialize_database()

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
            await database.initialize_database()
            insights = [{"content": "", "metadata": {}}, {"content": "A valid insight", "metadata": {}}]

            await self.curator.curate(self.playbook, insights)

            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)
            self.assertEqual(all_entries[0].content, "A valid insight")

        asyncio.run(_test())

    def test_curator_race_condition(self):
        """
        Tests that the Curator handles race conditions gracefully.

        This test simulates a scenario where multiple instances of the Curator
        are trying to add semantically similar insights at the same time.
        It verifies that the Curator's locking mechanism prevents duplicates.
        """
        async def _test():
            await database.initialize_database()

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
        Tests that the Curator uses the optimized batched similarity check
        from the database layer.
        """
        async def _test():
            await database.initialize_database()

            # Mock the similarity check to control the outcome
            mock_is_similar.side_effect = [True, False]

            insights = [{"content": "Insight 1", "metadata": {}}, {"content": "Insight 2", "metadata": {}}]
            await self.curator.curate(self.playbook, insights)

            # Verify that the similarity check was called for each insight
            self.assertEqual(mock_is_similar.call_count, 2)

            # Verify that only the non-similar insight was added
            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)
            self.assertEqual(all_entries[0].content, "Insight 2")

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

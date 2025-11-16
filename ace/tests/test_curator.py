import unittest
import os
import asyncio
from ace.config import settings
from ace.core.models import Playbook
from ace.core.curator import Curator
from ace import database

class TestCurator(unittest.TestCase):
    """Tests for the Curator component."""

    def setUp(self):
        """Set up the test configuration."""
        database.DATABASE_PATH = "test_playbook.db"
        self.config = settings
        self.playbook = Playbook()
        self.curator = Curator(config=self.config)

    def tearDown(self):
        """Remove the test database after each test."""
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_deduplication(self):
        """Ensures the curator does not add semantically similar insights."""
        async def _test():
            await database.initialize_database()

            # These two are semantically similar
            insight1 = {"content": "How do I install Python?", "metadata": {}}
            insight2 = {"content": "What is the process for installing Python?", "metadata": {}}

            # This one is different
            insight3 = {"content": "How do I write a function in Python?", "metadata": {}}

            insights = [insight1, insight2, insight3]

            await self.curator.curate(self.playbook, insights)

            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 2)
            self.assertEqual(all_entries[0].content, "How do I install Python?")
            self.assertEqual(all_entries[1].content, "How do I write a function in Python?")

        asyncio.run(_test())

    def test_empty_content(self):
        """Ensures the curator does not add insights with empty content."""
        async def _test():
            await database.initialize_database()
            insights = [
                {"content": "", "metadata": {}},
                {"content": "A valid insight", "metadata": {}},
            ]

            await self.curator.curate(self.playbook, insights)

            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)
            self.assertEqual(all_entries[0].content, "A valid insight")

        asyncio.run(_test())

    def test_curator_race_condition(self):
        """Tests that the Curator handles race conditions gracefully."""
        async def _test():
            await database.initialize_database()

            # These two are semantically similar
            insight1 = [{"content": "How do I install Python?", "metadata": {}}]
            insight2 = [{"content": "What is the process for installing Python?", "metadata": {}}]

            # Run curate concurrently
            await asyncio.gather(
                self.curator.curate(self.playbook, insight1),
                self.curator.curate(self.playbook, insight2),
            )

            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

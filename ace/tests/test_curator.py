import unittest
import os
import asyncio
from ace.core.models import Playbook
from ace.core.curator import Curator
from ace import database

class TestCurator(unittest.TestCase):
    """Tests for the Curator component."""

    def setUp(self):
        """Set up the test configuration."""
        database.DATABASE_PATH = "test_playbook.db"
        self.playbook = Playbook()
        self.curator = Curator()

    def tearDown(self):
        """Remove the test database after each test."""
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_deduplication(self):
        """Ensures the curator does not add duplicate insights."""
        async def _test():
            await database.initialize_database()
            insights = [
                {"content": "Unique insight 1", "metadata": {}},
                {"content": "Unique insight 2", "metadata": {}},
                {"content": "Unique insight 1", "metadata": {}},  # Duplicate
            ]

            await self.curator.curate(self.playbook, insights)

            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 2)
            self.assertEqual(all_entries[0].content, "Unique insight 1")
            self.assertEqual(all_entries[1].content, "Unique insight 2")

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

if __name__ == '__main__':
    unittest.main()

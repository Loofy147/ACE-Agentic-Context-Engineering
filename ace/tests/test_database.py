import unittest
import os
import asyncio
from ace import database

class TestDatabase(unittest.TestCase):
    """Tests for the database layer."""

    def setUp(self):
        """Set up the test configuration."""
        database.DATABASE_PATH = "test_playbook.db"

    def tearDown(self):
        """Remove the test database after each test."""
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_metadata_serialization(self):
        """Tests that metadata is correctly serialized and deserialized."""
        async def _test():
            await database.initialize_database()

            metadata = {"source": "test", "value": "some_value"}
            await database.add_playbook_entry(
                "test_id", "test_content", metadata, b"test_embedding"
            )

            entries = await database.get_all_playbook_entries()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["metadata"], metadata)

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

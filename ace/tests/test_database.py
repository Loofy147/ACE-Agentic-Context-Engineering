import unittest
import os
import asyncio
from ace import database
from ace.config import settings
from typing import Dict, Any

class TestDatabase(unittest.TestCase):
    """
    Tests for the database layer.

    This test suite verifies the functionality of the database operations,
    such as data serialization and deserialization, to ensure data integrity.
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


    def tearDown(self):
        """
        Clean up the test environment.
        """
        asyncio.run(database.db_close())
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

    def test_metadata_serialization(self):
        """
        Tests that metadata is correctly serialized to JSON and deserialized.
        """
        async def _test():
            # Define metadata to be stored
            metadata: Dict[str, Any] = {"source": "test", "value": "some_value", "number": 123}

            # Add an entry with the metadata
            await database.add_or_update_playbook_entry(
                "test_id", "test_content", metadata, b"test_embedding"
            )

            # Retrieve the entry and verify the metadata
            entries = await database.get_all_playbook_entries()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["metadata"], metadata)

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

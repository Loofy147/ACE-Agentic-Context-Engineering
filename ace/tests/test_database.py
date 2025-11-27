import unittest
import os
import asyncio
from ace import database
from typing import Dict, Any

class TestDatabase(unittest.TestCase):
    """
    Tests for the database layer.

    This test suite verifies the functionality of the database operations,
    such as data serialization and deserialization, to ensure data integrity.
    """

    def setUp(self):
        """
        Set up the test environment.

        Configures a separate test database for each test.
        """
        database.DATABASE_PATH = "test_playbook.db"

    def tearDown(self):
        """
        Clean up the test environment.

        Removes the test database file after each test to ensure a clean state.
        """
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_metadata_serialization(self):
        """
        Tests that metadata is correctly serialized to JSON and deserialized.

        This test ensures that the metadata dictionary, which is stored as a
        JSON string in the database, is correctly retrieved and converted
        back into a dictionary.
        """
        async def _test():
            await database.initialize_database()

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

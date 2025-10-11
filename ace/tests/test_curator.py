import unittest
import os
from ace.core.models import Playbook
from ace.core.curator import Curator
from ace import database

class TestCurator(unittest.TestCase):
    """Tests for the Curator component."""

    def setUp(self):
        """Set up a clean database for each test."""
        database.DATABASE_PATH = "test_playbook.db"
        database.initialize_database()
        self.playbook = Playbook()
        self.curator = Curator()

    def tearDown(self):
        """Remove the test database after each test."""
        os.remove(database.DATABASE_PATH)

    def test_deduplication(self):
        """Ensures the curator does not add duplicate insights."""
        insights = [
            {"content": "Unique insight 1", "metadata": {}},
            {"content": "Unique insight 2", "metadata": {}},
            {"content": "Unique insight 1", "metadata": {}},  # Duplicate
        ]

        self.curator.curate(self.playbook, insights)

        all_entries = self.playbook.get_all_entries()
        self.assertEqual(len(all_entries), 2)
        self.assertEqual(all_entries[0].content, "Unique insight 1")
        self.assertEqual(all_entries[1].content, "Unique insight 2")

    def test_empty_content(self):
        """Ensures the curator does not add insights with empty content."""
        insights = [
            {"content": "", "metadata": {}},
            {"content": "A valid insight", "metadata": {}},
        ]

        self.curator.curate(self.playbook, insights)

        all_entries = self.playbook.get_all_entries()
        self.assertEqual(len(all_entries), 1)
        self.assertEqual(all_entries[0].content, "A valid insight")

if __name__ == '__main__':
    unittest.main()

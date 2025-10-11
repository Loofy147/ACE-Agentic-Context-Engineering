import unittest
from ace.core.models import Playbook
from ace.core.curator import Curator

class TestCurator(unittest.TestCase):
    """Tests for the Curator component."""

    def setUp(self):
        """Set up a new playbook and curator for each test."""
        self.playbook = Playbook()
        self.curator = Curator()

    def test_deduplication(self):
        """Ensures the curator does not add duplicate insights."""
        insights = [
            {"content": "Unique insight 1", "metadata": {}},
            {"content": "Unique insight 2", "metadata": {}},
            {"content": "Unique insight 1", "metadata": {}},  # Duplicate
        ]

        self.curator.curate(self.playbook, insights)

        self.assertEqual(len(self.playbook.entries), 2)
        self.assertEqual(self.playbook.entries[0].content, "Unique insight 1")
        self.assertEqual(self.playbook.entries[1].content, "Unique insight 2")

    def test_empty_content(self):
        """Ensures the curator does not add insights with empty content."""
        insights = [
            {"content": "", "metadata": {}},
            {"content": "A valid insight", "metadata": {}},
        ]

        self.curator.curate(self.playbook, insights)

        self.assertEqual(len(self.playbook.entries), 1)
        self.assertEqual(self.playbook.entries[0].content, "A valid insight")

if __name__ == '__main__':
    unittest.main()

import unittest
import os
import asyncio
from unittest.mock import AsyncMock
from ace.config import settings
from ace.core.models import Playbook
from ace.self_healing import SelfHealing
from ace import database
from ace.llm import get_language_model
from ace.similarity import get_similarity_service

class TestSelfHealing(unittest.TestCase):
    """
    Tests for the SelfHealing component.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        database.DATABASE_PATH = "test_playbook.db"
        self.config = settings
        self.config['language_model']['name'] = 'mock'
        self.playbook = Playbook()
        self.similarity_service = get_similarity_service(self.config)

    def tearDown(self):
        """
        Clean up the test environment.
        """
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_analyze_and_correct(self):
        """
        Tests that the self-healing process can correct an outdated entry.
        """
        async def _test():
            await database.initialize_database()

            # Add an outdated entry to the playbook
            entry = await self.playbook.add_entry("Old content", {})

            # Setup the mock LLM to return a corrected version
            llm = get_language_model(self.config)
            llm.generate = AsyncMock(return_value="New content")

            # Run the self-healing process
            self_healing = SelfHealing(llm, self.playbook, self.similarity_service)
            await self_healing.analyze_and_correct()

            # Verify that the entry was corrected
            all_entries = await self.playbook.get_all_entries()
            self.assertEqual(len(all_entries), 1)
            self.assertEqual(all_entries[0].id, entry.id)
            self.assertEqual(all_entries[0].content, "New content")
            self.assertEqual(all_entries[0].metadata["source"], "self-healing")

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

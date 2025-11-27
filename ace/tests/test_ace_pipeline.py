import unittest
import os
import asyncio
from unittest.mock import AsyncMock
from ace.config import settings
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace import database
from ace.llm import get_language_model

class TestAcePipeline(unittest.TestCase):
    """
    Tests the full ACE pipeline, ensuring the integration of all components.

    This test suite validates the end-to-end functionality of the ACE
    framework, from generating a trajectory to curating the resulting
    insights into the playbook.
    """

    def setUp(self):
        """
        Set up the test environment.

        This method configures a separate test database and ensures that the
        mock language model is used for predictable test outcomes.
        """
        database.DATABASE_PATH = "test_playbook.db"
        self.config = settings
        self.config['language_model']['name'] = 'mock'

    def tearDown(self):
        """
        Clean up the test environment.

        This method removes the test database file after each test to ensure
        a clean state for subsequent tests.
        """
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_pipeline(self):
        """
        Tests the successful integration of Generator, Reflector, and Curator.

        This test simulates a complete run of the ACE pipeline. It verifies
        that a task is processed, insights are generated and reflected upon,
        and the playbook is updated as expected.
        """
        async def _test():
            await database.initialize_database()

            # 1. Setup components
            playbook = Playbook()
            llm = get_language_model(self.config)
            generator = Generator(llm=llm)
            reflector = Reflector(llm=llm)
            curator = Curator(config=self.config)

            # 2. Verify initial state
            self.assertEqual(len(await playbook.get_all_entries()), 0)

            # 3. Run the pipeline
            task = "Test task"
            trajectory = await generator.generate_trajectory(playbook, task)
            insights = await reflector.reflect(trajectory)
            await curator.curate(playbook, insights)

            # 4. Assert the final state
            all_entries = await playbook.get_all_entries()
            self.assertEqual(len(all_entries), 2)
            self.assertEqual(all_entries[0].content, "Cats are independent animals.")
            self.assertEqual(all_entries[1].content, "Dogs are loyal companions.")

        asyncio.run(_test())

    def test_reflector_malformed_json(self):
        """
        Tests that the Reflector handles malformed JSON responses gracefully.

        This test ensures that if the language model returns a response that
        is not valid JSON, the Reflector does not crash and instead returns
        an empty list of insights.
        """
        async def _test():
            await database.initialize_database()

            # 1. Setup Reflector with a mock LLM
            llm = get_language_model(self.config)
            llm.generate = AsyncMock(return_value="this is not valid json")
            reflector = Reflector(llm=llm)

            # 2. Run reflect and assert it returns an empty list
            trajectory = "Test trajectory"
            insights = await reflector.reflect(trajectory)
            self.assertEqual(insights, [])

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

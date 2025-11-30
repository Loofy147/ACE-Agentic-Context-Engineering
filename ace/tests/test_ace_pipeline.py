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
        settings['language_model']['name'] = 'mock'
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

    def test_pipeline(self):
        """
        Tests the successful integration of Generator, Reflector, and Curator.
        """
        async def _test():
            # 1. Setup components
            playbook = Playbook()
            llm = get_language_model(settings)
            generator = Generator(llm=llm)
            reflector = Reflector(llm=llm)
            curator = Curator(config=settings)

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
        """
        async def _test():
            # 1. Setup Reflector with a mock LLM
            llm = get_language_model(settings)
            llm.generate = AsyncMock(return_value="this is not valid json")
            reflector = Reflector(llm=llm)

            # 2. Run reflect and assert it returns an empty list
            trajectory = "Test trajectory"
            insights = await reflector.reflect(trajectory)
            self.assertEqual(insights, [])

        asyncio.run(_test())

if __name__ == '__main__':
    unittest.main()

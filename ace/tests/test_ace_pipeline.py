import unittest
import yaml
import os
import asyncio
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace import database
from ace.llm import get_language_model

class TestAcePipeline(unittest.TestCase):
    """Tests the full ACE pipeline."""

    def setUp(self):
        """Set up the test configuration."""
        database.DATABASE_PATH = "test_playbook.db"
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        # Ensure the test uses the mock model
        self.config['language_model']['name'] = 'mock'

    def tearDown(self):
        """Remove the test database after each test."""
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_pipeline(self):
        """Tests the integration of Generator, Reflector, and Curator."""
        async def _test():
            await database.initialize_database()
            # 1. Setup
            playbook = Playbook()
            llm = get_language_model(self.config)
            generator = Generator(llm=llm)
            reflector = Reflector(llm=llm)
            curator = Curator(config=self.config)

            # 2. Initial state
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
        """Tests that the Reflector handles malformed JSON gracefully."""
        async def _test():
            await database.initialize_database()
            # 1. Setup
            llm = get_language_model(self.config)
            # Mock the LLM to return malformed JSON
            llm.generate = unittest.mock.AsyncMock(return_value="this is not json")
            reflector = Reflector(llm=llm)

            # 2. Run reflect and assert it doesn't crash
            trajectory = "Test trajectory"
            insights = await reflector.reflect(trajectory)
            self.assertEqual(insights, [])

        asyncio.run(_test())


if __name__ == '__main__':
    unittest.main()

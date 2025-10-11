import unittest
import yaml
import os
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace import database

class MockModel:
    """A mock model for testing purposes."""
    def generate(self, prompt: str) -> str:
        return f"Mocked response for prompt: {prompt}"

class TestAcePipeline(unittest.TestCase):
    """Tests the full ACE pipeline."""

    def setUp(self):
        """Set up a clean database for each test."""
        database.DATABASE_PATH = "test_playbook.db"
        database.initialize_database()
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

    def tearDown(self):
        """Remove the test database after each test."""
        os.remove(database.DATABASE_PATH)

    def test_pipeline(self):
        """Tests the integration of Generator, Reflector, and Curator."""
        # 1. Setup
        playbook = Playbook()
        mock_model = MockModel()
        generator = Generator(model=mock_model, config=self.config)
        reflector = Reflector(model=mock_model, config=self.config)
        curator = Curator()

        # 2. Initial state
        self.assertEqual(len(playbook.get_all_entries()), 0)

        # 3. Run the pipeline
        task = "Test task"
        trajectory = generator.generate_trajectory(playbook, task)
        insights = reflector.reflect(trajectory)
        curator.curate(playbook, insights)

        # 4. Assert the final state
        all_entries = playbook.get_all_entries()
        self.assertEqual(len(all_entries), 3)
        entry1 = all_entries[0]
        self.assertIn("When analyzing task requirements", entry1.content)
        self.assertEqual(entry1.metadata["source"], "reflector")
        entry2 = all_entries[1]
        self.assertIn("Consulting the playbook", entry2.content)
        self.assertEqual(entry2.metadata["source"], "reflector")

if __name__ == '__main__':
    unittest.main()

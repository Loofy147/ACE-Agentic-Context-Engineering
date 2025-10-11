import unittest
import yaml
import os
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace import database
from ace.llm import get_language_model

class TestAcePipeline(unittest.TestCase):
    """Tests the full ACE pipeline."""

    def setUp(self):
        """Set up a clean database and load the test configuration."""
        database.DATABASE_PATH = "test_playbook.db"
        database.initialize_database()
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        # Ensure the test uses the mock model
        self.config['language_model']['name'] = 'mock'

    def tearDown(self):
        """Remove the test database after each test."""
        os.remove(database.DATABASE_PATH)

    def test_pipeline(self):
        """Tests the integration of Generator, Reflector, and Curator."""
        # 1. Setup
        playbook = Playbook()
        llm = get_language_model(self.config)
        generator = Generator(llm=llm)
        reflector = Reflector(llm=llm)
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
        self.assertEqual(len(all_entries), 2)
        self.assertEqual(all_entries[0].content, "Mock insight 1")
        self.assertEqual(all_entries[1].content, "Mock insight 2")

if __name__ == '__main__':
    unittest.main()

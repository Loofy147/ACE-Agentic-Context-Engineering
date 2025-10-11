import unittest
import yaml
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator

class MockModel:
    """A mock model for testing purposes."""
    def generate(self, prompt: str) -> str:
        return f"Mocked response for prompt: {prompt}"

class TestAcePipeline(unittest.TestCase):
    """Tests the full ACE pipeline."""

    def setUp(self):
        """Load the test configuration."""
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

    def test_pipeline(self):
        """Tests the integration of Generator, Reflector, and Curator."""
        # 1. Setup
        playbook = Playbook()
        mock_model = MockModel()
        generator = Generator(model=mock_model, config=self.config)
        reflector = Reflector(model=mock_model, config=self.config)
        curator = Curator()

        # 2. Initial state
        self.assertEqual(len(playbook.entries), 0)

        # 3. Run the pipeline
        task = "Test task"
        trajectory = generator.generate_trajectory(playbook, task)
        insights = reflector.reflect(trajectory)
        curator.curate(playbook, insights)

        # 4. Assert the final state
        self.assertEqual(len(playbook.entries), 3)
        entry1 = playbook.entries[0]
        self.assertIn("When analyzing task requirements", entry1.content)
        self.assertEqual(entry1.metadata["source"], "reflector")
        entry2 = playbook.entries[1]
        self.assertIn("Consulting the playbook", entry2.content)
        self.assertEqual(entry2.metadata["source"], "reflector")

if __name__ == '__main__':
    unittest.main()

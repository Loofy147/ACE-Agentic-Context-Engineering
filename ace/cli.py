import argparse
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator

class MockModel:
    """A mock model for the CLI."""
    pass

def main():
    """Main function for the ACE CLI."""
    parser = argparse.ArgumentParser(description="ACE Framework CLI")
    parser.add_argument("task", type=str, help="The task to run the ACE pipeline on.")
    args = parser.parse_args()

    # Initialize components
    playbook = Playbook()
    mock_model = MockModel()
    generator = Generator(model=mock_model)
    reflector = Reflector(model=mock_model)
    curator = Curator()

    print(f"Running ACE pipeline for task: '{args.task}'\n")

    # Run the pipeline
    trajectory = generator.generate_trajectory(playbook, args.task)
    insights = reflector.reflect(trajectory)
    curator.curate(playbook, insights)

    print("Pipeline complete. Updated playbook entries:")
    for entry in playbook.entries:
        print(f"- {entry.content}")

if __name__ == "__main__":
    main()

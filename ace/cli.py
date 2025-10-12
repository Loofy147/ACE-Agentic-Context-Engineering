import argparse
import sys
import os
import yaml
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace.llm import get_language_model
from ace import database
from ace.plugins.manager import plugin_manager

def load_config():
    """Loads the configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yaml not found. Please create it.", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}", file=sys.stderr)
        sys.exit(1)

async def main():
    """Main async function for the ACE CLI."""
    config = load_config()

    # Initialize the database
    await database.initialize_database()

    parser = argparse.ArgumentParser(description="ACE Framework CLI")
    parser.add_argument("task", type=str, nargs='?', default=config.get('cli_settings', {}).get('default_task'), help="The task to run the ACE pipeline on.")
    args = parser.parse_args()

    # Initialize components
    playbook = Playbook()
    llm = get_language_model(config)
    generator = Generator(llm=llm)
    reflector = Reflector(llm=llm)
    curator = Curator(config=config)

    print(f"Running ACE pipeline for task: '{args.task}'\n")

    # Run the pipeline
    await plugin_manager.execute_hook("on_pipeline_start", task=args.task)

    await plugin_manager.execute_hook("on_before_generation", playbook=playbook, task=args.task)
    trajectory = await generator.generate_trajectory(playbook, args.task)
    await plugin_manager.execute_hook("on_after_generation", trajectory=trajectory)

    await plugin_manager.execute_hook("on_before_reflection", trajectory=trajectory)
    insights = await reflector.reflect(trajectory)
    await plugin_manager.execute_hook("on_after_reflection", insights=insights)

    await plugin_manager.execute_hook("on_before_curation", insights=insights)
    await curator.curate(playbook, insights)
    await plugin_manager.execute_hook("on_after_curation")

    print("Pipeline complete. Updated playbook entries:")

    await plugin_manager.execute_hook("on_pipeline_end")
    for entry in await playbook.get_all_entries():
        print(f"- {entry.content}")

if __name__ == "__main__":
    asyncio.run(main())

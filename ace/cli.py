import argparse
import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ace.config import settings
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace.llm import get_language_model
from ace import database
from ace.plugins.manager import plugin_manager
from ace.cluster_manager import ClusterManager

async def main():
    """Main async function for the ACE CLI."""
    # Initialize the database
    await database.initialize_database()

    parser = argparse.ArgumentParser(description="ACE Framework CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for the 'run' command
    run_parser = subparsers.add_parser("run", help="Run the ACE pipeline on a task.")
    run_parser.add_argument("task", type=str, nargs='?', default=settings.get('cli_settings', {}).get('default_task'), help="The task to run the ACE pipeline on.")

    # Sub-parser for the 'cluster' command
    cluster_parser = subparsers.add_parser("cluster", help="Manage clusters.")
    cluster_subparsers = cluster_parser.add_subparsers(dest="cluster_command", required=True)
    cluster_subparsers.add_parser("run", help="Run the clustering and summarization process.")
    cluster_subparsers.add_parser("view", help="View the current clusters and their summaries.")

    args = parser.parse_args()

    llm = get_language_model(settings)

    if args.command == "run":
        playbook = Playbook()
        generator = Generator(llm=llm)
        reflector = Reflector(llm=llm)
        curator = Curator(config=settings)

        print(f"Running ACE pipeline for task: '{args.task}'\n")

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

    elif args.command == "cluster":
        cluster_manager = ClusterManager(settings, llm)
        if args.cluster_command == "run":
            print("Running clustering and summarization...")
            await cluster_manager.run_clustering()
            print("Clustering and summarization complete.")
        elif args.cluster_command == "view":
            print("Current clusters:")
            clusters = await cluster_manager.get_clusters()
            for cluster_id, data in clusters.items():
                print(f"\n--- Cluster {cluster_id} ---")
                print(f"Summary: {data['summary']}")
                print("Entries:")
                for entry in data['entries']:
                    print(f"  - {entry['content']}")

if __name__ == "__main__":
    asyncio.run(main())

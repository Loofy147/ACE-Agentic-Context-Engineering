from .base import Plugin
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class LoggingPlugin(Plugin):
    """
    A simple plugin that logs the events in the ACE pipeline.
    """

    async def on_pipeline_start(self, task: str):
        logging.info(f"Pipeline started for task: {task}")

    async def on_before_generation(self, playbook, task: str):
        logging.info("Starting generation...")

    async def on_after_generation(self, trajectory: str):
        logging.info(f"Generation complete. Trajectory: {trajectory[:80]}...")

    async def on_before_reflection(self, trajectory: str):
        logging.info("Starting reflection...")

    async def on_after_reflection(self, insights: List[Dict]):
        logging.info(f"Reflection complete. Found {len(insights)} insights.")

    async def on_before_curation(self, insights: List[Dict]):
        logging.info("Starting curation...")

    async def on_after_curation(self):
        logging.info("Curation complete.")

    async def on_pipeline_end(self):
        logging.info("Pipeline finished.")

from .base import Plugin
from typing import List, Dict, Any
from ace.logger import get_logger
from ace.core.models import Playbook

# Get a logger for this module.
logger = get_logger(__name__)

class LoggingPlugin(Plugin):
    """
    A simple plugin that logs the events in the ACE pipeline.

    This plugin serves as a straightforward example of how to use the plugin
    system. It hooks into every stage of the ACE pipeline and logs a message
    to the standard output, providing a real-time view of the framework's
    execution flow.

    This can be particularly useful for debugging and for understanding the
    sequence of operations within the ACE framework.
    """

    async def on_pipeline_start(self, task: str):
        """Logs the start of the pipeline."""
        logger.info(f"Pipeline started for task: {task}")

    async def on_before_generation(self, playbook: Playbook, task: str):
        """Logs the start of the generation phase."""
        logger.info("Starting generation...")

    async def on_after_generation(self, trajectory: str):
        """Logs the completion of the generation phase."""
        logger.info(f"Generation complete. Trajectory: {trajectory[:80]}...")

    async def on_before_reflection(self, trajectory: str):
        """Logs the start of the reflection phase."""
        logger.info("Starting reflection...")

    async def on_after_reflection(self, insights: List[Dict[str, Any]]):
        """Logs the completion of the reflection phase."""
        logger.info(f"Reflection complete. Found {len(insights)} insights.")

    async def on_before_curation(self, insights: List[Dict[str, Any]]):
        """Logs the start of the curation phase."""
        logger.info("Starting curation...")

    async def on_after_curation(self):
        """Logs the completion of the curation phase."""
        logger.info("Curation complete.")

    async def on_pipeline_end(self):
        """Logs the end of the pipeline."""
        logger.info("Pipeline finished.")

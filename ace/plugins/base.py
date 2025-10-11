from abc import ABC
from typing import List, Dict

class Plugin(ABC):
    """
    Abstract base class for a plugin.

    This interface defines the standard "hook" methods that plugins can
    implement to extend the functionality of the ACE framework. All hooks
    are asynchronous. Plugins should override the hooks they need.
    """

    async def on_pipeline_start(self, task: str):
        pass

    async def on_before_generation(self, playbook, task: str):
        pass

    async def on_after_generation(self, trajectory: str):
        pass

    async def on_before_reflection(self, trajectory: str):
        pass

    async def on_after_reflection(self, insights: List[Dict]):
        pass

    async def on_before_curation(self, insights: List[Dict]):
        pass

    async def on_after_curation(self):
        pass

    async def on_pipeline_end(self):
        pass

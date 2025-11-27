from abc import ABC
from typing import List, Dict, Any
from ace.core.models import Playbook

class Plugin(ABC):
    """
    Abstract base class for a plugin.

    This class defines the interface for plugins that can hook into various
    stages of the ACE pipeline. By inheriting from this class and overriding
    the appropriate methods, developers can introduce custom logic, such as
    logging, metrics collection, or modifying data in-flight, without
    altering the core framework code.

    All hook methods are asynchronous and are designed to be optional. A plugin
    only needs to implement the hooks that are relevant to its functionality.
    The default implementations are empty pass-through methods.
    """

    async def on_pipeline_start(self, task: str):
        """Called at the very beginning of the ACE pipeline."""
        pass

    async def on_before_generation(self, playbook: Playbook, task: str):
        """Called before the Generator starts its process."""
        pass

    async def on_after_generation(self, trajectory: str):
        """Called after the Generator has produced a trajectory."""
        pass

    async def on_before_reflection(self, trajectory: str):
        """Called before the Reflector starts its analysis."""
        pass

    async def on_after_reflection(self, insights: List[Dict[str, Any]]):
        """Called after the Reflector has extracted insights."""
        pass

    async def on_before_curation(self, insights: List[Dict[str, Any]]):
        """Called before the Curator starts processing the insights."""
        pass

    async def on_after_curation(self):
        """Called after the Curator has finished updating the playbook."""
        pass

    async def on_pipeline_end(self):
        """Called at the very end of the ACE pipeline."""
        pass

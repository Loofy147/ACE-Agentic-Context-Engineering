import importlib
import pkgutil
from .base import Plugin
import inspect
import asyncio
from typing import List, Any

class PluginManager:
    """
    Manages the discovery, loading, and execution of plugins.

    This class is responsible for the entire lifecycle of plugins within the
    ACE framework. It automatically discovers plugins located in the
    `ace.plugins` directory, instantiates them, and then executes their
    hook methods at the appropriate times during the ACE pipeline's execution.
    """

    def __init__(self):
        """
        Initializes the PluginManager.

        Upon initialization, the manager automatically discovers and registers
        all available plugins.
        """
        self.plugins: List[Plugin] = []
        self.discover_plugins()

    def discover_plugins(self):
        """
        Discovers and registers all plugins in the 'ace.plugins' package.

        This method iterates through all the modules in the `ace.plugins`
        package, identifies classes that are subclasses of `Plugin`, and
        instantiates them. It deliberately skips the `base` and `manager`
        modules to avoid registration issues.
        """
        import ace.plugins
        for _, name, _ in pkgutil.iter_modules(ace.plugins.__path__):
            if name not in ['base', 'manager']:
                module = importlib.import_module(f'ace.plugins.{name}')
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, Plugin) and cls is not Plugin:
                        self.register_plugin(cls())

    def register_plugin(self, plugin: Plugin):
        """
        Registers a single plugin instance.

        Args:
            plugin: An instance of a class that inherits from `Plugin`.
        """
        self.plugins.append(plugin)

    async def execute_hook(self, hook_name: str, *args: Any, **kwargs: Any):
        """
        Executes a specific hook on all registered plugins concurrently.

        This method finds the hook method with the given `hook_name` on each
        registered plugin and runs them concurrently using `asyncio.gather`.
        This ensures that hooks from different plugins do not block each other.

        Args:
            hook_name: The name of the hook to execute (e.g., 'on_pipeline_start').
            *args: Positional arguments to be passed to the hook method.
            **kwargs: Keyword arguments to be passed to the hook method.
        """
        tasks = []
        for plugin in self.plugins:
            if hasattr(plugin, hook_name):
                hook = getattr(plugin, hook_name)
                tasks.append(hook(*args, **kwargs))
        await asyncio.gather(*tasks)

# A global singleton instance of the PluginManager.
plugin_manager = PluginManager()

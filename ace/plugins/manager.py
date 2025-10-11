import importlib
import pkgutil
from .base import Plugin
import inspect
import asyncio

class PluginManager:
    """
    Manages the discovery, loading, and execution of plugins.
    """

    def __init__(self):
        """Initializes the PluginManager."""
        self.plugins = []
        self.discover_plugins()

    def discover_plugins(self):
        """Discovers and registers all plugins in the 'ace.plugins' package."""
        import ace.plugins
        for _, name, _ in pkgutil.iter_modules(ace.plugins.__path__):
            if name not in ['base', 'manager']:
                module = importlib.import_module(f'ace.plugins.{name}')
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, Plugin) and cls is not Plugin:
                        self.register_plugin(cls())

    def register_plugin(self, plugin: Plugin):
        """Registers a single plugin instance."""
        self.plugins.append(plugin)

    async def execute_hook(self, hook_name: str, *args, **kwargs):
        """
        Executes a specific hook on all registered plugins.

        Args:
            hook_name: The name of the hook to execute (e.g., 'on_pipeline_start').
            *args: Positional arguments to pass to the hook.
            **kwargs: Keyword arguments to pass to the hook.
        """
        tasks = []
        for plugin in self.plugins:
            if hasattr(plugin, hook_name):
                hook = getattr(plugin, hook_name)
                tasks.append(hook(*args, **kwargs))
        await asyncio.gather(*tasks)

plugin_manager = PluginManager()

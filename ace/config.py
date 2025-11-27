import yaml
from typing import Dict, Any

# A global variable to cache the loaded configuration.
_config = None

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Loads the application's configuration from a YAML file.

    This function reads the specified YAML file and loads its contents into a
    dictionary. The loaded configuration is then cached in a global variable
    to avoid redundant file I/O operations.

    The configuration file is expected to be in YAML format and should contain
    all the necessary settings for the application to run, such as language
    model configurations, similarity thresholds, and API keys.

    Args:
        config_path (str): The path to the configuration file. Defaults to
                           "config.yaml".

    Returns:
        Dict[str, Any]: A dictionary containing the loaded configuration.
    """
    global _config
    if _config is None:
        with open(config_path, "r") as f:
            _config = yaml.safe_load(f)
    return _config

def get_config() -> Dict[str, Any]:
    """
    Returns the loaded configuration.

    This function serves as an accessor to the cached configuration. If the
    configuration has not been loaded yet, it will first call `load_config`
    to load it.

    Returns:
        Dict[str, Any]: The application's configuration.
    """
    if _config is None:
        return load_config()
    return _config

# Load the configuration once and make it available for other modules.
settings = get_config()

from .base import LanguageModel
from .openai_model import OpenAILanguageModel
from .mock_model import MockLanguageModel
from typing import Dict, Any

def get_language_model(config: Dict[str, Any]) -> LanguageModel:
    """
    Factory function to get a language model instance based on the configuration.

    This function is the primary way to obtain a language model instance
    within the ACE framework. It reads the `language_model.name` from the
    configuration and returns an instance of the corresponding language model
    class.

    This factory approach allows the application to be flexible and easily
    support new language models in the future. To add a new model, you would
    create a new class that implements the `LanguageModel` interface and then
    add a new case in this function to instantiate it.

    Args:
        config: A dictionary containing the application configuration.

    Returns:
        An instance of a class that implements the `LanguageModel` interface.

    Raises:
        ValueError: If the specified language model name is unknown.
    """
    model_name = config.get('language_model', {}).get('name')
    if model_name == 'openai':
        return OpenAILanguageModel(config)
    elif model_name == 'mock':
        return MockLanguageModel(config)
    else:
        raise ValueError(f"Unknown language model: {model_name}")

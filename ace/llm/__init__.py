from .base import LanguageModel
from .openai_model import OpenAILanguageModel
from .mock_model import MockLanguageModel

def get_language_model(config: dict) -> LanguageModel:
    """
    Factory function to get a language model instance based on the configuration.

    Args:
        config: A dictionary containing the application configuration.

    Returns:
        An instance of a class that implements the LanguageModel interface.
    """
    model_name = config.get('language_model', {}).get('name')
    if model_name == 'openai':
        return OpenAILanguageModel(config)
    elif model_name == 'mock':
        return MockLanguageModel(config)
    else:
        raise ValueError(f"Unknown language model: {model_name}")

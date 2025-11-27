from abc import ABC, abstractmethod
from typing import Dict, Any

class LanguageModel(ABC):
    """
    Abstract base class for a language model.

    This class defines a universal, asynchronous interface for language models
    within the ACE framework. By adhering to this interface, different language

    models (e.g., OpenAI's GPT, a local model, or a mock model for testing)
    can be used interchangeably without altering the core application logic.

    The primary responsibility of a language model in this framework is to
    generate text-based responses to given prompts.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the language model with a configuration dictionary.

        Subclasses should use this constructor to store any configuration
        needed for the specific language model implementation, such as API
        keys, model names, or other parameters.

        Args:
            config: A dictionary containing the configuration for the model.
        """
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Asynchronously generates a response from the language model based on a prompt.

        This is the core method that must be implemented by all concrete
        language model classes. It takes a string prompt and is expected to
        return a string response from the language model.

        Args:
            prompt: The prompt to be sent to the language model.

        Returns:
            A string containing the response from the language model.
        """
        pass

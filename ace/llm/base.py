from abc import ABC, abstractmethod

class LanguageModel(ABC):
    """
    Abstract base class for a language model.

    This interface defines the standard methods that all language models
    in the ACE framework must implement.
    """

    def __init__(self, config: dict):
        """
        Initializes the language model with a configuration dictionary.

        Args:
            config: A dictionary containing the configuration for the model.
        """
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Asynchronously generates a response from the language model based on a prompt.

        Args:
            prompt: The prompt to send to the language model.

        Returns:
            The response from the language model.
        """
        pass

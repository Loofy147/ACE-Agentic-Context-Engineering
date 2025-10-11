from .base import LanguageModel
import random

class MockLanguageModel(LanguageModel):
    """
    A mock language model that returns pre-defined responses from the config.
    """

    def generate(self, prompt: str) -> str:
        """
        Generates a mock response by randomly selecting from a list in the config.

        Args:
            prompt: The prompt (ignored by the mock model).

        Returns:
            A randomly selected mock response.
        """
        responses = self.config.get('language_model', {}).get('mock', {}).get('responses', [])
        if not responses:
            return "No mock responses found in config."

        return random.choice(responses)

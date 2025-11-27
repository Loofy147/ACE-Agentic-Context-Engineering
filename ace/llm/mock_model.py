from .base import LanguageModel
import random

class MockLanguageModel(LanguageModel):
    """
    A mock language model that returns pre-defined responses.

    This class serves as a substitute for a real language model in testing or
    development environments. It does not make any external API calls. Instead,
    it cycles through a list of pre-defined responses provided in the
    application's configuration file.

    This allows for predictable and repeatable behavior, which is essential for
    unit testing and for developing the application without relying on a live
    internet connection or API keys.
    """

    async def generate(self, prompt: str) -> str:
        """
        Asynchronously generates a mock response.

        This method randomly selects a response from the list of mock responses
        defined in the `config.yaml` file. The `prompt` argument is ignored,
        as the response is not generated based on the input.

        Args:
            prompt: The prompt to the model (ignored in this implementation).

        Returns:
            A randomly selected string from the list of mock responses. If no
            responses are configured, it returns a default message.
        """
        responses = self.config.get('language_model', {}).get('mock', {}).get('responses', [])
        if not responses:
            return "No mock responses found in config."

        return random.choice(responses)

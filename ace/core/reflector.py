from typing import Dict, List
import json
from ace.llm import LanguageModel

class Reflector:
    """
    The Reflector component of the ACE framework.

    The Reflector analyzes a reasoning trajectory to distill key insights,
    strategies, and recommendations. These insights are then used by the
    Curator to update the playbook.
    """

    def __init__(self, llm: LanguageModel):
        """
        Initializes the Reflector with a language model.

        Args:
            llm: An instance of a class that implements the LanguageModel interface.
        """
        self.llm = llm

    async def reflect(self, trajectory: str) -> List[Dict[str, any]]:
        """
        Asynchronously analyzes a reasoning trajectory and extracts insights.

        This method prompts the language model to extract structured insights
        from a given trajectory.

        Args:
            trajectory: The reasoning trajectory to analyze.

        Returns:
            A list of insights, where each insight is a dictionary containing
            'content' and 'metadata'.
        """
        prompt = (
            f"Analyze the following trajectory and extract key insights. "
            f"Return the insights as a JSON list of objects, where each object "
            f"has 'content' and 'metadata' keys.\n\nTrajectory:\n{trajectory}"
        )

        response_text = await self.llm.generate(prompt)

        try:
            insights = json.loads(response_text)
        except json.JSONDecodeError:
            # Handle cases where the LLM response is not valid JSON
            print(f"Reflector received invalid JSON from LLM: {response_text}")
            insights = []

        return insights

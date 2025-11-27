from typing import Dict, List, Any
import json
from ace.llm import LanguageModel
from ace.logger import get_logger

logger = get_logger(__name__)

class Reflector:
    """
    The Reflector component of the ACE framework.

    The Reflector's role is to analyze the reasoning trajectory produced by the
    Generator and to distill key insights, strategies, and actionable
    learnings from it. These insights are the raw material that the Curator
    will use to enhance the playbook.

    This component uses a language model to perform the analysis, prompting it
    to extract structured information from the unstructured text of the
    trajectory.
    """

    def __init__(self, llm: LanguageModel):
        """
        Initializes the Reflector.

        Args:
            llm: An instance of a class that implements the `LanguageModel`
                 interface. This model is used to analyze the trajectory.
        """
        self.llm = llm

    async def reflect(self, trajectory: str) -> List[Dict[str, Any]]:
        """
        Asynchronously analyzes a reasoning trajectory and extracts insights.

        This method prompts the language model to identify and extract key
        insights from the given trajectory. It specifically requests that the
        output be in a structured JSON format, which can be directly used by
        the Curator.

        The method includes error handling to gracefully manage cases where the
        language model's response is not valid JSON.

        Args:
            trajectory: The reasoning trajectory to be analyzed.

        Returns:
            A list of insights, where each insight is a dictionary containing
            'content' and 'metadata'. Returns an empty list if the response
            from the language model is not valid JSON.
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
            logger.error(f"Reflector received invalid JSON from LLM: {response_text}")
            insights = []

        return insights

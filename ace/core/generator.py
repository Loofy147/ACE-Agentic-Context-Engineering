from ace.core.models import Playbook
from ace.llm import LanguageModel

class Generator:
    """
    The Generator component of the ACE framework.

    The Generator is responsible for generating a reasoning trajectory for a given
    task, using the current playbook as context. This trajectory outlines the
    steps to be taken to address the task.
    """

    def __init__(self, llm: LanguageModel):
        """
        Initializes the Generator with a language model.

        Args:
            llm: An instance of a class that implements the LanguageModel interface.
        """
        self.llm = llm

    async def generate_trajectory(self, playbook: Playbook, task: str) -> str:
        """
        Asynchronously generates a reasoning trajectory for a given task.

        This method constructs a prompt from the task and playbook, then uses
        the language model to generate a reasoning trajectory.

        Args:
            playbook: The playbook to use as context for the language model.
            task: The task for which to generate a reasoning trajectory.

        Returns:
            A string representing the reasoning trajectory.
        """
        prompt = f"Task: {task}\n\nPlaybook:\n"
        for entry in await playbook.get_all_entries():
            prompt += f"- {entry.content}\n"

        trajectory = await self.llm.generate(prompt)

        return trajectory

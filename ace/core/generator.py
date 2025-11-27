from ace.core.models import Playbook
from ace.llm import LanguageModel

class Generator:
    """
    The Generator component of the ACE framework.

    The Generator is the creative engine of the framework. Its primary
    responsibility is to generate a "reasoning trajectory" for a given task.
    This trajectory is a detailed, step-by-step plan that outlines how to
    approach the task, leveraging the accumulated knowledge stored in the
    playbook.

    The generation process is guided by a language model, which takes the
    current task and the contents of the playbook as input to produce a
    relevant and actionable trajectory.
    """

    def __init__(self, llm: LanguageModel):
        """
        Initializes the Generator.

        Args:
            llm: An instance of a class that implements the `LanguageModel`
                 interface. This model is used to generate the trajectories.
        """
        self.llm = llm

    async def generate_trajectory(self, playbook: Playbook, task: str) -> str:
        """
        Asynchronously generates a reasoning trajectory for a given task.

        This method constructs a comprehensive prompt that includes the current
        task and all the entries from the playbook. This prompt is then passed
        to the language model to generate the reasoning trajectory.

        Args:
            playbook: The playbook to be used as context for the language model.
            task: The task for which to generate a reasoning trajectory.

        Returns:
            A string representing the generated reasoning trajectory.
        """
        prompt = f"Task: {task}\n\nPlaybook:\n"
        for entry in await playbook.get_all_entries():
            prompt += f"- {entry.content}\n"

        trajectory = await self.llm.generate(prompt)

        return trajectory

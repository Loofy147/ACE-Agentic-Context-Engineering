from ace.core.models import Playbook
import random

class Generator:
    """
    The Generator component of the ACE framework.

    The Generator is responsible for generating a reasoning trajectory for a given
    task, using the current playbook as context. This trajectory outlines the
    steps to be taken to address the task.
    """

    def __init__(self, model: any, config: dict):
        """
        Initializes the Generator with a language model and configuration.

        Args:
            model: The language model to use for generation. This is currently a
                   placeholder and should be replaced with a real language model
                   interface.
            config: A dictionary containing the application configuration.
        """
        self.model = model
        self.config = config

    def generate_trajectory(self, playbook: Playbook, task: str) -> str:
        """
        Generates a reasoning trajectory for a given task.

        In a real implementation, this method would interact with a language model
        to generate a detailed, context-aware reasoning trajectory. The current
        implementation simulates this by selecting a random response from the config.

        Args:
            playbook: The playbook to use as context for the language model.
            task: The task for which to generate a reasoning trajectory.

        Returns:
            A string representing the reasoning trajectory.
        """
        # This is a placeholder implementation.
        # In a real implementation, this would use the language model
        # to generate a trajectory based on the playbook and task.
        prompt = f"Task: {task}\n\nPlaybook:\n"
        for entry in playbook.entries:
            prompt += f"- {entry.content}\n"

        # Simulate a language model call by randomly selecting a response from the config.
        responses = self.config.get('generator_responses', [])
        if not responses:
            return f"No generator responses found in config for task: {task}"

        trajectory_template = random.choice(responses)
        trajectory = trajectory_template.format(task=task)

        return trajectory

from typing import List
from ace.llm import LanguageModel

class SummarizationService:
    """
    A service for summarizing a cluster of playbook entries.
    """

    def __init__(self, llm: LanguageModel):
        """
        Initializes the SummarizationService.

        Args:
            llm: An instance of a class that implements the LanguageModel interface.
        """
        self.llm = llm

    async def summarize_cluster(self, texts: List[str]) -> str:
        """
        Generates a summary for a cluster of texts.

        Args:
            texts: A list of text content from the playbook entries in a cluster.

        Returns:
            A string containing the summary of the cluster.
        """
        prompt = (
            "Summarize the following insights into a single, coherent concept:\n\n"
            + "\n".join(f"- {text}" for text in texts)
        )
        summary = await self.llm.generate(prompt)
        return summary

summarization_service = None

def get_summarization_service(llm: LanguageModel) -> SummarizationService:
    """
    Returns a singleton instance of the SummarizationService.
    """
    global summarization_service
    if summarization_service is None:
        summarization_service = SummarizationService(llm)
    return summarization_service

from typing import List
from ace.llm import LanguageModel

class SummarizationService:
    """
    A service for summarizing a cluster of playbook entries.

    This service uses a language model to generate a concise summary for a
    given cluster of text entries. The summary is intended to capture the
    central theme or concept shared by the entries in the cluster.
    """

    def __init__(self, llm: LanguageModel):
        """
        Initializes the SummarizationService.

        Args:
            llm: An instance of a class that implements the `LanguageModel`
                 interface. This model will be used to generate the summaries.
        """
        self.llm = llm

    async def summarize_cluster(self, texts: List[str]) -> str:
        """
        Generates a summary for a cluster of texts.

        This method constructs a prompt that asks the language model to
        summarize the provided list of texts into a single, coherent concept.

        Args:
            texts: A list of text content from the playbook entries in a cluster.

        Returns:
            A string containing the generated summary of the cluster.
        """
        prompt = (
            "Summarize the following insights into a single, coherent concept:\n\n"
            + "\n".join(f"- {text}" for text in texts)
        )
        summary = await self.llm.generate(prompt)
        return summary

# A global singleton instance of the SummarizationService.
_summarization_service = None

def get_summarization_service(llm: LanguageModel) -> SummarizationService:
    """
    Returns a singleton instance of the SummarizationService.

    This function ensures that there is only one instance of the
    `SummarizationService` for a given language model. This can help to manage
    resources and maintain a consistent state.

    Args:
        llm: The language model instance to be used by the summarization service.

    Returns:
        A singleton instance of the `SummarizationService`.
    """
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService(llm)
    return _summarization_service

from typing import Dict, Any
from ace.core.models import Playbook
from ace.llm import LanguageModel
from ace.logger import get_logger
from ace.similarity import SimilarityService

logger = get_logger(__name__)

class SelfHealing:
    """
    The SelfHealing component of the ACE framework.

    This component is responsible for maintaining the quality and relevance of
    the playbook over time. It periodically reviews the playbook entries,
    identifies outdated or incorrect information, and attempts to correct it.
    """

    def __init__(self, llm: LanguageModel, playbook: Playbook, similarity_service: SimilarityService):
        """
        Initializes the SelfHealing component.

        Args:
            llm: An instance of a class that implements the `LanguageModel`
                 interface. This model is used to analyze and correct entries.
            playbook: The playbook instance to be maintained.
            similarity_service: The similarity service to use for recalculating embeddings.
        """
        self.llm = llm
        self.playbook = playbook
        self.similarity_service = similarity_service

    async def analyze_and_correct(self):
        """
        Analyzes all entries in the playbook and corrects them if necessary.

        This method iterates through each entry in the playbook, uses the
        language model to assess its correctness and relevance, and then
        updates the entry if a correction is suggested by the model.
        """
        logger.info("Starting self-healing process...")
        all_entries = await self.playbook.get_all_entries()
        for entry in all_entries:
            prompt = (
                f"Review the following playbook entry and determine if it is "
                f"still accurate and relevant. If it is not, provide a "
                f"corrected version. If it is correct, respond with the "
                f"original content.\n\n"
                f"Entry: {entry.content}\n\n"
                f"Corrected Entry:"
            )
            corrected_content = await self.llm.generate(prompt)
            if corrected_content != entry.content:
                logger.info(f"Correcting entry {entry.id}: '{entry.content}' -> '{corrected_content}'")
                new_embedding = self.similarity_service.get_embedding(corrected_content).tobytes()
                await self.playbook.add_entry(
                    entry_id=entry.id,
                    content=corrected_content,
                    metadata={"source": "self-healing"},
                    embedding=new_embedding
                )
        logger.info("Self-healing process complete.")

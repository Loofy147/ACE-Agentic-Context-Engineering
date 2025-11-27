from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any

class SimilarityService:
    """
    A service for calculating text embeddings and checking for semantic similarity.

    This class encapsulates the functionality for converting text into vector
    embeddings and comparing them to determine if they are semantically similar.
    It uses a pre-trained model from the `sentence-transformers` library to
    generate the embeddings.

    The similarity is determined by calculating the cosine similarity between
    embeddings and checking if it exceeds a configurable threshold.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the SimilarityService.

        The constructor loads the sentence transformer model specified in the
        application's configuration. If no model is specified, it defaults to
        'all-MiniLM-L6-v2'.

        Args:
            config: A dictionary containing the application configuration.
        """
        self.config = config
        model_name = self.config.get('similarity', {}).get('model', 'all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Calculates the vector embedding for a given text.

        Args:
            text: The text to be embedded.

        Returns:
            A numpy array representing the vector embedding of the text.
        """
        return self.model.encode([text])[0]

    def is_similar(self, new_embedding: np.ndarray, existing_embeddings: List[np.ndarray]) -> bool:
        """
        Checks if a new embedding is semantically similar to any existing embeddings.

        This method compares the `new_embedding` against a list of
        `existing_embeddings` using cosine similarity. If the similarity score
        between the new embedding and any of the existing ones is above a
        pre-defined threshold, the embeddings are considered similar.

        Args:
            new_embedding: The embedding of the new text or insight.
            existing_embeddings: A list of embeddings from existing texts.

        Returns:
            True if a similar embedding is found, False otherwise.
        """
        if not existing_embeddings:
            return False

        threshold = self.config.get('similarity', {}).get('threshold', 0.95)

        # Reshape the new_embedding to be a 2D array for cosine_similarity
        new_embedding = new_embedding.reshape(1, -1)

        # Calculate cosine similarity between the new embedding and all existing ones
        similarities = cosine_similarity(new_embedding, np.array(existing_embeddings))

        # Check if any similarity score is above the threshold
        return np.any(similarities > threshold)

# A global singleton instance of the SimilarityService.
_similarity_service = None

def get_similarity_service(config: Dict[str, Any]) -> SimilarityService:
    """
    Returns a singleton instance of the SimilarityService.

    This function ensures that there is only one instance of the
    `SimilarityService` throughout the application's lifecycle. This avoids
    re-loading the sentence transformer model, which can be resource-intensive.

    Args:
        config: The application's configuration dictionary.

    Returns:
        A singleton instance of the `SimilarityService`.
    """
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = SimilarityService(config)
    return _similarity_service

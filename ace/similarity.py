from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict

class SimilarityService:
    """
    A service for calculating text embeddings and checking for semantic similarity.
    """

    def __init__(self, config: dict):
        """
        Initializes the SimilarityService.

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
            text: The text to embed.

        Returns:
            A numpy array representing the vector embedding.
        """
        return self.model.encode([text])[0]

    def is_similar(self, new_embedding: np.ndarray, existing_embeddings: List[np.ndarray]) -> bool:
        """
        Checks if a new embedding is semantically similar to any existing embeddings.

        Args:
            new_embedding: The embedding of the new insight.
            existing_embeddings: A list of embeddings of existing insights.

        Returns:
            True if a similar insight is found, False otherwise.
        """
        if not existing_embeddings:
            return False

        threshold = self.config.get('similarity', {}).get('threshold', 0.95)

        # Reshape the new_embedding to be a 2D array for cosine_similarity
        new_embedding = new_embedding.reshape(1, -1)

        # Calculate cosine similarity between the new embedding and all existing ones
        similarities = cosine_similarity(new_embedding, np.array(existing_embeddings))

        # Check if any similarity is above the threshold
        return np.any(similarities > threshold)

similarity_service = None

def get_similarity_service(config: dict) -> SimilarityService:
    """
    Returns a singleton instance of the SimilarityService.
    """
    global similarity_service
    if similarity_service is None:
        similarity_service = SimilarityService(config)
    return similarity_service

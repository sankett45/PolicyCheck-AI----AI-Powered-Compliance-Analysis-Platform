from typing import List
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logger import logger


class EmbeddingsService:
    """Service class for generating text embeddings using SentenceTransformers."""

    def __init__(self) -> None:
        """Initialize and load the SentenceTransformer model once."""
        logger.info(f"Loading SentenceTransformer embedding model: {settings.EMBEDDING_MODEL}")
        try:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("SentenceTransformer embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}", exc_info=True)
            raise e

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding vector for a single query.

        Args:
            text (str): The query text to embed.

        Returns:
            List[float]: The computed embedding vector.
        """
        try:
            # Convert numpy array to standard list of floats
            vector = self._model.encode(text, convert_to_numpy=True)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}", exc_info=True)
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple documents.

        Args:
            texts (List[str]): List of texts to embed.

        Returns:
            List[List[float]]: List of computed embedding vectors.
        """
        try:
            vectors = self._model.encode(texts, convert_to_numpy=True)
            return vectors.tolist()
        except Exception as e:
            logger.error(f"Failed to generate document embeddings: {e}", exc_info=True)
            raise e

    def get_dimension(self) -> int:
        """Retrieve the dimension of the embedding vectors dynamically.

        Returns:
            int: The embedding vector dimension size.
        """
        try:
            if hasattr(self._model, "get_embedding_dimension"):
                dimension = self._model.get_embedding_dimension()
            else:
                dimension = self._model.get_sentence_embedding_dimension()
            if dimension is not None:
                return int(dimension)
        except Exception as e:
            logger.warning(f"Could not retrieve embedding dimension directly: {e}. Using fallback encoding.")
        
        # Fallback by encoding a small sample
        sample_vector = self.embed_query("test")
        return len(sample_vector)


# Create the singleton embeddings service instance
embeddings_service = EmbeddingsService()
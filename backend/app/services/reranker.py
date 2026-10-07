from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.evidence_models import Evidence
from app.utils.logger import logger


class BaseReranker(ABC):
    """Abstract base class for evidence reranking engines."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        evidence_list: List[Evidence],
        top_n: Optional[int] = None
    ) -> List[Evidence]:
        """Rerank a list of Evidence items against a query string.

        Args:
            query (str): The search query.
            evidence_list (List[Evidence]): The list of evidence to rerank.
            top_n (Optional[int]): If provided, limits the output to the top N results.

        Returns:
            List[Evidence]: The sorted, reranked list of evidence.
        """
        pass


class SimilarityReranker(BaseReranker):
    """Simple similarity-based reranker that sorts evidence by vector distance score."""

    def rerank(
        self,
        query: str,
        evidence_list: List[Evidence],
        top_n: Optional[int] = None
    ) -> List[Evidence]:
        """Rerank using the similarity scores directly.

        Args:
            query (str): The search query.
            evidence_list (List[Evidence]): List of evidence.
            top_n (Optional[int]): Optional maximum number of items to return.

        Returns:
            List[Evidence]: Sorted evidence by similarity score descending.
        """
        logger.info(f"Reranking: Sorting {len(evidence_list)} evidence items by similarity score.")
        sorted_evidence = sorted(evidence_list, key=lambda x: x.similarity_score, reverse=True)
        if top_n is not None:
            sorted_evidence = sorted_evidence[:top_n]
        return sorted_evidence


# Expose standard/default reranker instance
default_reranker = SimilarityReranker()

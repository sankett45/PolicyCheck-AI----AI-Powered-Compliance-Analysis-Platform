import uuid
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.evidence_models import Evidence, RetrievalResult
from app.services.postgres import postgres_service
from app.services.vectordb import vectordb_service
from app.services.reranker import BaseReranker, default_reranker
from app.services.confidence import EvidenceConfidenceEngine
from app.utils.logger import logger


class RetrievalService:
    """Service responsible for query embedding, vector search, version-aware filtering, and reranking."""

    def __init__(self, reranker: Optional[BaseReranker] = None) -> None:
        """Initialize the RetrievalService with an optional custom reranker.

        Args:
            reranker (Optional[BaseReranker]): Reranking engine (defaults to SimilarityReranker).
        """
        self.reranker = reranker or default_reranker

    def search(
        self,
        query: str,
        db: Optional[Session] = None,
        top_k: int = 5,
        document_type: Optional[str] = None,
        document_id: Optional[uuid.UUID] = None,
        document_version: Optional[str] = None,
    ) -> List[Evidence]:
        """Perform semantic search on Qdrant with filters, defaulting to latest document versions.

        Args:
            query (str): The search query text.
            db (Optional[Session]): Optional database session.
            top_k (int): Maximum number of evidence elements to return.
            document_type (Optional[str]): Optional document type to filter by.
            document_id (Optional[uuid.UUID]): Optional document ID to filter by.
            document_version (Optional[str]): Optional document version to filter by.

        Returns:
            List[Evidence]: Ordered and reranked list of Evidence objects.
        """
        logger.info(f"Embedding Query: '{query[:60]}...'")

        resolved_filters = {}
        if document_type:
            resolved_filters["document_type"] = document_type
        if document_id:
            resolved_filters["document_id"] = document_id
        if document_version:
            resolved_filters["document_version"] = document_version

        # Resolve database session if not provided
        is_local_db = False
        if db is None:
            db = SessionLocal()
            is_local_db = True

        try:
            # If no specific version or ID is requested, default to only the latest uploaded documents
            if "document_version" not in resolved_filters and "document_id" not in resolved_filters:
                latest_docs = postgres_service.get_latest_documents(db)
                latest_ids = [doc.id for doc in latest_docs]
                if latest_ids:
                    resolved_filters["document_ids"] = latest_ids
                else:
                    logger.info("No active documents found in PostgreSQL metadata database.")
                    return []

            # Query Qdrant
            raw_hits = vectordb_service.search_with_filter(
                query=query,
                filters=resolved_filters,
                limit=top_k
            )

            # Convert raw vector hits to structured Evidence objects
            evidence_list = []
            for hit in raw_hits:
                payload = hit["payload"]
                evidence_list.append(
                    Evidence(
                        document_id=uuid.UUID(payload["document_id"]),
                        document_version=payload["document_version"],
                        filename=payload["filename"],
                        document_type=payload["document_type"],
                        page_number=payload.get("page_number"),
                        chunk_index=payload["chunk_index"],
                        similarity_score=hit["score"],
                        text=payload["text"],
                        source=payload.get("source", payload["filename"])
                    )
                )

            # Apply reranking
            logger.info("Reranking starts...")
            reranked_evidence = self.reranker.rerank(query, evidence_list, top_n=top_k)

            logger.info(f"Evidence Returned: {len(reranked_evidence)} items.")
            return reranked_evidence

        except Exception as e:
            logger.error(f"Search failed in retrieval service: {e}", exc_info=True)
            raise e
        finally:
            if is_local_db:
                db.close()

    def search_by_document_type(
        self,
        query: str,
        document_type: str,
        db: Optional[Session] = None,
        top_k: int = 5
    ) -> List[Evidence]:
        """Perform semantic search filtered by a specific document type.

        Args:
            query (str): The search query text.
            document_type (str): Type of the document to search within.
            db (Optional[Session]): Optional database session.
            top_k (int): Max number of results.

        Returns:
            List[Evidence]: Reranked evidence list.
        """
        return self.search(
            query=query,
            db=db,
            top_k=top_k,
            document_type=document_type
        )

    def retrieve(
        self,
        question: str,
        db: Optional[Session] = None
    ) -> RetrievalResult:
        """Retrieve partitioned evidence packages (company policies vs regulations) for audits.

        Args:
            question (str): The compliance audit question.
            db (Optional[Session]): Optional database session.

        Returns:
            RetrievalResult: Complete response containing company_policy, regulations, and confidence.
        """
        logger.info(f"Starting retrieve workflow for question: '{question[:60]}...'")

        # Resolve database session if not provided
        is_local_db = False
        if db is None:
            db = SessionLocal()
            is_local_db = True

        try:
            # 1. Retrieve company documents (policies, SOPs, contracts)
            logger.info("Searching Company Documents...")
            company_evidence = []
            for doc_type in ["company_policy", "sop", "contract"]:
                results = self.search(
                    query=question,
                    db=db,
                    top_k=5,
                    document_type=doc_type
                )
                company_evidence.extend(results)
            # Rerank the combined company evidence and slice to top 5
            company_evidence = self.reranker.rerank(question, company_evidence, top_n=5)

            # 2. Retrieve regulations
            logger.info("Searching Regulations...")
            regulations_evidence = self.search(
                query=question,
                db=db,
                top_k=5,
                document_type="regulation"
            )

            # 3. Calculate evidence confidence
            logger.info("Confidence calculation started...")
            confidence_data = EvidenceConfidenceEngine.calculate_confidence(
                company_policy=company_evidence,
                regulations=regulations_evidence
            )

            return RetrievalResult(
                question=question,
                company_policy=company_evidence,
                regulations=regulations_evidence,
                confidence=confidence_data["confidence"],
                confidence_level=confidence_data["level"]
            )
        except Exception as e:
            logger.error(f"Retrieve failed in retrieval service: {e}", exc_info=True)
            raise e
        finally:
            if is_local_db:
                db.close()


# Singleton service instance
retrieval_service = RetrievalService()

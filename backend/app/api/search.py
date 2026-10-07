from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.evidence_models import (
    SearchRequest,
    RetrieveRequest,
    Evidence,
    RetrievalResult
)
from app.services.retriever import retrieval_service
from app.utils.logger import logger

router = APIRouter()

SUPPORTED_DOCUMENT_TYPES = {"company_policy", "regulation", "contract", "sop"}


@router.post("/search", response_model=List[Evidence], status_code=status.HTTP_200_OK)
def search_evidence(request: SearchRequest, db: Session = Depends(get_db)):
    """Exposes semantic search endpoint.

    Validates inputs, executes vector search with metadata filters, and returns ranked Evidence.
    """
    logger.info(f"Query received on POST /search: query='{request.query}', type={request.document_type}, top_k={request.top_k}")

    # Validate inputs
    query_stripped = request.query.strip()
    if not query_stripped:
        logger.error("Search failed: empty query string provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty or whitespace."
        )

    if request.document_type and request.document_type not in SUPPORTED_DOCUMENT_TYPES:
        logger.error(f"Search failed: invalid document type '{request.document_type}' requested.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {', '.join(SUPPORTED_DOCUMENT_TYPES)}"
        )

    if request.top_k is not None and request.top_k <= 0:
        logger.error(f"Search failed: invalid top_k value {request.top_k}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_k parameter must be a positive integer greater than 0."
        )

    try:
        # Perform retrieval service search
        results = retrieval_service.search(
            query=query_stripped,
            db=db,
            top_k=request.top_k or 5,
            document_type=request.document_type
        )

        if not results:
            logger.info("No matching evidence found for the search query.")
        else:
            logger.info(f"Search query returned {len(results)} ranked evidence items.")

        return results

    except ValueError as ve:
        logger.error(f"Validation or payload conversion error during search: {ve}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Search request validation failed: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Internal error processing semantic search query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/retrieve", response_model=RetrievalResult, status_code=status.HTTP_200_OK)
def retrieve_compliance_evidence(request: RetrieveRequest, db: Session = Depends(get_db)):
    """Exposes structured compliance retrieve endpoint.

    Separately retrieves company policies and regulations, reranks them, and computes a confidence score.
    """
    logger.info(f"Retrieve query received on POST /retrieve: question='{request.question}'")

    # Validate inputs
    question_stripped = request.question.strip()
    if not question_stripped:
        logger.error("Retrieve failed: empty question provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty or whitespace."
        )

    try:
        # Perform retrieval service retrieve
        retrieval_result = retrieval_service.retrieve(
            question=question_stripped,
            db=db
        )

        total_policy = len(retrieval_result.company_policy)
        total_regulation = len(retrieval_result.regulations)
        logger.info(
            f"Retrieval complete: company_policy_count={total_policy}, "
            f"regulations_count={total_regulation}, confidence={retrieval_result.confidence} ({retrieval_result.confidence_level})"
        )

        return retrieval_result

    except ValueError as ve:
        logger.error(f"Validation or conversion error during retrieval: {ve}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Retrieval validation failed: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Internal error processing retrieval question: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence retrieval failed: {str(e)}"
        )

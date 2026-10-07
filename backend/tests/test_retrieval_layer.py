import uuid
import pytest
from unittest.mock import MagicMock, patch

from app.models.evidence_models import Evidence, RetrievalResult, SearchRequest, RetrieveRequest
from app.services.reranker import SimilarityReranker
from app.services.confidence import EvidenceConfidenceEngine
from app.services.retriever import RetrievalService


# 1. Test Pydantic Models & Validation
def test_evidence_model_validation():
    doc_id = uuid.uuid4()
    ev = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="test.pdf",
        document_type="company_policy",
        page_number=3,
        chunk_index=5,
        similarity_score=0.85,
        text="This is a test chunk.",
        source="test.pdf"
    )
    assert ev.document_id == doc_id
    assert ev.document_version == "1.0.0"
    assert ev.filename == "test.pdf"
    assert ev.document_type == "company_policy"
    assert ev.page_number == 3
    assert ev.chunk_index == 5
    assert ev.similarity_score == 0.85
    assert ev.text == "This is a test chunk."
    assert ev.source == "test.pdf"


def test_search_request_validation():
    with pytest.raises(ValueError):
        SearchRequest(query="")

    req = SearchRequest(query="password policy", document_type="regulation", top_k=10)
    assert req.query == "password policy"
    assert req.document_type == "regulation"
    assert req.top_k == 10


def test_retrieve_request_validation():
    with pytest.raises(ValueError):
        RetrieveRequest(question="")

    req = RetrieveRequest(question="Is our policy compliant?")
    assert req.question == "Is our policy compliant?"


# 2. Test Similarity Reranker
def test_similarity_reranker():
    reranker = SimilarityReranker()
    doc_id = uuid.uuid4()
    ev1 = Evidence(
        document_id=doc_id, document_version="1.0.0", filename="test.pdf",
        document_type="company_policy", page_number=1, chunk_index=0,
        similarity_score=0.70, text="Low match", source="test.pdf"
    )
    ev2 = Evidence(
        document_id=doc_id, document_version="1.0.0", filename="test.pdf",
        document_type="company_policy", page_number=1, chunk_index=1,
        similarity_score=0.95, text="High match", source="test.pdf"
    )
    ev3 = Evidence(
        document_id=doc_id, document_version="1.0.0", filename="test.pdf",
        document_type="company_policy", page_number=1, chunk_index=2,
        similarity_score=0.85, text="Medium match", source="test.pdf"
    )

    # Test reranking order (descending by score)
    result = reranker.rerank("dummy query", [ev1, ev2, ev3])
    assert len(result) == 3
    assert result[0].similarity_score == 0.95
    assert result[1].similarity_score == 0.85
    assert result[2].similarity_score == 0.70

    # Test top_n truncation
    result_truncated = reranker.rerank("dummy query", [ev1, ev2, ev3], top_n=2)
    assert len(result_truncated) == 2
    assert result_truncated[0].similarity_score == 0.95
    assert result_truncated[1].similarity_score == 0.85


# 3. Test Evidence Confidence Engine
def test_confidence_engine_empty():
    res = EvidenceConfidenceEngine.calculate_confidence([], [])
    assert res["confidence"] == 0.0
    assert res["level"] == "low"


def test_confidence_engine_high():
    doc_id1 = uuid.uuid4()
    doc_id2 = uuid.uuid4()
    doc_id3 = uuid.uuid4()

    company_policy = [
        Evidence(
            document_id=doc_id1, document_version="1.0.0", filename="policy.pdf",
            document_type="company_policy", page_number=2, chunk_index=0,
            similarity_score=0.90, text="Policy content", source="policy.pdf"
        ),
        Evidence(
            document_id=doc_id2, document_version="1.0.0", filename="sop.pdf",
            document_type="sop", page_number=1, chunk_index=1,
            similarity_score=0.85, text="SOP content", source="sop.pdf"
        )
    ]
    regulations = [
        Evidence(
            document_id=doc_id3, document_version="2.1.0", filename="reg.pdf",
            document_type="regulation", page_number=15, chunk_index=10,
            similarity_score=0.95, text="Reg content", source="reg.pdf"
        )
    ]

    res = EvidenceConfidenceEngine.calculate_confidence(company_policy, regulations)
    assert res["confidence"] >= 0.80
    assert res["level"] == "high"


def test_confidence_engine_medium_or_low():
    doc_id = uuid.uuid4()
    company_policy = [
        Evidence(
            document_id=doc_id, document_version="1.0.0", filename="policy.pdf",
            document_type="company_policy", page_number=None, chunk_index=0,
            similarity_score=0.55, text="Policy content", source="policy.pdf"
        )
    ]
    regulations = []

    res = EvidenceConfidenceEngine.calculate_confidence(company_policy, regulations)
    assert res["confidence"] < 0.80
    assert res["level"] in ("medium", "low")


# 4. Test Retrieval Service with Mocks
@patch("app.services.retriever.vectordb_service")
@patch("app.services.retriever.postgres_service")
def test_retriever_search_default_latest_version(mock_postgres, mock_vectordb):
    db_mock = MagicMock()
    doc_id_latest = uuid.uuid4()

    latest_doc_mock = MagicMock()
    latest_doc_mock.id = doc_id_latest
    latest_doc_mock.filename = "policy.pdf"
    mock_postgres.get_latest_documents.return_value = [latest_doc_mock]

    mock_vectordb.search_with_filter.return_value = [
        {
            "id": "point-1",
            "score": 0.88,
            "payload": {
                "document_id": str(doc_id_latest),
                "document_version": "2.0.0",
                "filename": "policy.pdf",
                "document_type": "company_policy",
                "page_number": 1,
                "chunk_index": 0,
                "text": "MFA is mandatory."
            }
        }
    ]

    service = RetrievalService()
    results = service.search(query="MFA", db=db_mock)

    assert len(results) == 1
    assert results[0].document_id == doc_id_latest
    assert results[0].document_version == "2.0.0"
    assert results[0].similarity_score == 0.88
    assert results[0].text == "MFA is mandatory."

    mock_postgres.get_latest_documents.assert_called_once_with(db_mock)
    mock_vectordb.search_with_filter.assert_called_once()
    called_args = mock_vectordb.search_with_filter.call_args[1]
    assert "document_ids" in called_args["filters"]
    assert doc_id_latest in called_args["filters"]["document_ids"]


@patch("app.services.retriever.vectordb_service")
@patch("app.services.retriever.postgres_service")
def test_retriever_search_with_version_filter(mock_postgres, mock_vectordb):
    db_mock = MagicMock()
    doc_id = uuid.uuid4()

    mock_vectordb.search_with_filter.return_value = [
        {
            "id": "point-1",
            "score": 0.92,
            "payload": {
                "document_id": str(doc_id),
                "document_version": "1.0.0",
                "filename": "policy.pdf",
                "document_type": "company_policy",
                "page_number": 2,
                "chunk_index": 3,
                "text": "Old backup policy."
            }
        }
    ]

    service = RetrievalService()
    results = service.search(query="backup", db=db_mock, document_version="1.0.0")

    assert len(results) == 1
    assert results[0].document_version == "1.0.0"
    mock_postgres.get_latest_documents.assert_not_called()

    mock_vectordb.search_with_filter.assert_called_once()
    called_args = mock_vectordb.search_with_filter.call_args[1]
    assert called_args["filters"]["document_version"] == "1.0.0"

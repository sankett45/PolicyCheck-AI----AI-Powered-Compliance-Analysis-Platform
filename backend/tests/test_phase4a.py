import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError
import uuid

from app.models.planner_models import PlannerOutput
from app.models.audit_models import AuditRequest, AuditResponse
from app.graph.state import AuditState
from app.graph.nodes import planner_node, retrieval_node
from app.services.audit_graph import audit_graph_service
from app.models.evidence_models import RetrievalResult, Evidence


# 1. PlannerOutput validation
def test_planner_output_validation():
    # Valid model
    output = PlannerOutput(
        audit_type="policy_compliance",
        subject="password_policy",
        regulation="ISO 27001",
        intent="Compare password policy requirements."
    )
    assert output.audit_type == "policy_compliance"
    assert output.subject == "password_policy"
    assert output.regulation == "ISO 27001"
    assert output.intent == "Compare password policy requirements."

    # Invalid model: missing audit_type
    with pytest.raises(ValidationError):
        PlannerOutput(
            subject="password_policy",
            intent="Compare password policy."
        )


# 2. Planner node with mocked LLM
@patch("app.graph.nodes.planner_agent")
def test_planner_node_success(mock_agent):
    # Mock PlannerAgent output
    mock_output = PlannerOutput(
        audit_type="regulatory_compliance",
        subject="data_privacy",
        regulation="GDPR",
        intent="Audit data privacy policy under GDPR."
    )
    mock_agent.plan.return_value = mock_output

    state: AuditState = {
        "question": "Is our data privacy compliant with GDPR?",
        "errors": []
    }

    result = planner_node(state)
    assert result["audit_type"] == "regulatory_compliance"
    assert result["subject"] == "data_privacy"
    assert result["regulation"] == "GDPR"
    assert result["intent"] == "Audit data privacy policy under GDPR."


# 3. Retrieval node with mocked RetrievalService
@patch("app.graph.nodes.retrieval_service")
def test_retrieval_node_success(mock_retrieval_service):
    doc_id = uuid.uuid4()
    mock_result = RetrievalResult(
        question="Is our password policy compliant?",
        company_policy=[
            Evidence(
                document_id=doc_id,
                document_version="1.0.0",
                filename="policy.pdf",
                document_type="company_policy",
                page_number=1,
                chunk_index=0,
                similarity_score=0.90,
                text="Password must be 8 chars.",
                source="policy.pdf"
            )
        ],
        regulations=[],
        confidence=0.75,
        confidence_level="medium"
    )
    mock_retrieval_service.retrieve.return_value = mock_result

    state: AuditState = {
        "question": "Is our password policy compliant?",
        "errors": []
    }

    result = retrieval_node(state)
    assert result["retrieval_result"] == mock_result
    assert result["confidence"] == 0.75
    assert result["confidence_level"] == "medium"


# 4. Graph execution with both nodes mocked
@patch("app.graph.nodes.planner_agent")
@patch("app.graph.nodes.retrieval_service")
def test_graph_execution_success(mock_retrieval_service, mock_planner_agent):
    # Mock Planner
    mock_planner_agent.plan.return_value = PlannerOutput(
        audit_type="policy_compliance",
        subject="backup_policy",
        regulation="ISO 27001",
        intent="Evaluate backup policy"
    )

    # Mock Retriever
    mock_retrieval_service.retrieve.return_value = RetrievalResult(
        question="Is our backup compliant?",
        company_policy=[],
        regulations=[],
        confidence=0.50,
        confidence_level="medium"
    )

    result = audit_graph_service.run_audit("Is our backup compliant?")
    assert result["audit_type"] == "policy_compliance"
    assert result["subject"] == "backup_policy"
    assert result["regulation"] == "ISO 27001"
    assert result["intent"] == "Evaluate backup policy"
    assert result["retrieval_result"].confidence == 0.50
    assert result["confidence"] == 0.50
    assert result["confidence_level"] == "medium"


# 5. Empty question validation
def test_empty_question_validation():
    # Service validation
    with pytest.raises(ValueError):
        audit_graph_service.run_audit("")

    # Planner Node validation
    state: AuditState = {"question": "", "errors": []}
    result = planner_node(state)
    assert "errors" in result
    assert "Question cannot be empty." in result["errors"]


# 6. Planner failure handling
@patch("app.graph.nodes.planner_agent")
def test_planner_node_failure(mock_agent):
    mock_agent.plan.side_effect = Exception("LLM connection timeout")
    state: AuditState = {"question": "Some question", "errors": []}

    with pytest.raises(ValueError) as exc:
        planner_node(state)
    assert "Planner failure" in str(exc.value)


# 7. Retrieval failure handling
@patch("app.graph.nodes.retrieval_service")
def test_retrieval_node_failure(mock_retrieval_service):
    mock_retrieval_service.retrieve.side_effect = Exception("Qdrant unavailable")
    state: AuditState = {"question": "Some question", "errors": []}

    with pytest.raises(ValueError) as exc:
        retrieval_node(state)
    assert "Retrieval failure" in str(exc.value)


# 8. /audit endpoint with mocked graph
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.audit.audit_graph_service")
def test_audit_endpoint_success(mock_graph_service):
    doc_id = uuid.uuid4()
    mock_graph_service.run_audit.return_value = {
        "question": "Is our password policy compliant with ISO 27001?",
        "audit_type": "policy_compliance",
        "subject": "password_policy",
        "regulation": "ISO 27001",
        "intent": "Compare password policy",
        "retrieval_result": RetrievalResult(
            question="Is our password policy compliant with ISO 27001?",
            company_policy=[
                Evidence(
                    document_id=doc_id,
                    document_version="1.2.3",
                    filename="policy.pdf",
                    document_type="company_policy",
                    page_number=4,
                    chunk_index=8,
                    similarity_score=0.91,
                    text="Pass length >= 8",
                    source="policy.pdf"
                )
            ],
            regulations=[],
            confidence=0.91,
            confidence_level="high"
        ),
        "confidence": 0.91,
        "confidence_level": "high",
        "errors": []
    }

    response = client.post(
        "/audit",
        json={"question": "Is our password policy compliant with ISO 27001?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Is our password policy compliant with ISO 27001?"
    assert data["planner"]["audit_type"] == "policy_compliance"
    assert data["planner"]["subject"] == "password_policy"
    assert data["planner"]["regulation"] == "ISO 27001"
    assert data["planner"]["intent"] == "Compare password policy"
    assert len(data["retrieval"]["company_policy"]) == 1
    assert data["retrieval"]["confidence"] == 0.91
    assert data["retrieval"]["confidence_level"] == "high"

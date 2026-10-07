import uuid
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.models.evidence_models import Evidence, RetrievalResult
from app.models.compliance_models import (
    ComplianceAnalysis,
    ComplianceFinding,
    ComplianceAnalysisLLM,
    ComplianceFindingLLM,
    EvidenceCitation
)
from app.agents.compliance import ComplianceAgent
from app.graph.nodes import compliance_node
from app.services.audit_graph import audit_graph_service
from app.models.planner_models import PlannerOutput
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Compliance model validation
def test_compliance_model_validation():
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.88,
        text="MFA is required.",
        source="policy.txt"
    )

    finding = ComplianceFinding(
        control="Access Control",
        status="compliant",
        company_requirement="MFA mandatory",
        regulatory_requirement="MFA required",
        reasoning="Satisfied.",
        evidence=[evidence_obj]
    )

    analysis = ComplianceAnalysis(
        overall_status="compliant",
        summary="Audit summary.",
        findings=[finding],
        confidence=0.90,
        evidence_sufficient=True
    )

    assert analysis.overall_status == "compliant"
    assert len(analysis.findings) == 1
    assert analysis.confidence == 0.90
    assert analysis.evidence_sufficient is True


# 2. Compliant / Partially compliant / Non-compliant / Insufficient evidence scenarios
@patch("app.agents.compliance.llm_service")
def test_compliance_scenarios_from_llm(mock_llm_service):
    doc_id1 = uuid.uuid4()
    doc_id2 = uuid.uuid4()

    ev_policy = Evidence(
        document_id=doc_id1, document_version="1.0.0", filename="policy.txt",
        document_type="company_policy", page_number=1, chunk_index=0,
        similarity_score=0.80, text="MFA is mandatory for SSH access.", source="policy.txt"
    )
    ev_reg = Evidence(
        document_id=doc_id2, document_version="1.0.0", filename="reg.txt",
        document_type="regulation", page_number=1, chunk_index=0,
        similarity_score=0.85, text="Multi-factor authentication must be implemented.", source="reg.txt"
    )

    retrieval_res = RetrievalResult(
        question="Is MFA compliant?",
        company_policy=[ev_policy],
        regulations=[ev_reg],
        confidence=0.80,
        confidence_level="high"
    )

    agent = ComplianceAgent()
    agent._chain = MagicMock()

    # Scenario: COMPLIANT
    agent._chain.invoke.return_value = ComplianceAnalysisLLM(
        overall_status="compliant",
        summary="Satisfied.",
        findings=[
            ComplianceFindingLLM(
                control="MFA",
                status="compliant",
                company_requirement="MFA mandatory for SSH",
                regulatory_requirement="MFA required",
                reasoning="Both require MFA.",
                evidence_citations=[
                    EvidenceCitation(filename="policy.txt", chunk_index=0),
                    EvidenceCitation(filename="reg.txt", chunk_index=0)
                ]
            )
        ],
        confidence=0.95,
        evidence_sufficient=True
    )

    analysis = agent.analyze(retrieval_res)
    assert analysis.overall_status == "compliant"
    assert analysis.evidence_sufficient is True
    assert len(analysis.findings[0].evidence) == 2

    # Scenario: PARTIALLY COMPLIANT
    agent._chain.invoke.return_value = ComplianceAnalysisLLM(
        overall_status="partially_compliant",
        summary="Partial.",
        findings=[
            ComplianceFindingLLM(
                control="MFA",
                status="partially_compliant",
                company_requirement="MFA SSH only",
                regulatory_requirement="MFA all admin access",
                reasoning="Missing web console MFA.",
                evidence_citations=[
                    EvidenceCitation(filename="policy.txt", chunk_index=0)
                ]
            )
        ],
        confidence=0.70,
        evidence_sufficient=True
    )
    analysis = agent.analyze(retrieval_res)
    assert analysis.overall_status == "partially_compliant"

    # Scenario: NON COMPLIANT
    agent._chain.invoke.return_value = ComplianceAnalysisLLM(
        overall_status="non_compliant",
        summary="Non-compliant.",
        findings=[
            ComplianceFindingLLM(
                control="MFA",
                status="non_compliant",
                company_requirement="MFA optional",
                regulatory_requirement="MFA mandatory",
                reasoning="Optional violates mandatory.",
                evidence_citations=[
                    EvidenceCitation(filename="policy.txt", chunk_index=0)
                ]
            )
        ],
        confidence=0.85,
        evidence_sufficient=True
    )
    analysis = agent.analyze(retrieval_res)
    assert analysis.overall_status == "non_compliant"


# 3. Insufficient evidence scenario
def test_insufficient_evidence_direct():
    doc_id = uuid.uuid4()
    ev_policy = Evidence(
        document_id=doc_id, document_version="1.0.0", filename="policy.txt",
        document_type="company_policy", page_number=1, chunk_index=0,
        similarity_score=0.80, text="MFA is optional.", source="policy.txt"
    )

    retrieval_res = RetrievalResult(
        question="Is MFA compliant?",
        company_policy=[ev_policy],
        regulations=[],
        confidence=0.40,
        confidence_level="low"
    )

    agent = ComplianceAgent()
    analysis = agent.analyze(retrieval_res)
    assert analysis.overall_status == "insufficient_evidence"
    assert analysis.evidence_sufficient is False
    assert analysis.confidence == 0.20


# 4. Invalid/fabricated evidence citation rejection
@patch("app.agents.compliance.llm_service")
def test_citation_validation_rejection(mock_llm_service):
    doc_id_real = uuid.uuid4()

    ev_real = Evidence(
        document_id=doc_id_real, document_version="1.0.0", filename="real_policy.txt",
        document_type="company_policy", page_number=1, chunk_index=0,
        similarity_score=0.90, text="Real text.", source="real_policy.txt"
    )
    ev_reg = Evidence(
        document_id=uuid.uuid4(), document_version="1.0.0", filename="real_reg.txt",
        document_type="regulation", page_number=1, chunk_index=0,
        similarity_score=0.90, text="Reg text.", source="real_reg.txt"
    )

    retrieval_res = RetrievalResult(
        question="Compliance question?",
        company_policy=[ev_real],
        regulations=[ev_reg],
        confidence=0.90,
        confidence_level="high"
    )

    agent = ComplianceAgent()
    agent._chain = MagicMock()
    agent._chain.invoke.return_value = ComplianceAnalysisLLM(
        overall_status="compliant",
        summary="Summary text.",
        findings=[
            ComplianceFindingLLM(
                control="Control Name",
                status="compliant",
                company_requirement="Req.",
                regulatory_requirement="Reg.",
                reasoning="Reasoning.",
                evidence_citations=[
                    EvidenceCitation(filename="real_policy.txt", chunk_index=0),
                    EvidenceCitation(filename="fake_policy.txt", chunk_index=99)
                ]
            )
        ],
        confidence=0.90,
        evidence_sufficient=True
    )

    analysis = agent.analyze(retrieval_res)

    finding = analysis.findings[0]
    assert len(finding.evidence) == 1
    assert finding.evidence[0].document_id == doc_id_real
    assert finding.evidence[0].filename == "real_policy.txt"


# 5. Missing RetrievalResult handling in compliance node
def test_compliance_node_missing_result():
    state: AuditState = {
        "question": "Is policy compliant?",
        "retrieval_result": None,
        "errors": []
    }
    with pytest.raises(ValueError) as exc:
        compliance_node(state)
    assert "retrieval_result is missing" in str(exc.value)


# 6. Compliance node state update
@patch("app.graph.nodes.compliance_agent")
def test_compliance_node_state_update(mock_compliance_agent):
    mock_analysis = ComplianceAnalysis(
        overall_status="compliant",
        summary="Analysis complete.",
        findings=[],
        confidence=0.88,
        evidence_sufficient=True
    )
    mock_compliance_agent.analyze.return_value = mock_analysis

    state: AuditState = {
        "question": "Is policy compliant?",
        "retrieval_result": RetrievalResult(
            question="Is policy compliant?",
            company_policy=[],
            regulations=[],
            confidence=0.80,
            confidence_level="high"
        ),
        "errors": []
    }

    result = compliance_node(state)
    assert result["compliance_analysis"] == mock_analysis
    assert result["compliance_confidence"] == 0.88


# 7. Full graph execution with all nodes mocked
@patch("app.graph.nodes.planner_agent")
@patch("app.graph.nodes.retrieval_service")
@patch("app.graph.nodes.compliance_agent")
def test_full_graph_execution(mock_compliance_agent, mock_retrieval_service, mock_planner_agent):
    mock_planner_agent.plan.return_value = PlannerOutput(
        audit_type="regulatory_compliance",
        subject="backup",
        regulation="GDPR",
        intent="Audit backups"
    )

    mock_retrieval_service.retrieve.return_value = RetrievalResult(
        question="Audit question?",
        company_policy=[],
        regulations=[],
        confidence=0.70,
        confidence_level="medium"
    )

    mock_analysis = ComplianceAnalysis(
        overall_status="insufficient_evidence",
        summary="Empty lists.",
        findings=[],
        confidence=0.20,
        evidence_sufficient=False
    )
    mock_compliance_agent.analyze.return_value = mock_analysis

    result = audit_graph_service.run_audit("Audit question?")
    assert result["audit_type"] == "regulatory_compliance"
    assert result["retrieval_result"].confidence == 0.70
    assert result["compliance_analysis"] == mock_analysis
    assert result["compliance_confidence"] == 0.20


# 8. /audit API response structure
@patch("app.api.audit.audit_graph_service")
def test_audit_api_response_structure(mock_graph_service):
    doc_id = uuid.uuid4()
    mock_graph_service.run_audit.return_value = {
        "question": "Is backup compliant?",
        "audit_type": "policy_compliance",
        "subject": "backup",
        "regulation": "ISO 27001",
        "intent": "Evaluate backup policy",
        "retrieval_result": RetrievalResult(
            question="Is backup compliant?",
            company_policy=[
                Evidence(
                    document_id=doc_id,
                    document_version="1.0.0",
                    filename="policy.txt",
                    document_type="company_policy",
                    page_number=2,
                    chunk_index=1,
                    similarity_score=0.75,
                    text="Backup daily.",
                    source="policy.txt"
                )
            ],
            regulations=[],
            confidence=0.75,
            confidence_level="medium"
        ),
        "retrieval_confidence": 0.75,
        "confidence_level": "medium",
        "compliance_analysis": ComplianceAnalysis(
            overall_status="compliant",
            summary="All compliant.",
            findings=[
                ComplianceFinding(
                    control="Backup",
                    status="compliant",
                    company_requirement="Backup daily",
                    regulatory_requirement="Daily backups",
                    reasoning="Daily satisfies requirement.",
                    evidence=[]
                )
            ],
            confidence=0.85,
            evidence_sufficient=True
        ),
        "compliance_confidence": 0.85,
        "errors": []
    }

    response = client.post(
        "/audit",
        json={"question": "Is backup compliant?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "compliance" in data
    assert data["compliance"]["overall_status"] == "compliant"
    assert len(data["compliance"]["findings"]) == 1
    assert data["compliance"]["findings"][0]["control"] == "Backup"
    assert data["compliance"]["confidence"] == 0.85
    assert data["compliance"]["evidence_sufficient"] is True

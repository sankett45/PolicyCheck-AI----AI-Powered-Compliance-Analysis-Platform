import uuid
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.models.evidence_models import Evidence, RetrievalResult
from app.models.compliance_models import ComplianceAnalysis, ComplianceFinding
from app.models.risk_models import (
    RiskLevel,
    RiskFactorAssessment,
    RiskAnalysisLLM,
    RiskAssessment,
    RiskAnalysis
)
from app.models.risk_scoring import calculate_risk_score, map_score_to_level
from app.agents.risk import RiskAgent
from app.graph.nodes import risk_node
from app.services.audit_graph import audit_graph_service
from app.models.planner_models import PlannerOutput
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Risk model validation (input bounds for fields)
def test_risk_model_validation():
    # Valid model validation
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="Sample text",
        source="policy.txt"
    )

    assessment = RiskAssessment(
        finding_id="finding_0",
        control="Access Control",
        risk_level="medium",
        severity=3,
        likelihood=3,
        impact=3,
        risk_score=27,
        rationale="Moderate risk",
        evidence=[evidence_obj]
    )
    assert assessment.risk_score == 27
    assert assessment.risk_level == "medium"

    # Out of bounds validation (severity > 5)
    with pytest.raises(ValidationError):
        RiskAssessment(
            finding_id="finding_0",
            control="Access Control",
            risk_level="medium",
            severity=6,  # Invalid
            likelihood=3,
            impact=3,
            risk_score=54,
            rationale="Invalid severity",
            evidence=[evidence_obj]
        )


# 2. Risk score calculation
def test_risk_score_calculation():
    assert calculate_risk_score(1, 1, 1) == 1
    assert calculate_risk_score(5, 5, 5) == 125
    assert calculate_risk_score(3, 4, 2) == 24


# 3. Risk threshold mapping
def test_risk_threshold_mapping():
    assert map_score_to_level(0) == "low"
    assert map_score_to_level(1) == "low"
    assert map_score_to_level(20) == "low"
    assert map_score_to_level(21) == "medium"
    assert map_score_to_level(50) == "medium"
    assert map_score_to_level(51) == "high"
    assert map_score_to_level(80) == "high"
    assert map_score_to_level(81) == "critical"
    assert map_score_to_level(125) == "critical"


# 4-7. Severity / likelihood / impact mapping scenarios
def test_risk_level_scenarios():
    # Low-risk mapping (score 12)
    assert map_score_to_level(calculate_risk_score(2, 3, 2)) == "low"

    # Medium-risk mapping (score 36)
    assert map_score_to_level(calculate_risk_score(4, 3, 3)) == "medium"

    # High-risk mapping (score 64)
    assert map_score_to_level(calculate_risk_score(4, 4, 4)) == "high"

    # Critical-risk mapping (score 100)
    assert map_score_to_level(calculate_risk_score(5, 4, 5)) == "critical"


# 8. Multiple findings overall-risk selection
def test_multiple_findings_overall_selection():
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="Sample text",
        source="policy.txt"
    )

    assessment_1 = RiskAssessment(
        finding_id="finding_0",
        control="Control A",
        risk_level="medium",
        severity=3,
        likelihood=3,
        impact=3,
        risk_score=27,
        rationale="Med risk",
        evidence=[evidence_obj]
    )

    assessment_2 = RiskAssessment(
        finding_id="finding_1",
        control="Control B",
        risk_level="critical",
        severity=5,
        likelihood=4,
        impact=5,
        risk_score=100,
        rationale="Critical risk",
        evidence=[evidence_obj]
    )

    analysis = RiskAnalysis(
        overall_risk_level=map_score_to_level(max(assessment_1.risk_score, assessment_2.risk_score)),
        overall_risk_score=max(assessment_1.risk_score, assessment_2.risk_score),
        assessments=[assessment_1, assessment_2],
        summary="Audit summary"
    )

    assert analysis.overall_risk_score == 100
    assert analysis.overall_risk_level == "critical"


# 9. Fully compliant scenario
@patch("app.agents.risk.llm_service")
def test_fully_compliant_scenario(mock_llm_service):
    comp_analysis = ComplianceAnalysis(
        overall_status="compliant",
        summary="All good.",
        findings=[
            ComplianceFinding(
                control="Control A",
                status="compliant",
                company_requirement="Mandatory",
                regulatory_requirement="Mandatory",
                reasoning="Aligned.",
                evidence=[]
            )
        ],
        confidence=0.95,
        evidence_sufficient=True
    )

    agent = RiskAgent()
    result = agent.assess(comp_analysis)
    # Fully compliant bypasses LLM
    assert len(result.assessments) == 0
    assert "No material compliance gaps" in result.summary


# 10. Insufficient-evidence scenario
def test_insufficient_evidence_scenario():
    # If compliance status is insufficient_evidence, node bypasses evaluation
    comp_analysis = ComplianceAnalysis(
        overall_status="insufficient_evidence",
        summary="Missing policy.",
        findings=[],
        confidence=0.20,
        evidence_sufficient=False
    )

    state = {
        "compliance_analysis": comp_analysis,
        "errors": []
    }

    result = risk_node(state)
    assert result["risk_analysis"].overall_risk_level == "low"
    assert result["risk_analysis"].overall_risk_score == 0
    assert len(result["risk_analysis"].assessments) == 0
    assert "insufficient" in result["risk_analysis"].summary.lower()



# 11. Risk Agent with mocked LLM
@patch("app.agents.risk.llm_service")
def test_risk_agent_with_mock_llm(mock_llm_service):
    comp_analysis = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Missing backup protocol.",
        findings=[
            ComplianceFinding(
                control="Backup Protocol",
                status="partially_compliant",
                company_requirement="Weekly backups",
                regulatory_requirement="Daily backups",
                reasoning="Gap identified.",
                evidence=[]
            )
        ],
        confidence=0.80,
        evidence_sufficient=True
    )

    agent = RiskAgent()
    agent._chain = MagicMock()
    agent._chain.invoke.return_value = RiskAnalysisLLM(
        assessments=[
            RiskFactorAssessment(
                finding_id="finding_0",
                severity=4,
                likelihood=3,
                impact=4,
                rationale="Reasoning"
            )
        ],
        summary="Gaps in backups"
    )

    result = agent.assess(comp_analysis)
    assert len(result.assessments) == 1
    assert result.assessments[0].finding_id == "finding_0"
    assert result.assessments[0].severity == 4


# 12. Invalid severity/likelihood/impact handling (clamping)
def test_clamping_behavior():
    # calculate_risk_score clamps values internally
    assert calculate_risk_score(6, 3, 0) == 15  # clamps 6->5, 0->1 -> 5 * 3 * 1 = 15
    assert calculate_risk_score(-2, 10, 3) == 15  # clamps -2->1, 10->5 -> 1 * 5 * 3 = 15


# 13. Risk node state update
@patch("app.graph.nodes.risk_agent")
def test_risk_node_state_update(mock_risk_agent):
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="Sample text",
        source="policy.txt"
    )

    mock_risk_agent.assess.return_value = RiskAnalysisLLM(
        assessments=[
            RiskFactorAssessment(
                finding_id="finding_0",
                severity=4,
                likelihood=3,
                impact=4,
                rationale="Backup gap"
            )
        ],
        summary="High risk summary"
    )

    comp_analysis = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Gap identified.",
        findings=[
            ComplianceFinding(
                control="Backup Protocol",
                status="partially_compliant",
                company_requirement="Weekly",
                regulatory_requirement="Daily",
                reasoning="Weekly is not daily.",
                evidence=[evidence_obj]
            )
        ],
        confidence=0.85,
        evidence_sufficient=True
    )

    state = {
        "compliance_analysis": comp_analysis,
        "errors": []
    }

    result = risk_node(state)
    assert "risk_analysis" in result
    analysis = result["risk_analysis"]
    assert analysis.overall_risk_score == 48  # 4 * 3 * 4 = 48
    assert analysis.overall_risk_level == "medium"  # 48 <= 50 is medium
    assert len(analysis.assessments) == 1
    assert len(analysis.assessments[0].evidence) == 1
    assert analysis.assessments[0].evidence[0].filename == "policy.txt"


# 14. Full graph execution with mocked agents
@patch("app.graph.nodes.planner_agent")
@patch("app.graph.nodes.retrieval_service")
@patch("app.graph.nodes.compliance_agent")
@patch("app.graph.nodes.risk_agent")
@patch("app.graph.nodes.recommendation_agent")
def test_full_graph_execution(mock_rec_agent, mock_risk_agent, mock_compliance_agent, mock_retrieval_service, mock_planner_agent):
    mock_planner_agent.plan.return_value = PlannerOutput(
        audit_type="regulatory_compliance",
        subject="backup",
        regulation="GDPR",
        intent="Audit backups"
    )

    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="Weekly backup",
        source="policy.txt"
    )

    mock_retrieval_service.retrieve.return_value = RetrievalResult(
        question="Audit backups?",
        company_policy=[evidence_obj],
        regulations=[],
        confidence=0.80,
        confidence_level="high"
    )

    mock_compliance_agent.analyze.return_value = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Analysis",
        findings=[
            ComplianceFinding(
                control="Backups",
                status="partially_compliant",
                company_requirement="Weekly",
                regulatory_requirement="Daily",
                reasoning="Gap",
                evidence=[evidence_obj]
            )
        ],
        confidence=0.80,
        evidence_sufficient=True
    )

    mock_risk_agent.assess.return_value = RiskAnalysisLLM(
        assessments=[
            RiskFactorAssessment(
                finding_id="finding_0",
                severity=4,
                likelihood=4,
                impact=4,
                rationale="Reasoning"
            )
        ],
        summary="Risk analysis summary"
    )

    from app.models.recommendation_models import RecommendationAnalysisLLM
    mock_rec_agent.recommend.return_value = RecommendationAnalysisLLM(
        recommendations=[],
        summary="Remediation"
    )

    result = audit_graph_service.run_audit("Audit backups?")
    assert result["audit_type"] == "regulatory_compliance"
    assert result["risk_analysis"].overall_risk_score == 64  # 4*4*4=64
    assert result["risk_analysis"].overall_risk_level == "high"


# 15. /audit API response containing risk analysis
@patch("app.api.audit.audit_graph_service")
def test_audit_api_response_containing_risk(mock_graph_service):
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="Weekly backup",
        source="policy.txt"
    )

    mock_graph_service.run_audit.return_value = {
        "question": "Is backup compliant?",
        "audit_type": "regulatory_compliance",
        "subject": "backup",
        "regulation": "GDPR",
        "intent": "Verify backups",
        "retrieval_result": RetrievalResult(
            question="Is backup compliant?",
            company_policy=[evidence_obj],
            regulations=[],
            confidence=0.80,
            confidence_level="high"
        ),
        "retrieval_confidence": 0.80,
        "confidence_level": "high",
        "compliance_analysis": ComplianceAnalysis(
            overall_status="partially_compliant",
            summary="Gaps in backups",
            findings=[
                ComplianceFinding(
                    control="Backups",
                    status="partially_compliant",
                    company_requirement="Weekly",
                    regulatory_requirement="Daily",
                    reasoning="Weekly is not daily.",
                    evidence=[evidence_obj]
                )
            ],
            confidence=0.80,
            evidence_sufficient=True
        ),
        "compliance_confidence": 0.80,
        "risk_analysis": RiskAnalysis(
            overall_risk_level="high",
            overall_risk_score=64,
            assessments=[
                RiskAssessment(
                    finding_id="finding_0",
                    control="Backups",
                    risk_level="high",
                    severity=4,
                    likelihood=4,
                    impact=4,
                    risk_score=64,
                    rationale="Reasoning text.",
                    evidence=[evidence_obj]
                )
            ],
            summary="Backup gap is high risk."
        ),
        "errors": []
    }

    response = client.post(
        "/audit",
        json={"question": "Is backup compliant?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk" in data
    assert data["risk"]["overall_risk_score"] == 64
    assert data["risk"]["overall_risk_level"] == "high"
    assert len(data["risk"]["assessments"]) == 1
    assert data["risk"]["assessments"][0]["control"] == "Backups"
    assert len(data["risk"]["assessments"][0]["evidence"]) == 1
    assert data["risk"]["assessments"][0]["evidence"][0]["filename"] == "policy.txt"

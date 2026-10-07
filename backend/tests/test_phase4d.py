import uuid
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.models.evidence_models import Evidence, RetrievalResult
from app.models.compliance_models import ComplianceAnalysis, ComplianceFinding
from app.models.risk_models import RiskAnalysis, RiskAssessment, RiskAnalysisLLM, RiskFactorAssessment
from app.models.recommendation_models import (

    Recommendation,
    RecommendationAnalysis,
    RecommendationLLM,
    RecommendationAnalysisLLM
)
from app.models.recommendation_scoring import risk_level_to_priority
from app.agents.recommendation import RecommendationAgent
from app.graph.nodes import recommendation_node
from app.services.audit_graph import audit_graph_service
from app.models.planner_models import PlannerOutput
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Recommendation model validation
def test_recommendation_model_validation():
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.90,
        text="Sample text",
        source="policy.txt"
    )

    rec = Recommendation(
        finding_id="finding_0",
        control="Access Control",
        priority="high",
        recommendation="Enable MFA",
        rationale="Mitigates unauthorized access",
        implementation_steps=["1. Enable Identity Settings", "2. Enforce MFA"],
        evidence=[evidence_obj]
    )
    assert rec.finding_id == "finding_0"
    assert rec.priority == "high"
    assert len(rec.implementation_steps) == 2


# 2-6. Priority Mapping tests
def test_priority_mapping():
    assert risk_level_to_priority("critical") == "critical"
    assert risk_level_to_priority("high") == "high"
    assert risk_level_to_priority("medium") == "medium"
    assert risk_level_to_priority("low") == "low"
    assert risk_level_to_priority("UNKNOWN") == "low"


# 7. Finding-to-recommendation mapping & 10. Evidence Provenance
def test_finding_to_recommendation_evidence_preservation():
    doc_id = uuid.uuid4()
    evidence_obj = Evidence(
        document_id=doc_id,
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.90,
        text="Sample text",
        source="policy.txt"
    )

    comp_analysis = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Audit summary.",
        findings=[
            ComplianceFinding(
                control="Access Control",
                status="partially_compliant",
                company_requirement="MFA optional",
                regulatory_requirement="MFA required",
                reasoning="Gap",
                evidence=[evidence_obj]
            )
        ],
        confidence=0.80,
        evidence_sufficient=True
    )

    risk_analysis = RiskAnalysis(
        overall_risk_level="high",
        overall_risk_score=64,
        assessments=[
            RiskAssessment(
                finding_id="finding_0",
                control="Access Control",
                risk_level="high",
                severity=4,
                likelihood=4,
                impact=4,
                risk_score=64,
                rationale="Reasoning",
                evidence=[evidence_obj]
            )
        ],
        summary="Risk summary"
    )

    # In recommendation_node, verify that finding_id links exactly and evidence is preserved
    state = {
        "compliance_analysis": comp_analysis,
        "risk_analysis": risk_analysis,
        "errors": []
    }

    with patch("app.graph.nodes.recommendation_agent") as mock_agent:
        mock_agent.recommend.return_value = RecommendationAnalysisLLM(
            recommendations=[
                RecommendationLLM(
                    finding_id="finding_0",
                    recommendation="Enable MFA",
                    rationale="Resolves gap",
                    implementation_steps=["Steps here"]
                )
            ],
            summary="Rec Summary"
        )

        result = recommendation_node(state)
        rec_analysis = result["recommendation_analysis"]
        assert len(rec_analysis.recommendations) == 1
        recommendation = rec_analysis.recommendations[0]
        assert recommendation.finding_id == "finding_0"
        assert recommendation.control == "Access Control"
        assert recommendation.priority == "high"  # maps from risk_level "high"
        assert len(recommendation.evidence) == 1
        assert recommendation.evidence[0].document_id == doc_id


# 8. Fully compliant scenario
def test_fully_compliant_scenario():
    comp_analysis = ComplianceAnalysis(
        overall_status="compliant",
        summary="All compliant",
        findings=[
            ComplianceFinding(
                control="MFA",
                status="compliant",
                company_requirement="MFA required",
                regulatory_requirement="MFA required",
                reasoning="Both aligned",
                evidence=[]
            )
        ],
        confidence=0.90,
        evidence_sufficient=True
    )

    risk_analysis = RiskAnalysis(
        overall_risk_level="low",
        overall_risk_score=0,
        assessments=[],
        summary="No risks"
    )

    state = {
        "compliance_analysis": comp_analysis,
        "risk_analysis": risk_analysis,
        "errors": []
    }

    result = recommendation_node(state)
    rec_analysis = result["recommendation_analysis"]
    assert len(rec_analysis.recommendations) == 0
    assert rec_analysis.overall_priority == "low"
    assert "No remediation actions" in rec_analysis.summary


# 9. Insufficient evidence scenario
def test_insufficient_evidence_scenario():
    comp_analysis = ComplianceAnalysis(
        overall_status="insufficient_evidence",
        summary="No documents uploaded",
        findings=[],
        confidence=0.20,
        evidence_sufficient=False
    )

    risk_analysis = RiskAnalysis(
        overall_risk_level="low",
        overall_risk_score=0,
        assessments=[],
        summary="No risk calculated"
    )

    state = {
        "compliance_analysis": comp_analysis,
        "risk_analysis": risk_analysis,
        "errors": []
    }

    result = recommendation_node(state)
    rec_analysis = result["recommendation_analysis"]
    assert len(rec_analysis.recommendations) == 0
    assert rec_analysis.overall_priority == "low"
    assert "insufficient" in rec_analysis.summary.lower()


# 10. Recommendation Agent with mocked LLM
@patch("app.agents.recommendation.llm_service")
def test_recommendation_agent_with_mock_llm(mock_llm_service):
    comp_analysis = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Gaps",
        findings=[
            ComplianceFinding(
                control="Backup",
                status="partially_compliant",
                company_requirement="None",
                regulatory_requirement="Required",
                reasoning="Gap",
                evidence=[]
            )
        ],
        confidence=0.80,
        evidence_sufficient=True
    )

    risk_analysis = RiskAnalysis(
        overall_risk_level="medium",
        overall_risk_score=30,
        assessments=[
            RiskAssessment(
                finding_id="finding_0",
                control="Backup",
                risk_level="medium",
                severity=3,
                likelihood=5,
                impact=2,
                risk_score=30,
                rationale="Reason",
                evidence=[]
            )
        ],
        summary="Risk summary"
    )

    agent = RecommendationAgent()
    agent._chain = MagicMock()
    agent._chain.invoke.return_value = RecommendationAnalysisLLM(
        recommendations=[
            RecommendationLLM(
                finding_id="finding_0",
                recommendation="Create backup schedule",
                rationale="Resolves regulation",
                implementation_steps=["Enable backup script"]
            )
        ],
        summary="Summary"
    )

    result = agent.recommend(comp_analysis, risk_analysis)
    assert len(result.recommendations) == 1
    assert result.recommendations[0].finding_id == "finding_0"
    assert result.recommendations[0].recommendation == "Create backup schedule"


# 11. Invalid/Fabricated finding_id rejection in nodes validation
def test_invalid_finding_id_rejection():
    comp_analysis = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Gaps",
        findings=[
            ComplianceFinding(
                control="MFA",
                status="partially_compliant",
                company_requirement="Optional",
                regulatory_requirement="Mandatory",
                reasoning="Gap",
                evidence=[]
            )
        ],
        confidence=0.80,
        evidence_sufficient=True
    )

    risk_analysis = RiskAnalysis(
        overall_risk_level="high",
        overall_risk_score=64,
        assessments=[
            RiskAssessment(
                finding_id="finding_0",
                control="MFA",
                risk_level="high",
                severity=4,
                likelihood=4,
                impact=4,
                risk_score=64,
                rationale="Reasoning",
                evidence=[]
            )
        ],
        summary="Risk summary"
    )

    state = {
        "compliance_analysis": comp_analysis,
        "risk_analysis": risk_analysis,
        "errors": []
    }

    with patch("app.graph.nodes.recommendation_agent") as mock_agent:
        mock_agent.recommend.return_value = RecommendationAnalysisLLM(
            recommendations=[
                RecommendationLLM(
                    finding_id="finding_99",  # Hallucinated invalid id
                    recommendation="Enable MFA",
                    rationale="Reasoning",
                    implementation_steps=["Step"]
                )
            ],
            summary="Summary text"
        )

        result = recommendation_node(state)
        # Verify that finding_99 is safely rejected and skipped
        assert len(result["recommendation_analysis"].recommendations) == 0


# 12. Missing ComplianceAnalysis handling
def test_recommendation_node_missing_compliance():
    state = {
        "compliance_analysis": None,
        "risk_analysis": RiskAnalysis(overall_risk_level="low", overall_risk_score=0, assessments=[], summary=""),
        "errors": []
    }
    with pytest.raises(ValueError) as exc:
        recommendation_node(state)
    assert "compliance_analysis is missing" in str(exc.value)


# 13. Missing RiskAnalysis handling
def test_recommendation_node_missing_risk():
    state = {
        "compliance_analysis": ComplianceAnalysis(overall_status="compliant", summary="", findings=[], confidence=1.0, evidence_sufficient=True),
        "risk_analysis": None,
        "errors": []
    }
    with pytest.raises(ValueError) as exc:
        recommendation_node(state)
    assert "risk_analysis is missing" in str(exc.value)


# 14. Recommendation node state update
@patch("app.graph.nodes.recommendation_agent")
def test_recommendation_node_state_update(mock_rec_agent):
    mock_rec_agent.recommend.return_value = RecommendationAnalysisLLM(
        recommendations=[
            RecommendationLLM(
                finding_id="finding_0",
                recommendation="Upgrade software",
                rationale="Reasoning",
                implementation_steps=["Step 1"]
            )
        ],
        summary="Upgrade steps"
    )

    comp_analysis = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Gaps",
        findings=[
            ComplianceFinding(
                control="Updates",
                status="partially_compliant",
                company_requirement="Outdated",
                regulatory_requirement="Updated",
                reasoning="Gap",
                evidence=[]
            )
        ],
        confidence=0.80,
        evidence_sufficient=True
    )

    risk_analysis = RiskAnalysis(
        overall_risk_level="medium",
        overall_risk_score=36,
        assessments=[
            RiskAssessment(
                finding_id="finding_0",
                control="Updates",
                risk_level="medium",
                severity=3,
                likelihood=4,
                impact=3,
                risk_score=36,
                rationale="Reasoning",
                evidence=[]
            )
        ],
        summary="Risk summary"
    )

    state = {
        "compliance_analysis": comp_analysis,
        "risk_analysis": risk_analysis,
        "errors": []
    }

    result = recommendation_node(state)
    assert "recommendation_analysis" in result
    analysis = result["recommendation_analysis"]
    assert len(analysis.recommendations) == 1
    assert analysis.overall_priority == "medium"
    assert analysis.recommendations[0].priority == "medium"


# 15. Full graph execution with mocked agents
@patch("app.graph.nodes.planner_agent")
@patch("app.graph.nodes.retrieval_service")
@patch("app.graph.nodes.compliance_agent")
@patch("app.graph.nodes.risk_agent")
@patch("app.graph.nodes.recommendation_agent")
def test_full_graph_execution(mock_rec_agent, mock_risk_agent, mock_comp_agent, mock_retrieval_service, mock_planner_agent):
    mock_planner_agent.plan.return_value = PlannerOutput(
        audit_type="regulatory_compliance",
        subject="access_control",
        regulation="ISO 27001",
        intent="Audit access control"
    )

    evidence_obj = Evidence(
        document_id=uuid.uuid4(),
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="No MFA",
        source="policy.txt"
    )

    mock_retrieval_service.retrieve.return_value = RetrievalResult(
        question="MFA audit?",
        company_policy=[evidence_obj],
        regulations=[],
        confidence=0.80,
        confidence_level="high"
    )

    mock_comp_agent.analyze.return_value = ComplianceAnalysis(
        overall_status="partially_compliant",
        summary="Gaps in MFA",
        findings=[
            ComplianceFinding(
                control="MFA Control",
                status="partially_compliant",
                company_requirement="Optional",
                regulatory_requirement="Mandatory",
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
                impact=5,
                rationale="Reason"
            )
        ],
        summary="Risk Landscape"
    )

    mock_rec_agent.recommend.return_value = RecommendationAnalysisLLM(
        recommendations=[
            RecommendationLLM(
                finding_id="finding_0",
                recommendation="Enforce MFA settings",
                rationale="Resolves non-compliance",
                implementation_steps=["Step 1", "Step 2"]
            )
        ],
        summary="Remediation strategy"
    )

    result = audit_graph_service.run_audit("MFA audit?")
    assert result["audit_type"] == "regulatory_compliance"
    assert result["risk_analysis"].overall_risk_score == 80  # 4 * 4 * 5 = 80
    assert result["recommendation_analysis"].overall_priority == "high"  # maps from risk_level "high"
    assert len(result["recommendation_analysis"].recommendations) == 1
    assert result["recommendation_analysis"].recommendations[0].control == "MFA Control"


# 16. /audit API response structure containing recommendations
@patch("app.api.audit.audit_graph_service")
def test_audit_api_response_containing_recommendations(mock_graph_service):
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
        "recommendation_analysis": RecommendationAnalysis(
            recommendations=[
                Recommendation(
                    finding_id="finding_0",
                    control="Backups",
                    priority="high",
                    recommendation="Enable daily cron backups",
                    rationale="Ensures daily backup regulation is met.",
                    implementation_steps=["1. Configure daily cron script", "2. Monitor logs"],
                    evidence=[evidence_obj]
                )
            ],
            summary="Overall remediation schedule",
            overall_priority="high"
        ),
        "errors": []
    }

    response = client.post(
        "/audit",
        json={"question": "Is backup compliant?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert data["recommendations"]["overall_priority"] == "high"
    assert len(data["recommendations"]["recommendations"]) == 1
    assert data["recommendations"]["recommendations"][0]["control"] == "Backups"
    assert len(data["recommendations"]["recommendations"][0]["implementation_steps"]) == 2
    assert data["recommendations"]["recommendations"][0]["evidence"][0]["filename"] == "policy.txt"

import uuid
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.models.evidence_models import Evidence, RetrievalResult
from app.models.compliance_models import ComplianceAnalysis, ComplianceFinding
from app.models.risk_models import RiskAnalysis, RiskAssessment
from app.models.review_models import (
    ConfidenceGateResult,
    HumanReviewRequest,
    HumanReviewDecision,
    ReviewReason,
    ReviewStatus
)
from app.services.confidence_gate import confidence_gate_service
from app.graph.nodes import confidence_gate_node, human_review_node
from app.graph.workflow import route_after_gate, audit_graph, END
from app.database.schema import HumanReview
from app.database.connection import engine, Base
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app

# Ensure database tables exist for test client execution
Base.metadata.create_all(bind=engine)

client = TestClient(app)



# Dummy inputs helper
def get_dummy_compliance_analysis(status="compliant", reasoning="All good.", confidence=0.90):
    return ComplianceAnalysis(
        overall_status=status,
        summary="Compliant summary",
        findings=[
            ComplianceFinding(
                control="Access Control",
                status=status,
                company_requirement="Require password complexity",
                regulatory_requirement="Require password complexity",
                reasoning=reasoning,
                evidence=[]
            )
        ],
        confidence=confidence,
        evidence_sufficient=True
    )


def get_dummy_risk_analysis(level="low", score=10):
    return RiskAnalysis(
        overall_risk_level=level,
        overall_risk_score=score,
        assessments=[],
        summary="Risk summary"
    )


# 1. ConfidenceGateService with high confidence -> review_required = false
def test_gate_high_confidence():
    comp = get_dummy_compliance_analysis()
    risk = get_dummy_risk_analysis()
    res = confidence_gate_service.evaluate_gate(
        retrieval_confidence=0.85,
        compliance_analysis=comp,
        compliance_confidence=0.90,
        risk_analysis=risk
    )
    assert res.review_required is False
    assert len(res.reasons) == 0


# 2. Low retrieval confidence -> review_required = true
def test_gate_low_retrieval_confidence():
    comp = get_dummy_compliance_analysis()
    risk = get_dummy_risk_analysis()
    res = confidence_gate_service.evaluate_gate(
        retrieval_confidence=0.35,  # < 0.50
        compliance_analysis=comp,
        compliance_confidence=0.90,
        risk_analysis=risk
    )
    assert res.review_required is True
    assert "low_retrieval_confidence" in res.reasons


# 3. Low compliance confidence -> review_required = true
def test_gate_low_compliance_confidence():
    comp = get_dummy_compliance_analysis(confidence=0.40)
    risk = get_dummy_risk_analysis()
    res = confidence_gate_service.evaluate_gate(
        retrieval_confidence=0.85,
        compliance_analysis=comp,
        compliance_confidence=0.40,  # < 0.50
        risk_analysis=risk
    )
    assert res.review_required is True
    assert "low_compliance_confidence" in res.reasons


# 4. Insufficient evidence -> review_required = true
def test_gate_insufficient_evidence():
    comp = get_dummy_compliance_analysis(status="insufficient_evidence")
    risk = get_dummy_risk_analysis()
    res = confidence_gate_service.evaluate_gate(
        retrieval_confidence=0.85,
        compliance_analysis=comp,
        compliance_confidence=0.80,
        risk_analysis=risk
    )
    assert res.review_required is True
    assert "insufficient_evidence" in res.reasons


# 5. Critical risk -> review_required = true
def test_gate_critical_risk():
    comp = get_dummy_compliance_analysis()
    risk = get_dummy_risk_analysis(level="critical", score=100)
    res = confidence_gate_service.evaluate_gate(
        retrieval_confidence=0.85,
        compliance_analysis=comp,
        compliance_confidence=0.80,
        risk_analysis=risk
    )
    assert res.review_required is True
    assert "high_risk" in res.reasons


# 6. Multiple review reasons & Rule 5 conflicts
def test_gate_multiple_reasons_and_conflicts():
    # Trigger conflict by having "conflict" in reasoning
    comp = get_dummy_compliance_analysis(status="non_compliant", confidence=0.30, reasoning="Unresolved conflict exists.")
    risk = get_dummy_risk_analysis(level="critical", score=100)
    res = confidence_gate_service.evaluate_gate(
        retrieval_confidence=0.20,
        compliance_analysis=comp,
        compliance_confidence=0.30,
        risk_analysis=risk
    )
    assert res.review_required is True
    assert "low_retrieval_confidence" in res.reasons
    assert "low_compliance_confidence" in res.reasons
    assert "high_risk" in res.reasons
    assert "policy_or_regulation_conflict" in res.reasons


# 7. Confidence gate node
def test_confidence_gate_node():
    comp = get_dummy_compliance_analysis()
    risk = get_dummy_risk_analysis()
    state = {
        "retrieval_confidence": 0.85,
        "compliance_analysis": comp,
        "compliance_confidence": 0.90,
        "risk_analysis": risk,
        "errors": []
    }
    res = confidence_gate_node(state)
    assert res["review_required"] is False
    assert res["review_status"] == "not_required"
    assert len(res["review_reasons"]) == 0


# 8. Conditional routing to END
def test_conditional_routing_to_end():
    state = {"review_required": False}
    assert route_after_gate(state) in (END, "report")




# 9. Conditional routing to human review
def test_conditional_routing_to_human_review():
    state = {"review_required": True}
    assert route_after_gate(state) == "human_review"


# 10. Human review request creation
def test_human_review_node():
    state = {
        "review_decision": "approve",
        "reviewer_comment": "Excellent work",
        "errors": []
    }
    res = human_review_node(state)
    assert res["review_status"] == "approved"


# 11-13. Approve, Reject, and Request-more-evidence actions validation
def test_human_review_node_decisions():
    assert human_review_node({"review_decision": "approve"})["review_status"] == "approved"
    assert human_review_node({"review_decision": "reject"})["review_status"] == "rejected"
    assert human_review_node({"review_decision": "request_more_evidence"})["review_status"] == "needs_more_evidence"
    assert human_review_node({"review_decision": "other"})["review_status"] == "pending"


# 14. Invalid review decision validation in endpoints
@patch("app.api.review.get_db")
def test_invalid_review_decision(mock_get_db):
    response = client.post(
        "/review/some_id/decision",
        json={
            "review_id": "some_id",
            "decision": "invalid_decision",  # invalid
            "reviewer_comment": "Comment",
            "selected_action": "continue"
        }
    )
    assert response.status_code == 422  # validation error


# 15. Review of already completed request validation
def test_completed_review_error_handling():
    # Set up mock DB
    mock_db = MagicMock()
    # Mocking completed review
    mock_record = HumanReview(
        review_id="rev_1",
        thread_id="thread_1",
        question="Question",
        status="approved",  # already completed!
        reasons="high_risk",
        created_at=datetime.utcnow()
    )
    mock_db.query().filter().first.return_value = mock_record

    from app.api.review import post_human_review_decision
    with pytest.raises(HTTPException) as exc:
        post_human_review_decision(
            review_id="rev_1",
            decision_data=HumanReviewDecision(
                review_id="rev_1",
                decision="approve",
                reviewer_comment="Retry",
                selected_action="continue"
            ),
            db=mock_db
        )
    assert exc.value.status_code == 400
    assert "already completed" in exc.value.detail


# 16. Review Persistence & 18. GET /review/{review_id}
@patch("app.api.review.audit_graph")
def test_get_review_route_persistence(mock_graph):
    # Set up mock DB and checkpointer state
    mock_db = MagicMock()
    mock_record = HumanReview(
        review_id="rev_2",
        thread_id="thread_2",
        question="Is access control compliant?",
        status="pending",
        reasons="high_risk",
        retrieval_confidence=0.90,
        compliance_confidence=0.85,
        risk_level="critical",
        risk_score=100,
        created_at=datetime.utcnow()
    )
    mock_db.query().filter().first.return_value = mock_record

    mock_state = MagicMock()
    mock_state.values = {
        "compliance_analysis": get_dummy_compliance_analysis(),
        "recommendation_analysis": None
    }
    mock_graph.get_state.return_value = mock_state

    from app.api.review import get_human_review_request
    res = get_human_review_request(review_id="rev_2", db=mock_db)
    assert res.review_id == "rev_2"
    assert res.review_status == "pending"
    assert "high_risk" in res.reasons
    assert res.risk_level == "critical"
    assert len(res.findings) == 1


# 17. Graph interrupt/resume behavior and 19. Decision submission
@patch("app.api.review.audit_graph")
def test_post_decision_route_flow(mock_graph):
    mock_db = MagicMock()
    mock_record = HumanReview(
        review_id="rev_3",
        thread_id="thread_3",
        question="Audit?",
        status="pending",
        reasons="low_retrieval_confidence",
        created_at=datetime.utcnow()
    )
    mock_db.query().filter().first.return_value = mock_record

    from app.api.review import post_human_review_decision
    res = post_human_review_decision(
        review_id="rev_3",
        decision_data=HumanReviewDecision(
            review_id="rev_3",
            decision="reject",
            reviewer_comment="Fail",
            selected_action="terminate"
        ),
        db=mock_db
    )
    assert res["status"] == "rejected"
    assert mock_db.commit.called
    mock_graph.update_state.assert_called_once()
    mock_graph.invoke.assert_called_once()



# 20. Full graph execution with mocked LLM agents
@patch("app.graph.nodes.planner_agent")
@patch("app.graph.nodes.retrieval_service")
@patch("app.graph.nodes.compliance_agent")
@patch("app.graph.nodes.risk_agent")
@patch("app.graph.nodes.recommendation_agent")
@patch("app.api.audit.get_db")
def test_full_graph_routing_interrupt(mock_db_dep, mock_rec_agent, mock_risk_agent, mock_comp_agent, mock_retrieval_service, mock_planner):
    # Set up mocks
    from app.models.planner_models import PlannerOutput
    mock_planner.plan.return_value = PlannerOutput(
        audit_type="regulatory_compliance",
        subject="access",
        regulation="ISO 27001",
        intent="Audit"
    )

    evidence_obj = Evidence(
        document_id=uuid.uuid4(),
        document_version="1.0.0",
        filename="policy.txt",
        document_type="company_policy",
        page_number=1,
        chunk_index=0,
        similarity_score=0.85,
        text="Sample",
        source="policy.txt"
    )

    mock_retrieval_service.retrieve.return_value = RetrievalResult(
        question="Audit access?",
        company_policy=[evidence_obj],
        regulations=[],
        confidence=0.40,  # < 0.50 -> Triggers confidence gate low_retrieval_confidence review!
        confidence_level="low"
    )

    mock_comp_agent.analyze.return_value = get_dummy_compliance_analysis(status="partially_compliant")
    
    from app.models.risk_models import RiskAnalysisLLM, RiskFactorAssessment
    mock_risk_agent.assess.return_value = RiskAnalysisLLM(
        assessments=[
            RiskFactorAssessment(
                finding_id="finding_0",
                severity=3,
                likelihood=3,
                impact=3,
                rationale="Reason"
            )
        ],
        summary="Risk landscape"
    )

    from app.models.recommendation_models import RecommendationAnalysisLLM
    mock_rec_agent.recommend.return_value = RecommendationAnalysisLLM(
        recommendations=[],
        summary="Remediation"
    )

    # Mock DB sessions
    mock_sess = MagicMock()
    mock_db_dep.return_value = mock_sess

    # Run audit request via client
    response = client.post(
        "/audit",
        json={"question": "Audit access?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "review_required"
    assert "review_id" in data
    assert "thread_id" in data
    assert "low_retrieval_confidence" in data["reasons"]

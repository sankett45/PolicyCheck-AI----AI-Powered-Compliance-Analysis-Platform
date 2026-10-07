import uuid
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.models.evidence_models import Evidence, RetrievalResult
from app.models.compliance_models import ComplianceAnalysis, ComplianceFinding
from app.models.risk_models import RiskAnalysis, RiskAssessment
from app.models.recommendation_models import RecommendationAnalysis, Recommendation
from app.models.report_models import AuditReport, ReportStatus, HumanReviewDetail
from app.services.report_generator import report_generator_service
from app.graph.nodes import report_node
from app.graph.workflow import route_after_gate, route_after_review, audit_graph, END
from app.database.schema import AuditReport as DBAuditReport, HumanReview as DBReview
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

client = TestClient(app)


# Helpers for dummy inputs
def get_dummy_compliance_analysis(status="compliant", reasoning="All good.", confidence=0.90, has_evidence=True):
    ev = []
    if has_evidence:
        ev.append(
            Evidence(
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
        )
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
                evidence=ev
            )
        ],
        confidence=confidence,
        evidence_sufficient=True
    )


def get_dummy_risk_analysis(level="low", score=10):
    return RiskAnalysis(
        overall_risk_level=level,
        overall_risk_score=score,
        assessments=[
            RiskAssessment(
                finding_id="finding_0",
                control="Access Control",
                risk_level=level,
                severity=2,
                likelihood=2,
                impact=2,
                risk_score=score,
                rationale="Analytical risk rationale",
                evidence=[]
            )
        ],
        summary="Risk summary"
    )


def get_dummy_recommendation_analysis(priority="low"):
    return RecommendationAnalysis(
        recommendations=[
            Recommendation(
                finding_id="finding_0",
                control="Access Control",
                priority=priority,
                recommendation="Fix it",
                rationale="Analytical rec rationale",
                implementation_steps=["Step 1"],
                evidence=[]
            )
        ],
        summary="Rec summary",
        overall_priority=priority
    )


# 1. AuditReport model validation & 2. ReportStatus validation
def test_report_models_validation():
    report_id = str(uuid.uuid4())
    audit_id = str(uuid.uuid4())
    report = AuditReport(
        report_id=report_id,
        audit_id=audit_id,
        question="Is it compliant?",
        audit_type="compliance",
        subject="access",
        regulation="ISO 27001",
        executive_summary="Summary",
        overall_compliance_status="compliant",
        overall_risk_level="low",
        overall_risk_score=10,
        findings=[],
        risk_assessments=[],
        recommendations=[],
        evidence_summary=[],
        human_review=None,
        generated_at=datetime.utcnow(),
        report_version=1,
        status=ReportStatus.final
    )
    assert report.report_id == report_id
    assert report.status == ReportStatus.final
    assert report.status.value == "final"


# 3. Report assembly from valid AuditState, 9. Evidence provenance, 10. Finding->Risk->Rec Traceability
@patch.object(report_generator_service, "report_agent")
def test_report_assembly_from_state(mock_agent):
    mock_agent.generate_summary.return_value = "Mock Executive Summary"


    db_mock = MagicMock()
    # Mock DBAuditReport counts (existing report count = 0 -> version 1)
    db_mock.query().filter().count.return_value = 0

    state = {
        "question": "Is it compliant?",
        "audit_type": "regulatory_compliance",
        "subject": "Access Control",
        "regulation": "ISO 27001",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis(),
        "review_required": False,
        "review_status": "not_required"
    }

    report = report_generator_service.generate_report(state, "thread_id_123", db_mock)
    assert report.status == ReportStatus.final
    assert report.report_version == 1
    assert report.executive_summary == "Mock Executive Summary"
    assert len(report.findings) == 1
    assert report.findings[0].finding_id == "finding_0"  # deterministic assignment
    assert report.risk_assessments[0].finding_id == "finding_0"  # traceability mapped
    assert report.recommendations[0].finding_id == "finding_0"  # traceability mapped
    assert len(report.evidence_summary) == 1  # provenance preserved
    assert report.evidence_summary[0].filename == "policy.txt"


# 4. Executive summary generation with mocked LLM
@patch.object(report_generator_service, "report_agent")
def test_executive_summary_llm_mock(mock_agent):
    mock_agent.generate_summary.return_value = "Specific LLM Summary"
    db_mock = MagicMock()
    db_mock.query().filter().count.return_value = 0

    state = {
        "question": "Q?",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis()
    }
    report = report_generator_service.generate_report(state, "thread_123", db_mock)
    assert report.executive_summary == "Specific LLM Summary"


# 5. No report when review is pending & 8. No report when more evidence is required
def test_no_report_on_pending_or_evidence_missing():
    db_mock = MagicMock()
    # Case 2: review_required=True, review_decision=None (pending)
    state_pending = {
        "question": "Q",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis(),
        "review_required": True,
        "review_status": "pending",
        "review_decision": None
    }
    report = report_generator_service.generate_report(state_pending, "thread_p", db_mock)
    assert report.status == ReportStatus.pending_review
    assert report.executive_summary == "Executive summary is pending human review approval."

    # Case 5: review_status=needs_more_evidence
    state_more_ev = {
        "question": "Q",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis(),
        "review_required": True,
        "review_status": "needs_more_evidence",
        "review_decision": "request_more_evidence"
    }
    report_more = report_generator_service.generate_report(state_more_ev, "thread_more", db_mock)
    assert report_more.status == ReportStatus.pending_review

    # Compliant control findings with missing evidence list -> should fallback to pending_review
    state_no_ev = {
        "question": "Q",
        "compliance_analysis": get_dummy_compliance_analysis(has_evidence=False),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis()
    }
    report_no_ev = report_generator_service.generate_report(state_no_ev, "thread_no_ev", db_mock)
    assert report_no_ev.status == ReportStatus.pending_review


# 6. Report generated after approved review
@patch.object(report_generator_service, "report_agent")
def test_report_approved_review(mock_agent):
    mock_agent.generate_summary.return_value = "Summary text"
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = DBReview(
        review_id="rev_1",
        thread_id="thread_app",
        question="Q",
        status="approved",
        reasons="high_risk",
        decision="approve",
        reviewer_comment="Fine"
    )

    state = {
        "question": "Q",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis(),
        "review_required": True,
        "review_status": "approved",
        "review_decision": "approve"
    }
    report = report_generator_service.generate_report(state, "thread_app", db_mock)
    assert report.status == ReportStatus.final
    assert report.human_review is not None
    assert report.human_review.reviewer_decision == "approve"


# 7. No report after rejected review
def test_report_rejected_review():
    db_mock = MagicMock()
    state = {
        "question": "Q",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis(),
        "review_required": True,
        "review_status": "rejected",
        "review_decision": "reject"
    }
    report = report_generator_service.generate_report(state, "thread_rej", db_mock)
    assert report.status == ReportStatus.rejected
    assert report.executive_summary == "Report rejected by human reviewer."


# 11. Report versioning
def test_report_versioning_increments():
    db_mock = MagicMock()
    # Mock count to return 2 existing reports (meaning next version is 3)
    db_mock.query().filter().count.return_value = 2

    state = {
        "question": "Q",
        "compliance_analysis": get_dummy_compliance_analysis(),
        "risk_analysis": get_dummy_risk_analysis(),
        "recommendation_analysis": get_dummy_recommendation_analysis()
    }
    report = report_generator_service.generate_report(state, "thread_v3", db_mock)
    assert report.report_version == 3


# 12. Report persistence & 13. GET /reports/{report_id} & 14. GET /reports/{report_id}/evidence & 15. GET /reports/{report_id}/download
def test_reports_api_endpoints():
    from app.database.connection import get_db
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    # Create dummy database report record
    db_report = DBAuditReport(
        report_id="rep_999",
        audit_id="audit_999",
        question="Is access control compliant?",
        status="final",
        executive_summary="Executive summary content.",
        audit_type="regulatory_compliance",
        subject="access_control",
        regulation="ISO 27001",
        overall_compliance_status="compliant",
        overall_risk_level="low",
        overall_risk_score=0,
        report_version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        findings=[get_dummy_compliance_analysis().findings[0].model_dump()],
        risk_assessments=[get_dummy_risk_analysis().assessments[0].model_dump()],
        recommendations=[get_dummy_recommendation_analysis().recommendations[0].model_dump()],
        evidence_summary=[get_dummy_compliance_analysis().findings[0].evidence[0].model_dump()],
        human_review=None
    )

    mock_db.query().filter().first.return_value = db_report

    try:
        # Test GET /reports/{report_id}
        res = client.get("/reports/rep_999")
        assert res.status_code == 200
        assert res.json()["report_id"] == "rep_999"
        assert res.json()["overall_compliance_status"] == "compliant"

        # Test GET /reports/{report_id}/evidence
        res_ev = client.get("/reports/rep_999/evidence")
        assert res_ev.status_code == 200
        assert len(res_ev.json()) == 1
        assert res_ev.json()[0]["filename"] == "policy.txt"

        # Test GET /reports/{report_id}/download
        res_dl = client.get("/reports/rep_999/download")
        assert res_dl.status_code == 200
        assert "text/markdown" in res_dl.headers["content-type"]
        assert "attachment; filename=audit_report_rep_999.md" in res_dl.headers["content-disposition"]
        assert "Audit Report: Access Control" in res_dl.text
    finally:
        app.dependency_overrides.clear()



# 16. Full LangGraph execution with mocked agents & 17. Final /audit API response
@patch("app.graph.nodes.planner_agent")
@patch("app.graph.nodes.retrieval_service")
@patch("app.graph.nodes.compliance_agent")
@patch("app.graph.nodes.risk_agent")
@patch("app.graph.nodes.recommendation_agent")
@patch("app.api.audit.get_db")
def test_full_graph_routing_report_completion(mock_db_dep, mock_rec_agent, mock_risk_agent, mock_comp_agent, mock_retrieval_service, mock_planner):
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
        text="Sample text",
        source="policy.txt"
    )

    mock_retrieval_service.retrieve.return_value = RetrievalResult(
        question="Audit access?",
        company_policy=[evidence_obj],
        regulations=[],
        confidence=0.85,  # High confidence -> no review required
        confidence_level="high"
    )

    mock_comp_agent.analyze.return_value = get_dummy_compliance_analysis()
    
    from app.models.risk_models import RiskAnalysisLLM, RiskFactorAssessment
    mock_risk_agent.assess.return_value = RiskAnalysisLLM(
        assessments=[
            RiskFactorAssessment(
                finding_id="finding_0",
                severity=1,
                likelihood=1,
                impact=1,
                rationale="Low risk rationale"
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
    mock_sess.query().filter().count.return_value = 0

    response = client.post(
        "/audit",
        json={"question": "Audit access?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "report_id" in data
    assert "report" in data
    assert data["report"]["overall_compliance_status"] == "compliant"

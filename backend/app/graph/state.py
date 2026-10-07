from typing import TypedDict, List, Optional, Any, Dict
from app.models.evidence_models import RetrievalResult
from app.models.compliance_models import ComplianceAnalysis
from app.models.risk_models import RiskAnalysis
from app.models.recommendation_models import RecommendationAnalysis


class AuditState(TypedDict):
    """LangGraph state schema for the AuditFlow AI compliance audit assistant."""

    # Core Phase 4A fields
    question: str
    audit_type: Optional[str]
    subject: Optional[str]
    regulation: Optional[str]
    intent: Optional[str]
    retrieval_result: Optional[RetrievalResult]
    confidence: Optional[float]
    confidence_level: Optional[str]
    errors: List[str]

    # Core Phase 4B fields
    compliance_analysis: Optional[ComplianceAnalysis]
    retrieval_confidence: Optional[float]
    compliance_confidence: Optional[float]

    # Core Phase 4C fields
    risk_analysis: Optional[RiskAnalysis]

    # Core Phase 4D fields
    recommendation_analysis: Optional[RecommendationAnalysis]

    # Core Phase 4E fields
    review_status: Optional[str]
    review_required: Optional[bool]
    review_reasons: Optional[List[str]]
    review_id: Optional[str]
    review_decision: Optional[str]
    reviewer_comment: Optional[str]
    review_request: Optional[Dict[str, Any]]

    # Reserved fields for future agent phases (Phase 4F)
    compliance_findings: Optional[List[Any]]
    risk_assessment: Optional[Dict[str, Any]]
    recommendations: Optional[List[Any]]
    review_status_legacy: Optional[str]
    final_report: Optional[Dict[str, Any]]





from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.compliance_models import ComplianceFinding
from app.models.recommendation_models import Recommendation

ReviewStatus = Literal["not_required", "pending", "approved", "rejected", "needs_more_evidence"]

ReviewReason = Literal[
    "low_retrieval_confidence",
    "low_compliance_confidence",
    "insufficient_evidence",
    "high_risk",
    "policy_or_regulation_conflict",
    "manual_review_required"
]


class ConfidenceGateResult(BaseModel):
    """Pydantic model representing deterministic results returned from the ConfidenceGateService."""

    review_required: bool = Field(..., description="Whether a human review is required")
    reasons: List[ReviewReason] = Field(..., description="List of reasons triggering the review")
    retrieval_confidence: float = Field(..., description="The internal retrieval confidence signal score")
    compliance_confidence: float = Field(..., description="The internal compliance confidence signal score")
    risk_level: str = Field(..., description="The evaluated risk level of findings")
    risk_score: int = Field(..., description="The evaluated risk score of findings")


class HumanReviewRequest(BaseModel):
    """Pydantic model representing the context package exposed to human reviewers."""

    review_id: str = Field(..., description="Unique identifier for the review request")
    question: str = Field(..., description="The original compliance query being audited")
    review_status: ReviewStatus = Field(..., description="Current status of the review request")
    reasons: List[ReviewReason] = Field(..., description="Reasons why this review request was triggered")
    retrieval_confidence: float = Field(..., description="Quality score of the retrieved evidence")
    compliance_confidence: float = Field(..., description="Confidence score of the compliance analysis")
    risk_level: str = Field(..., description="Evaluated risk posture level")
    risk_score: int = Field(..., description="Evaluated risk posture score")
    compliance_summary: str = Field(..., description="Summary overview of compliance gaps")
    findings: List[ComplianceFinding] = Field(..., description="Trace compliance control evaluations")
    recommendations: List[Recommendation] = Field(..., description="Actionable remediation recommendations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class HumanReviewDecision(BaseModel):
    """Pydantic model representing input parameters sent by a reviewer resolving a request."""

    review_id: str = Field(..., description="Unique identifier of the review request")
    decision: Literal["approve", "reject", "request_more_evidence"] = Field(..., description="The resolution decision")
    reviewer_comment: str = Field(..., description="Text comment describing reasoning for this decision")
    selected_action: Literal["continue", "terminate", "retrieve_more_evidence"] = Field(..., description="Action to route execution path")

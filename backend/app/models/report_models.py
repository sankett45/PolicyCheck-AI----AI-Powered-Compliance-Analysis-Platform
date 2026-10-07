from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.models.evidence_models import Evidence
from app.models.compliance_models import ComplianceFinding
from app.models.risk_models import RiskAssessment
from app.models.recommendation_models import Recommendation


class ReportStatus(str, Enum):
    """Allowed publication statuses for the synthesized audit report."""
    draft = "draft"
    final = "final"
    rejected = "rejected"
    pending_review = "pending_review"


class HumanReviewDetail(BaseModel):
    """Detailed summary of the human-in-the-loop review outcome."""
    review_status: str = Field(..., description="Review status: pending, approved, rejected, needs_more_evidence")
    reviewer_decision: Optional[str] = Field(None, description="Reviewer decision choice (approve, reject, request_more_evidence)")
    reviewer_comment: Optional[str] = Field(None, description="Reviewer feedback or rationale")
    timestamp: Optional[datetime] = Field(None, description="Time when reviewer action was submitted")


class AuditReport(BaseModel):
    """Synthesized production audit report wrapping all verified upstream agent findings."""
    report_id: str = Field(..., description="Unique UUID identifier for this report")
    audit_id: str = Field(..., description="Unique UUID identifier for the audit session")
    question: str = Field(..., description="Original user compliance question")
    audit_type: str = Field(..., description="Inferred audit classification category")
    subject: str = Field(..., description="Target control area subject")
    regulation: str = Field(..., description="Compliance regulation evaluated")
    executive_summary: str = Field(default="", description="Generated executive summary summarizing verified findings")
    overall_compliance_status: str = Field(..., description="Consolidated compliance status")
    overall_risk_level: str = Field(..., description="Aggregated risk level across findings")
    overall_risk_score: int = Field(..., description="Aggregated risk score")
    findings: List[ComplianceFinding] = Field(default_factory=list, description="Verified compliance agent findings")
    risk_assessments: List[RiskAssessment] = Field(default_factory=list, description="Verified risk agent assessments")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Verified recommendation agent suggestions")
    evidence_summary: List[Evidence] = Field(default_factory=list, description="Summary of evidence references and provenance")
    human_review: Optional[HumanReviewDetail] = Field(None, description="Historical human-in-the-loop review detail logs")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of report generation")
    report_version: int = Field(default=1, description="Version index of the report")
    status: ReportStatus = Field(default=ReportStatus.draft, description="Current report lifecycle status")

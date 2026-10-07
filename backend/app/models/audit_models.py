from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.evidence_models import Evidence
from app.models.compliance_models import ComplianceAnalysis
from app.models.risk_models import RiskAnalysis
from app.models.recommendation_models import RecommendationAnalysis


class AuditRequest(BaseModel):
    """Validation schema for query audit requests."""

    question: str = Field(..., min_length=1, description="Compliance question to audit")


class AuditPlannerResponse(BaseModel):
    """Pydantic model representing structured planner state inside audit response."""

    audit_type: str = Field(..., description="Categorized audit type")
    subject: str = Field(..., description="Categorized audit subject")
    regulation: Optional[str] = Field(None, description="Target regulation framework")
    intent: str = Field(..., description="Audit evaluation intent description")


class AuditRetrievalResponse(BaseModel):
    """Pydantic model representing structured retrieval state inside audit response."""

    company_policy: List[Evidence] = Field(..., description="List of matched company policy chunks")
    regulations: List[Evidence] = Field(..., description="List of matched regulation chunks")
    confidence: float = Field(..., description="Deterministic retrieval confidence score")
    confidence_level: str = Field(..., description="Calculated confidence level (low, medium, high)")


class AuditResponse(BaseModel):
    """Structured response model for the POST /audit API endpoint."""

    question: str = Field(..., description="Original user question")
    planner: AuditPlannerResponse = Field(..., description="Planner node execution state details")
    retrieval: AuditRetrievalResponse = Field(..., description="Evidence retrieval node execution state details")
    compliance: Optional[ComplianceAnalysis] = Field(None, description="Compliance agent reasoning analysis and findings details")
    risk: Optional[RiskAnalysis] = Field(None, description="Risk agent analysis scoring and assessments")
    recommendations: Optional[RecommendationAnalysis] = Field(None, description="Actionable remediation recommendations and steps details")



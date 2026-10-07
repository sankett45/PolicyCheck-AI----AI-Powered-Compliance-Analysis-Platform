from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.models.evidence_models import Evidence


# Simplified models for LLM Structured Output tool-calling/JSON compatibility
class EvidenceCitation(BaseModel):
    """Pydantic model representing a simplified citation to verify against retrieved evidence."""

    filename: str = Field(..., description="The exact filename of the document referenced")
    chunk_index: int = Field(..., description="The chunk index of the text snippet referenced")


class ComplianceFindingLLM(BaseModel):
    """Structured Pydantic model for LLM generation of compliance findings."""

    control: str = Field(..., description="The control being evaluated")
    status: Literal["compliant", "partially_compliant", "non_compliant", "insufficient_evidence"] = Field(
        ...,
        description="The compliance status of this control finding"
    )
    company_requirement: str = Field(..., description="Description of the company policy requirements")
    regulatory_requirement: str = Field(..., description="Description of the regulatory standard requirements")
    reasoning: str = Field(..., description="Detailed reasoning explaining the compliance gap or status")
    evidence_citations: List[EvidenceCitation] = Field(..., description="Citations to retrieved document chunks backing this finding")


class ComplianceAnalysisLLM(BaseModel):
    """Structured Pydantic model for LLM generation of the compliance analysis report."""

    overall_status: Literal["compliant", "partially_compliant", "non_compliant", "insufficient_evidence"] = Field(
        ...,
        description="Overall compliance status determined from evidence comparison"
    )
    summary: str = Field(..., description="Analytical summary describing the compliance review findings")
    findings: List[ComplianceFindingLLM] = Field(..., description="Individual control evaluations")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0 based on evidence reliability")
    evidence_sufficient: bool = Field(..., description="Whether the evidence provided is sufficient to determine status")


# Final output models returned to the graph state and API responses
class ComplianceFinding(BaseModel):
    """Pydantic model representing a compliance evaluation finding for a specific control."""

    finding_id: Optional[str] = Field(None, description="Stable identifier for finding traceability")
    control: str = Field(..., description="The name of the control being evaluated (e.g. Multi-Factor Authentication)")
    status: Literal["compliant", "partially_compliant", "non_compliant", "insufficient_evidence"] = Field(
        ...,
        description="The compliance status of this finding"
    )
    company_requirement: str = Field(..., description="Description of the requirements under company policies")
    regulatory_requirement: str = Field(..., description="Description of the requirements under the regulation framework")
    reasoning: str = Field(..., description="Reasoning comparing policy and regulation evidence")
    evidence: List[Evidence] = Field(..., description="List of evidence objects cited to back this finding")



class ComplianceAnalysis(BaseModel):
    """Pydantic model representing the overall compliance reasoning assessment output."""

    overall_status: Literal["compliant", "partially_compliant", "non_compliant", "insufficient_evidence"] = Field(
        ...,
        description="Overall compliance status based on evidence evaluation"
    )
    summary: str = Field(..., description="Analytical summary describing the compliance comparison results")
    findings: List[ComplianceFinding] = Field(..., description="List of individual control findings")
    confidence: float = Field(..., description="Compliance reasoning confidence score (from 0.0 to 1.0)")
    evidence_sufficient: bool = Field(..., description="Flag indicating whether evidence is sufficient to make a determination")

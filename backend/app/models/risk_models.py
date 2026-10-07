from typing import List, Literal
from pydantic import BaseModel, Field
from app.models.evidence_models import Evidence

RiskLevel = Literal["low", "medium", "high", "critical"]


class RiskFactorAssessment(BaseModel):
    """Pydantic model representing LLM intermediate risk factor output."""

    finding_id: str = Field(..., description="The ID of the compliance finding being assessed")
    severity: int = Field(..., ge=1, le=5, description="Severity score from 1-5")
    likelihood: int = Field(..., ge=1, le=5, description="Likelihood score from 1-5")
    impact: int = Field(..., ge=1, le=5, description="Impact score from 1-5")
    rationale: str = Field(..., description="Analytical explanation of the risk factors identified")


class RiskAnalysisLLM(BaseModel):
    """Pydantic model representing structured LLM report containing multiple findings."""

    assessments: List[RiskFactorAssessment] = Field(..., description="List of individual finding risk factor assessments")
    summary: str = Field(default="", description="Summary overview of the risk landscape evaluated")



class RiskAssessment(BaseModel):
    """Pydantic model representing a final, validated risk assessment with calculation properties."""

    finding_id: str = Field(..., description="The ID of the corresponding compliance finding")
    control: str = Field(..., description="The control being assessed")
    risk_level: RiskLevel = Field(..., description="The calculated risk level based on the risk score")
    severity: int = Field(..., ge=1, le=5, description="Severity score from 1-5")
    likelihood: int = Field(..., ge=1, le=5, description="Likelihood score from 1-5")
    impact: int = Field(..., ge=1, le=5, description="Impact score from 1-5")
    risk_score: int = Field(..., ge=1, le=125, description="Deterministic risk score calculated (severity * likelihood * impact)")
    rationale: str = Field(..., description="Analytical explanation for the assigned risk levels")
    evidence: List[Evidence] = Field(..., description="Original evidence preserved from the compliance finding")


class RiskAnalysis(BaseModel):
    """Pydantic model representing the overall risk report output."""

    overall_risk_level: RiskLevel = Field(..., description="Calculated overall risk level")
    overall_risk_score: int = Field(..., ge=0, le=125, description="Calculated overall risk score (highest individual risk score or 0)")
    assessments: List[RiskAssessment] = Field(..., description="List of final risk assessments")
    summary: str = Field(..., description="Executive summary of the risk analysis")

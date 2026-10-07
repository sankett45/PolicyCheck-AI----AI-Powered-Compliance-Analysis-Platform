from typing import List, Literal
from pydantic import BaseModel, Field
from app.models.evidence_models import Evidence

RecommendationPriority = Literal["low", "medium", "high", "critical"]


class RecommendationLLM(BaseModel):
    """Pydantic model representing structured LLM recommendation output for a single finding."""

    finding_id: str = Field(..., description="The ID of the compliance finding being addressed")
    recommendation: str = Field(..., description="Actionable remediation recommendation details")
    rationale: str = Field(..., description="Reasoning explaining why this recommendation helps address the gap")
    implementation_steps: List[str] = Field(..., description="Step-by-step guidance to implement the recommendation")


class RecommendationAnalysisLLM(BaseModel):
    """Pydantic model representing structured top-level LLM recommendation report."""

    recommendations: List[RecommendationLLM] = Field(..., description="List of intermediate recommendations")
    summary: str = Field(default="Remediation recommendations report.", description="Summary overview of the remediation guidance")



class Recommendation(BaseModel):
    """Pydantic model representing a final, validated remediation recommendation with trace preservation."""

    finding_id: str = Field(..., description="The ID of the corresponding compliance finding")
    control: str = Field(..., description="The control being addressed")
    priority: RecommendationPriority = Field(..., description="The calculated priority level based on the risk level")
    recommendation: str = Field(..., description="Actionable remediation recommendation details")
    rationale: str = Field(..., description="Reasoning explaining why this recommendation helps address the gap")
    implementation_steps: List[str] = Field(..., description="Practical steps to implement the recommendation")
    evidence: List[Evidence] = Field(..., description="Original evidence preserved from the compliance finding")


class RecommendationAnalysis(BaseModel):
    """Pydantic model representing the overall recommendation analysis report."""

    recommendations: List[Recommendation] = Field(..., description="List of final recommendations")
    summary: str = Field(default="Remediation recommendations report.", description="Summary overview of the recommendation plan")
    overall_priority: RecommendationPriority = Field(..., description="Calculated overall priority (highest recommendation priority or low)")


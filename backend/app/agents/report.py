from typing import List, Any
from pydantic import BaseModel, Field
from app.services.llm import llm_service
from app.prompts.report_prompt import REPORT_SYSTEM_PROMPT
from app.utils.logger import logger


class ExecutiveSummaryOutput(BaseModel):
    """Structured Pydantic schema for the generated executive summary."""
    summary: str = Field(..., description="The synthesized executive summary text")


class ReportAgent:
    """Agent responsible for compiling and synthesizing report executive summaries from validated inputs."""

    def __init__(self) -> None:
        self._runnable = llm_service.with_structured_output(ExecutiveSummaryOutput)

    def generate_summary(
        self,
        question: str,
        audit_type: str,
        subject: str,
        regulation: str,
        overall_compliance_status: str,
        overall_risk_level: str,
        overall_risk_score: int,
        findings: List[Any],
        risk_assessments: List[Any],
        recommendations: List[Any],
        human_review_text: str
    ) -> str:
        """Construct prompt and request structured executive summary from ChatGroq."""
        logger.info("Generating report executive summary via ReportAgent")

        # Serialize findings detail
        findings_text = "\n".join([
            f"- Finding: {f.control} | Status: {f.status} | Rationale: {f.reasoning}"
            for f in findings
        ]) if findings else "No findings."

        # Serialize risk factor assessments
        risk_text = "\n".join([
            f"- Risk Control: {r.control} | Score: {r.risk_score} (Level: {r.risk_level}) | Rationale: {r.rationale}"
            for r in risk_assessments
        ]) if risk_assessments else "No risk assessments."

        # Serialize remediation guidance
        recs_text = "\n".join([
            f"- Suggestion for {rec.control}: {rec.recommendation} | Rationale: {rec.rationale} | Steps: {', '.join(rec.implementation_steps)}"
            for rec in recommendations
        ]) if recommendations else "No recommendations."

        # Compose context
        formatted_prompt = REPORT_SYSTEM_PROMPT.format(
            question=question,
            audit_type=audit_type,
            subject=subject,
            regulation=regulation,
            overall_compliance_status=overall_compliance_status,
            overall_risk_level=overall_risk_level,
            overall_risk_score=overall_risk_score,
            findings_text=findings_text,
            risk_text=risk_text,
            recommendations_text=recs_text,
            human_review_text=human_review_text
        )

        try:
            result = self._runnable.invoke(formatted_prompt)
            logger.info("Executive summary successfully generated.")
            return result.summary
        except Exception as e:
            logger.error(f"ReportAgent LLM execution failed: {e}", exc_info=True)
            # Safe default fallback summary mapping verified states
            return (
                f"Executive Summary: Audit evaluating compliance for '{subject}' under regulation '{regulation}'. "
                f"The overall compliance assessment status is '{overall_compliance_status}' with a calculated overall "
                f"risk level of '{overall_risk_level}' (score: {overall_risk_score}). Please refer to findings list "
                f"for specific gap logs."
            )

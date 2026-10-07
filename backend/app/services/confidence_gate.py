from typing import List
from app.config import settings
from app.models.compliance_models import ComplianceAnalysis
from app.models.risk_models import RiskAnalysis
from app.models.review_models import ConfidenceGateResult, ReviewReason
from app.utils.logger import logger


class ConfidenceGateService:
    """Service responsible for determining whether an audit workflow requires human-in-the-loop review."""

    def evaluate_gate(
        self,
        retrieval_confidence: float,
        compliance_analysis: ComplianceAnalysis,
        compliance_confidence: float,
        risk_analysis: RiskAnalysis
    ) -> ConfidenceGateResult:
        """Deterministically assess confidence metrics and findings to decide if review is required.

        Args:
            retrieval_confidence (float): Signal score representing quality of evidence retrieval.
            compliance_analysis (ComplianceAnalysis): Calculated compliance findings and status.
            compliance_confidence (float): Calculated compliance reasoning confidence.
            risk_analysis (RiskAnalysis): Assessed risk level and scores.

        Returns:
            ConfidenceGateResult: Evaluated review flags and reasons list.
        """
        logger.info("Evaluating deterministic Confidence Gate rules...")
        reasons: List[ReviewReason] = []

        # RULE 1: Retrieval confidence check
        if retrieval_confidence < settings.RETRIEVAL_CONFIDENCE_REVIEW_THRESHOLD:
            logger.info(f"Gate Rule 1 Triggered: retrieval_confidence ({retrieval_confidence}) < threshold ({settings.RETRIEVAL_CONFIDENCE_REVIEW_THRESHOLD})")
            reasons.append("low_retrieval_confidence")

        # RULE 2: Insufficient evidence status check
        if compliance_analysis.overall_status == "insufficient_evidence":
            logger.info("Gate Rule 2 Triggered: compliance overall_status is insufficient_evidence")
            reasons.append("insufficient_evidence")

        # RULE 3: Compliance confidence check
        if compliance_confidence < settings.COMPLIANCE_CONFIDENCE_REVIEW_THRESHOLD:
            logger.info(f"Gate Rule 3 Triggered: compliance_confidence ({compliance_confidence}) < threshold ({settings.COMPLIANCE_CONFIDENCE_REVIEW_THRESHOLD})")
            reasons.append("low_compliance_confidence")

        # RULE 4: Critical risk check
        if settings.CRITICAL_RISK_REQUIRES_REVIEW and risk_analysis.overall_risk_level == "critical":
            logger.info("Gate Rule 4 Triggered: overall risk level is critical")
            reasons.append("high_risk")

        # RULE 5: Evidence unresolved conflicts check (reasoning strings containing conflict indicators)
        has_conflict = False
        for finding in compliance_analysis.findings:
            if finding.status in ("partially_compliant", "non_compliant"):
                reasoning_lower = finding.reasoning.lower()
                if "conflict" in reasoning_lower or "contradict" in reasoning_lower or "clash" in reasoning_lower:
                    has_conflict = True
                    break


        if has_conflict:
            logger.info("Gate Rule 5 Triggered: compliance evidence contains conflicts or contradictions")
            reasons.append("policy_or_regulation_conflict")

        review_required = len(reasons) > 0
        logger.info(f"Confidence Gate evaluation complete: review_required={review_required}, reasons={reasons}")

        return ConfidenceGateResult(
            review_required=review_required,
            reasons=reasons,
            retrieval_confidence=retrieval_confidence,
            compliance_confidence=compliance_confidence,
            risk_level=risk_analysis.overall_risk_level,
            risk_score=risk_analysis.overall_risk_score
        )


# Singleton gate service instance
confidence_gate_service = ConfidenceGateService()

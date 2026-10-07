from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.graph.state import AuditState

from app.agents.planner import PlannerAgent
from app.agents.compliance import ComplianceAgent
from app.agents.risk import RiskAgent
from app.agents.recommendation import RecommendationAgent
from app.models.risk_models import RiskAnalysis, RiskAssessment
from app.models.risk_scoring import calculate_risk_score, map_score_to_level
from app.models.recommendation_models import RecommendationAnalysis, Recommendation
from app.models.recommendation_scoring import risk_level_to_priority
from app.services.retriever import retrieval_service
from app.services.confidence_gate import confidence_gate_service
from app.utils.logger import logger

# Instantiate Agents
planner_agent = PlannerAgent()
compliance_agent = ComplianceAgent()
risk_agent = RiskAgent()
recommendation_agent = RecommendationAgent()


def planner_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the planning and intent parsing stage.

    Uses PlannerAgent to parse user compliance query metadata.
    """
    logger.info("Planner node started")
    question = state.get("question", "")

    if not question.strip():
        err_msg = "Question cannot be empty."
        logger.error(f"Planner node error: {err_msg}")
        return {"errors": state.get("errors", []) + [err_msg]}

    try:
        planner_output = planner_agent.plan(question)
        logger.info("Planner node completed successfully")
        return {
            "audit_type": planner_output.audit_type,
            "subject": planner_output.subject,
            "regulation": planner_output.regulation,
            "intent": planner_output.intent,
        }
    except Exception as e:
        err_msg = f"Planner failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def retrieval_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the evidence retrieval stage.

    Directly queries the existing RetrievalService for policies and regulations.
    """
    logger.info("Retrieval node started")
    question = state.get("question", "")

    if not question.strip():
        err_msg = "Question cannot be empty for retrieval."
        logger.error(f"Retrieval node error: {err_msg}")
        return {"errors": state.get("errors", []) + [err_msg]}

    try:
        # Directly call the internal RetrievalService (never an HTTP call)
        retrieval_result = retrieval_service.retrieve(question=question)

        logger.info("Retrieval node completed successfully")
        return {
            "retrieval_result": retrieval_result,
            "confidence": retrieval_result.confidence,
            "confidence_level": retrieval_result.confidence_level,
            "retrieval_confidence": retrieval_result.confidence,  # Store separately in state (Phase 4B)
        }
    except Exception as e:
        err_msg = f"Retrieval failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def compliance_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the compliance analysis stage.

    Uses ComplianceAgent to compare policy against regulation and evaluate compliance.
    """
    logger.info("Compliance analysis node started")

    retrieval_result = state.get("retrieval_result")
    if not retrieval_result:
        err_msg = "Critical error in compliance node: retrieval_result is missing from graph state."
        logger.error(err_msg)
        raise ValueError(err_msg)

    try:
        compliance_analysis = compliance_agent.analyze(retrieval_result)
        logger.info("Compliance analysis node completed successfully")
        return {
            "compliance_analysis": compliance_analysis,
            "compliance_confidence": compliance_analysis.confidence
        }
    except Exception as e:
        err_msg = f"Compliance analysis failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def risk_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the risk assessment stage.

    Uses RiskAgent to evaluate risk severity, likelihood, and impact for compliance findings,
    then calculates deterministic risk scores and levels.
    """
    logger.info("Risk analysis node started")

    compliance_analysis = state.get("compliance_analysis")
    if not compliance_analysis:
        err_msg = "Critical error in risk node: compliance_analysis is missing from graph state."
        logger.error(err_msg)
        raise ValueError(err_msg)

    # Handle insufficient compliance evidence (Requirement 9)
    if compliance_analysis.overall_status == "insufficient_evidence":
        logger.info("Compliance status is insufficient_evidence. Bypassing normal risk assessment.")
        insufficient_risk = RiskAnalysis(
            overall_risk_level="low",
            overall_risk_score=0,
            assessments=[],
            summary="Risk assessment skipped: compliance evidence was insufficient to perform assessment."
        )
        return {"risk_analysis": insufficient_risk}

    try:
        # Call RiskAgent to generate intermediate factor recommendations
        llm_result = risk_agent.assess(compliance_analysis)
        logger.info(f"Intermediate risk factors generated. Validating and calculating scores...")

        assessments = []
        for item in llm_result.assessments:
            # Safe finding_id suffix extraction (Requirement 7)
            finding_idx = None
            if item.finding_id.startswith("finding_"):
                try:
                    finding_idx = int(item.finding_id.split("_")[1])
                except (ValueError, IndexError):
                    pass

            if finding_idx is not None and 0 <= finding_idx < len(compliance_analysis.findings):
                original_finding = compliance_analysis.findings[finding_idx]
            else:
                logger.warning(f"Risk assessment generated invalid finding_id: '{item.finding_id}'. Skipping.")
                continue

            # Validate constraints (Requirement 15)
            severity = max(1, min(5, item.severity))
            likelihood = max(1, min(5, item.likelihood))
            impact = max(1, min(5, item.impact))

            # Deterministic scoring (Requirement 2 & 3)
            risk_score = calculate_risk_score(severity, likelihood, impact)
            risk_level = map_score_to_level(risk_score)

            # Build validated assessment preserving original evidence
            assessment = RiskAssessment(
                finding_id=item.finding_id,
                control=original_finding.control,
                risk_level=risk_level,
                severity=severity,
                likelihood=likelihood,
                impact=impact,
                risk_score=risk_score,
                rationale=item.rationale,
                evidence=original_finding.evidence
            )
            assessments.append(assessment)

            logger.info(
                f"Finding '{original_finding.control}' assessed: score={risk_score}, level={risk_level}"
            )

        # Calculate overall risk based on highest individual risk score (Requirement 10)
        overall_risk_score = max([a.risk_score for a in assessments]) if assessments else 0
        overall_risk_level = map_score_to_level(overall_risk_score)

        final_risk_analysis = RiskAnalysis(
            overall_risk_level=overall_risk_level,
            overall_risk_score=overall_risk_score,
            assessments=assessments,
            summary=llm_result.summary
        )

        logger.info(
            f"Risk analysis completed: overall_score={overall_risk_score}, overall_level={overall_risk_level}"
        )
        return {"risk_analysis": final_risk_analysis}

    except Exception as e:
        err_msg = f"Risk analysis failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def recommendation_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the remediation recommendations stage.

    Uses RecommendationAgent to generate actionable guidance, mapping priorities and
    evidence from upstream compliance and risk analysis.
    """
    logger.info("Recommendation analysis node started")

    compliance_analysis = state.get("compliance_analysis")
    risk_analysis = state.get("risk_analysis")

    if not compliance_analysis:
        err_msg = "Critical error in recommendation node: compliance_analysis is missing from graph state."
        logger.error(err_msg)
        raise ValueError(err_msg)

    if not risk_analysis:
        err_msg = "Critical error in recommendation node: risk_analysis is missing from graph state."
        logger.error(err_msg)
        raise ValueError(err_msg)

    # Handle insufficient compliance evidence (Requirement 9)
    if compliance_analysis.overall_status == "insufficient_evidence":
        logger.info("Compliance status is insufficient_evidence. Skipping recommendation generation.")
        insufficient_recs = RecommendationAnalysis(
            recommendations=[],
            summary="Remediation recommendations skipped: compliance evidence was insufficient to perform assessment.",
            overall_priority="low"
        )
        return {"recommendation_analysis": insufficient_recs}

    # Handle fully compliant case with no residual risks (Requirement 8)
    all_compliant = all(f.status == "compliant" for f in compliance_analysis.findings)
    if all_compliant and len(risk_analysis.assessments) == 0:
        logger.info("All findings are compliant. Returning empty recommendation list.")
        compliant_recs = RecommendationAnalysis(
            recommendations=[],
            summary="No remediation actions are currently required because all evaluated controls are compliant.",
            overall_priority="low"
        )
        return {"recommendation_analysis": compliant_recs}

    try:
        # Call RecommendationAgent to generate textual content
        llm_result = recommendation_agent.recommend(compliance_analysis, risk_analysis)
        logger.info(f"Intermediate recommendations generated. Mapping priorities and verifying evidence...")

        # Build risk lookup map for priority calculation (Requirement 6)
        risk_map = {a.finding_id: a.risk_level for a in risk_analysis.assessments}

        recommendations = []
        priority_ranks = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        highest_rank = -1
        overall_priority = "low"

        for item in llm_result.recommendations:
            # Safe finding_id suffix extraction (Requirement 7)
            finding_idx = None
            if item.finding_id.startswith("finding_"):
                try:
                    finding_idx = int(item.finding_id.split("_")[1])
                except (ValueError, IndexError):
                    pass

            if finding_idx is not None and 0 <= finding_idx < len(compliance_analysis.findings):
                original_finding = compliance_analysis.findings[finding_idx]
            else:
                logger.warning(
                    f"Recommendation generated invalid finding_id: '{item.finding_id}'. Skipping."
                )
                continue

            # Deterministic priority mapping (Requirement 5 & 6)
            risk_level = risk_map.get(item.finding_id, "low")
            priority = risk_level_to_priority(risk_level)

            # Preserve evidence provenance (Requirement 10)
            evidence_preserved = original_finding.evidence

            # Build final recommendation object
            rec = Recommendation(
                finding_id=item.finding_id,
                control=original_finding.control,
                priority=priority,
                recommendation=item.recommendation,
                rationale=item.rationale,
                implementation_steps=item.implementation_steps,
                evidence=evidence_preserved
            )
            recommendations.append(rec)

            # Overall priority calculation based on highest individual rank
            rank = priority_ranks.get(priority, 0)
            if rank > highest_rank:
                highest_rank = rank
                overall_priority = priority

            logger.info(
                f"Recommendation generated for control '{original_finding.control}': priority={priority}"
            )

        final_rec_analysis = RecommendationAnalysis(
            recommendations=recommendations,
            summary=llm_result.summary,
            overall_priority=overall_priority
        )

        logger.info(
            f"Recommendation analysis completed: overall_priority={overall_priority}, count={len(recommendations)}"
        )
        return {"recommendation_analysis": final_rec_analysis}

    except Exception as e:
        err_msg = f"Recommendation analysis failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def confidence_gate_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the deterministic confidence gate stage.

    Reads retrieval and compliance metrics to evaluate if a human-in-the-loop review
    is required.
    """
    logger.info("Confidence gate node started")

    retrieval_result = state.get("retrieval_result")
    compliance_analysis = state.get("compliance_analysis")
    risk_analysis = state.get("risk_analysis")

    if not compliance_analysis:
        err_msg = "Critical error in confidence gate node: compliance_analysis is missing."
        logger.error(err_msg)
        raise ValueError(err_msg)

    if not risk_analysis:
        err_msg = "Critical error in confidence gate node: risk_analysis is missing."
        logger.error(err_msg)
        raise ValueError(err_msg)

    # Retrieval confidence
    retrieval_confidence = state.get("retrieval_confidence")
    if retrieval_confidence is None:
        retrieval_confidence = retrieval_result.confidence if retrieval_result else 0.0

    # Compliance confidence
    compliance_confidence = state.get("compliance_confidence")
    if compliance_confidence is None:
        compliance_confidence = compliance_analysis.confidence if compliance_analysis else 0.0

    # Run deterministic gate logic
    gate_result = confidence_gate_service.evaluate_gate(
        retrieval_confidence=retrieval_confidence,
        compliance_analysis=compliance_analysis,
        compliance_confidence=compliance_confidence,
        risk_analysis=risk_analysis
    )

    logger.info(
        f"Confidence gate result: review_required={gate_result.review_required}, "
        f"reasons={gate_result.reasons}"
    )

    return {
        "review_required": gate_result.review_required,
        "review_reasons": gate_result.reasons,
        "review_status": "pending" if gate_result.review_required else "not_required"
    }


def human_review_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the human-in-the-loop review stage.

    Applies the reviewer's decision to update the state status once the graph is resumed.
    """
    logger.info("Human review node started")

    decision = state.get("review_decision")
    comment = state.get("reviewer_comment")

    logger.info(f"Human review node received decision: {decision}, comment: {comment}")

    if decision == "approve":
        status = "approved"
    elif decision == "reject":
        status = "rejected"
    elif decision == "request_more_evidence":
        status = "needs_more_evidence"
    else:
        status = "pending"

    return {
        "review_status": status
    }


def report_node(state: AuditState, config: RunnableConfig) -> Dict[str, Any]:
    """LangGraph node representing the final synthesis and persistence stage.

    Retrieves all validated agent outputs, verifies HITL review state decisions,
    triggers executive summary generation, and persists versioned reports to DB.
    """
    logger.info("Report node started")

    # Extract thread session configuration
    thread_id = config["configurable"].get("thread_id")
    if not thread_id:
        import uuid
        thread_id = str(uuid.uuid4())
        logger.warning(f"No thread_id configured. Generated default: {thread_id}")

    from app.database.connection import SessionLocal
    from app.services.report_generator import report_generator_service

    with SessionLocal() as db:
        try:
            # Assembly & save database record
            report = report_generator_service.generate_report(state, thread_id, db)

            # Dump report representation to persist in Graph State
            report_dict = report.model_dump()

            # Ensure datetime properties are serialized to ISO format strings
            if report_dict.get("generated_at"):
                report_dict["generated_at"] = report.generated_at.isoformat()
            if report_dict.get("human_review") and report_dict["human_review"].get("timestamp"):
                report_dict["human_review"]["timestamp"] = report.human_review.timestamp.isoformat()

            return {
                "final_report": report_dict,
                "review_status": report.status.value
            }
        except Exception as e:
            logger.error(f"Report node execution failed: {e}", exc_info=True)
            raise ValueError(f"Report node failure: {str(e)}")





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schema import HumanReview
from app.models.review_models import HumanReviewRequest, HumanReviewDecision
from app.graph.workflow import audit_graph
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/review", tags=["Human Review"])


@router.get("/{review_id}", response_model=HumanReviewRequest)
def get_human_review_request(review_id: str, db: Session = Depends(get_db)):
    """Retrieve details of a specific human-in-the-loop review request."""
    logger.info(f"Retrieving human review request: {review_id}")

    # Query persistent database record
    review_record = db.query(HumanReview).filter(HumanReview.review_id == review_id).first()
    if not review_record:
        logger.warning(f"Human review request not found: {review_id}")
        raise HTTPException(status_code=404, detail="Human review request not found.")

    # Retrieve matching thread state checkpoints from LangGraph
    config = {"configurable": {"thread_id": review_record.thread_id}}
    state = audit_graph.get_state(config)
    if not state or not state.values:
        logger.error(f"LangGraph state checkpoint not found for thread: {review_record.thread_id}")
        raise HTTPException(status_code=404, detail="Graph state checkpoint not found for this review request.")

    vals = state.values
    findings = vals.get("compliance_analysis").findings if vals.get("compliance_analysis") else []
    recommendations = vals.get("recommendation_analysis").recommendations if vals.get("recommendation_analysis") else []
    compliance_summary = vals.get("compliance_analysis").summary if vals.get("compliance_analysis") else ""

    return HumanReviewRequest(
        review_id=review_record.review_id,
        question=review_record.question,
        review_status=review_record.status,
        reasons=review_record.reasons.split(",") if review_record.reasons else [],
        retrieval_confidence=review_record.retrieval_confidence or 0.0,
        compliance_confidence=review_record.compliance_confidence or 0.0,
        risk_level=review_record.risk_level or "low",
        risk_score=review_record.risk_score or 0,
        compliance_summary=compliance_summary,
        findings=findings,
        recommendations=recommendations,
        created_at=review_record.created_at
    )


@router.post("/{review_id}/decision")
def post_human_review_decision(
    review_id: str,
    decision_data: HumanReviewDecision,
    db: Session = Depends(get_db)
):
    """Submit a reviewer decision (approve, reject, request_more_evidence) and resume graph."""
    logger.info(f"Received review decision for request {review_id}: {decision_data.decision}")

    if decision_data.review_id != review_id:
        raise HTTPException(status_code=400, detail="Review ID in path does not match request body.")

    # Query persistent record
    review_record = db.query(HumanReview).filter(HumanReview.review_id == review_id).first()
    if not review_record:
        logger.warning(f"Human review request not found: {review_id}")
        raise HTTPException(status_code=404, detail="Human review request not found.")

    # Validate pending status (Requirement 13)
    if review_record.status != "pending":
        logger.warning(f"Cannot update resolved review request: {review_id} (Status: {review_record.status})")
        raise HTTPException(status_code=400, detail="Review request is already completed and cannot be modified.")

    # Map decision to status
    status_mapping = {
        "approve": "approved",
        "reject": "rejected",
        "request_more_evidence": "needs_more_evidence"
    }
    mapped_status = status_mapping.get(decision_data.decision)

    # 1. Update graph state configuration
    config = {"configurable": {"thread_id": review_record.thread_id}}
    try:
        audit_graph.update_state(config, {
            "review_decision": decision_data.decision,
            "reviewer_comment": decision_data.reviewer_comment,
            "review_status": mapped_status
        }, as_node="human_review")
    except Exception as e:
        logger.error(f"Failed to update LangGraph state for review {review_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update graph state checkpoint: {e}")

    # 2. Resume graph execution by invoking with None input (Requirement 10 & 14)
    try:
        audit_graph.invoke(None, config)
    except Exception as e:
        logger.error(f"Failed to resume LangGraph thread {review_record.thread_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to resume workflow: {e}")

    # 3. Update persistent database metadata and commit audit trail (Requirement 17 & 21)
    review_record.status = mapped_status
    review_record.decision = decision_data.decision
    review_record.reviewer_comment = decision_data.reviewer_comment
    review_record.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"Review {review_id} successfully updated to status: {mapped_status}")
    return {
        "status": mapped_status,
        "message": f"Human review decision '{decision_data.decision}' processed and graph state updated."
    }

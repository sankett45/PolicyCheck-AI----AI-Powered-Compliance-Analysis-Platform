from typing import Dict, Any, Optional
from app.graph.workflow import audit_graph
from app.utils.logger import logger


class AuditGraphService:
    """Service to execute the compiled LangGraph compliance audit workflow."""

    def run_audit(self, question: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the compliance audit workflow for a given question.

        Args:
            question (str): The compliance question.
            thread_id (str, optional): Unique thread/session identifier for state tracking.

        Returns:
            Dict[str, Any]: The final compiled state of the graph.
        """
        logger.info(f"Audit workflow started for question: '{question[:60]}...' on thread: {thread_id}")

        # Validate question
        if not question.strip():
            logger.error("Audit workflow failed validation: empty question.")
            raise ValueError("Question cannot be empty or whitespace.")

        import uuid
        if thread_id is None:
            thread_id = str(uuid.uuid4())


        # Initialize AuditState
        initial_state = {
            "question": question,
            "audit_type": None,
            "subject": None,
            "regulation": None,
            "intent": None,
            "retrieval_result": None,
            "confidence": None,
            "confidence_level": None,
            "errors": [],
            "compliance_analysis": None,
            "retrieval_confidence": None,
            "compliance_confidence": None,
            "compliance_findings": None,
            "risk_assessment": None,
            "recommendations": None,
            "review_status": None,
            "final_report": None
        }

        try:
            # Invoke LangGraph workflow with thread identifier
            config = {"configurable": {"thread_id": thread_id}}
            final_state = audit_graph.invoke(initial_state, config)
            logger.info("Audit workflow execution completed or interrupted.")
            return final_state
        except Exception as e:
            logger.error(f"Audit workflow execution failed on thread {thread_id}: {e}", exc_info=True)
            raise e



# Create singleton service instance
audit_graph_service = AuditGraphService()

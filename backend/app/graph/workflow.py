from langgraph.graph import StateGraph, START, END
from app.graph.state import AuditState
from app.graph.nodes import (
    planner_node,
    retrieval_node,
    compliance_node,
    risk_node,
    recommendation_node,
    confidence_gate_node,
    human_review_node,
    report_node
)


# Initialize StateGraph with the custom AuditState TypedDict
workflow = StateGraph(AuditState)

# Register nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieval_node)
workflow.add_node("compliance", compliance_node)
workflow.add_node("risk", risk_node)
workflow.add_node("recommendation", recommendation_node)
workflow.add_node("confidence_gate", confidence_gate_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("report", report_node)

# Configure sequential execution edges
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "retriever")
workflow.add_edge("retriever", "compliance")
workflow.add_edge("compliance", "risk")
workflow.add_edge("risk", "recommendation")
workflow.add_edge("recommendation", "confidence_gate")


# Configure conditional edge routing after confidence gate (Requirement 10 & 23)
def route_after_gate(state: AuditState) -> str:
    """Route to human review if gate reports review required, otherwise to report generation."""
    if state.get("review_required"):
        return "human_review"
    return "report"


workflow.add_conditional_edges(
    "confidence_gate",
    route_after_gate,
    {
        "human_review": "human_review",
        "report": "report"
    }
)


# Configure conditional edge routing after human review (Requirement 10 & 23)
def route_after_review(state: AuditState) -> str:
    """Route to report generation if approved, otherwise terminate workflow immediately."""
    if state.get("review_status") == "approved":
        return "report"
    return END


workflow.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "report": "report",
        END: END
    }
)

# Route report node completion to END
workflow.add_edge("report", END)


# Set up PostgreSQL checkpointer with InMemory fallback for test suites
import sys
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from app.config import settings

if "pytest" in sys.modules or not settings.DATABASE_URL:
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
else:
    try:
        checkpoint_pool = ConnectionPool(
            conninfo=settings.DATABASE_URL,
            min_size=1,
            max_size=10,
            kwargs={"autocommit": True}
        )
        checkpointer = PostgresSaver(checkpoint_pool)
    except Exception as e:
        from langgraph.checkpoint.memory import InMemorySaver
        checkpointer = InMemorySaver()

# Compile workflow graph with checkpointer and interrupt before human review
audit_graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)





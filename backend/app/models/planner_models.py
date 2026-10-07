from typing import Optional
from pydantic import BaseModel, Field


class PlannerOutput(BaseModel):
    """Structured Pydantic model representing the output of the query planner."""

    audit_type: str = Field(
        ...,
        description="The type of the audit (e.g. policy_compliance, regulatory_compliance, sop_audit)."
    )
    subject: str = Field(
        ...,
        description="The specific subject or domain being audited (e.g. password_policy, mfa_policy, backup_policy)."
    )
    regulation: Optional[str] = Field(
        None,
        description="The specific regulation or framework mentioned explicitly, or null if not explicitly named."
    )
    intent: str = Field(
        ...,
        description="The core audit intent describing the evaluation request."
    )

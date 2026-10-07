import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON

from sqlalchemy.dialects.postgresql import UUID

from app.database.connection import Base



class Document(Base):
    """SQLAlchemy model representing document ingestion metadata and statuses."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # company_policy, regulation, contract, sop
    document_version = Column(String, nullable=False, default="1.0.0")
    file_path = Column(String, nullable=False)
    chunk_count = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="processing")  # processing, indexed, failed


class HumanReview(Base):
    """SQLAlchemy model representing human-in-the-loop review requests and decisions."""

    __tablename__ = "human_reviews"

    review_id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=False)
    question = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, approved, rejected, needs_more_evidence
    reasons = Column(String, nullable=False)  # comma-separated string list
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewer_comment = Column(String, nullable=True)
    decision = Column(String, nullable=True)

    # Persistent audit trail details
    retrieval_confidence = Column(Float, nullable=True)
    compliance_confidence = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_score = Column(Integer, nullable=True)


class AuditReport(Base):
    """SQLAlchemy model representing final, versioned compliance audit reports."""

    __tablename__ = "audit_reports"

    report_id = Column(String, primary_key=True)
    audit_id = Column(String, nullable=False, index=True)
    question = Column(String, nullable=False)
    executive_summary = Column(String, nullable=False, default="")
    audit_type = Column(String, nullable=False, default="compliance_audit")
    subject = Column(String, nullable=False, default="general")
    regulation = Column(String, nullable=False, default="general")
    status = Column(String, nullable=False)  # draft, final, rejected, pending_review


    overall_compliance_status = Column(String, nullable=False)
    overall_risk_level = Column(String, nullable=False)
    overall_risk_score = Column(Integer, nullable=False)
    report_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    human_review_status = Column(String, nullable=True)

    # JSON/JSONB serialized columns
    findings = Column(JSON, nullable=False)
    risk_assessments = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    evidence_summary = Column(JSON, nullable=False)
    human_review = Column(JSON, nullable=True)



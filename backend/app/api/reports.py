from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schema import AuditReport as DBAuditReport
from app.models.report_models import AuditReport, Evidence
from app.utils.logger import logger
from typing import List

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{report_id}", response_model=AuditReport)
def get_audit_report(report_id: str, db: Session = Depends(get_db)):
    """Retrieve details of a persistent finalized or draft audit report."""
    logger.info(f"Retrieving audit report: {report_id}")

    db_report = db.query(DBAuditReport).filter(DBAuditReport.report_id == report_id).first()
    if not db_report:
        logger.warning(f"Audit report not found: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit report not found."
        )

    return db_report


@router.get("/{report_id}/evidence", response_model=List[Evidence])
def get_report_evidence(report_id: str, db: Session = Depends(get_db)):
    """Retrieve the set of evidence sources referenced in the audit report findings."""
    logger.info(f"Retrieving evidence references for report: {report_id}")

    db_report = db.query(DBAuditReport).filter(DBAuditReport.report_id == report_id).first()
    if not db_report:
        logger.warning(f"Audit report not found for evidence extraction: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit report not found."
        )

    # Return evidence summary directly from DB JSON
    return db_report.evidence_summary


@router.get("/{report_id}/download")
def download_report(report_id: str, db: Session = Depends(get_db)):
    """Download the synthesized audit report as a structured Markdown document."""
    logger.info(f"Downloading report: {report_id}")

    db_report = db.query(DBAuditReport).filter(DBAuditReport.report_id == report_id).first()
    if not db_report:
        logger.warning(f"Audit report not found for download: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit report not found."
        )

    # Assemble Markdown report text deterministically
    md_lines = [
        f"# Audit Report: {db_report.subject.replace('_', ' ').title()}",
        f"**Question:** {db_report.question}",
        "",
        "## 1. Audit Metadata",
        f"- **Report ID:** {db_report.report_id}",
        f"- **Audit ID:** {db_report.audit_id}",
        f"- **Report Version:** {db_report.report_version}",
        f"- **Status:** {db_report.status.upper()}",
        f"- **Classification:** {db_report.audit_type}",
        f"- **Framework/Regulation:** {db_report.regulation}",
        f"- **Generated At:** {db_report.created_at.isoformat()}",
        "",
        "## 2. Executive Summary",
        db_report.executive_summary,
        "",
        "## 3. Overall Audit Scorecard",
        f"- **Compliance Status:** {db_report.overall_compliance_status.upper()}",
        f"- **Risk Level:** {db_report.overall_risk_level.upper()}",
        f"- **Risk Score:** {db_report.overall_risk_score} / 125",
        "",
        "## 4. Compliance Findings",
    ]

    # Findings details
    findings_list = db_report.findings or []
    if not findings_list:
        md_lines.append("No findings recorded.")
    else:
        for idx, f in enumerate(findings_list):
            fid = f.get("finding_id", f"finding_{idx}")
            md_lines.extend([
                f"### Finding: {f.get('control')} ({fid})",
                f"- **Status:** {f.get('status').upper()}",
                f"- **Company Requirement:** {f.get('company_requirement')}",
                f"- **Regulatory Requirement:** {f.get('regulatory_requirement')}",
                f"- **Reasoning:** {f.get('reasoning')}",
                ""
            ])

    # Risk assessments details
    md_lines.append("## 5. Risk Assessment details")
    risks_list = db_report.risk_assessments or []
    if not risks_list:
        md_lines.append("No material risks assessed.")
    else:
        for r in risks_list:
            md_lines.extend([
                f"### Risk Assessment for {r.get('finding_id')}",
                f"- **Control Evaluated:** {r.get('control')}",
                f"- **Risk Level:** {r.get('risk_level').upper()}",
                f"- **Metrics:** Severity={r.get('severity')}, Likelihood={r.get('likelihood')}, Impact={r.get('impact')}",
                f"- **Calculated Risk Score:** {r.get('risk_score')}",
                f"- **Rationale:** {r.get('rationale')}",
                ""
            ])

    # Recommendations details
    md_lines.append("## 6. Actionable Remediation Guidance")
    recs_list = db_report.recommendations or []
    if not recs_list:
        md_lines.append("No remediation actions are required.")
    else:
        for rec in recs_list:
            steps_text = "\n".join([f"  {i+1}. {step}" for i, step in enumerate(rec.get("implementation_steps", []))])
            md_lines.extend([
                f"### Recommendation for {rec.get('finding_id')}",
                f"- **Control Gap:** {rec.get('control')}",
                f"- **Priority:** {rec.get('priority').upper()}",
                f"- **Remediation Action:** {rec.get('recommendation')}",
                f"- **Rationale:** {rec.get('rationale')}",
                "- **Implementation Steps:**",
                steps_text,
                ""
            ])

    # Human review details if applicable
    if db_report.human_review:
        hr = db_report.human_review
        md_lines.extend([
            "## 7. Human-in-the-Loop Review Trail",
            f"- **Outcome Status:** {hr.get('review_status').upper()}",
            f"- **Decision:** {hr.get('reviewer_decision')}",
            f"- **Comment:** {hr.get('reviewer_comment')}",
            f"- **Timestamp:** {hr.get('timestamp')}",
            ""
        ])

    # Evidence sources provenance details
    md_lines.append("## 8. Verified Traceable Evidence Sources")
    ev_list = db_report.evidence_summary or []
    if not ev_list:
        md_lines.append("No evidence documents referenced.")
    else:
        for idx, ev in enumerate(ev_list):
            md_lines.extend([
                f"### Source {idx + 1}: '{ev.get('filename')}' (v{ev.get('document_version')})",
                f"- **Type:** {ev.get('document_type')}",
                f"- **Page Index:** {ev.get('page_number')} | Chunk: {ev.get('chunk_index')}",
                f"- **Source Path:** {ev.get('source')}",
                f"- **Similarity Metric:** {ev.get('similarity_score')}",
                f"- **Snippet:** *\"{ev.get('text')}\"*",
                ""
            ])

    # Join lines to compose Markdown string
    md_report = "\n".join(md_lines)

    # Return as downloadable text response
    headers = {
        "Content-Disposition": f"attachment; filename=audit_report_{report_id}.md"
    }
    return Response(content=md_report, media_type="text/markdown", headers=headers)

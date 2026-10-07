from typing import Dict, Any, List
import uuid
import json

from app.models.evidence_models import RetrievalResult, Evidence
from app.models.compliance_models import ComplianceAnalysis, ComplianceFinding, ComplianceAnalysisLLM, ComplianceFindingLLM
from app.services.llm import llm_service
from app.prompts.compliance_prompt import SYSTEM_PROMPT
from app.utils.logger import logger
from langchain_core.prompts import ChatPromptTemplate


class ComplianceAgent:
    """Agent responsible for performing compliance analysis over retrieved evidence."""

    def __init__(self) -> None:
        """Initialize the ComplianceAgent by binding the LLM with structured output."""
        logger.info("Initializing ComplianceAgent with structured output...")
        try:
            # Bind to the simplified LLM schema for optimal JSON mode execution
            self._structured_llm = llm_service.with_structured_output(
                ComplianceAnalysisLLM,
                method="json_mode"
            )
            self._prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", (
                    "Audit Question: {question}\n\n"
                    "=== COMPANY POLICY EVIDENCE ===\n{company_policy}\n\n"
                    "=== REGULATION EVIDENCE ===\n{regulations}\n"
                ))
            ])
            self._chain = self._prompt_template | self._structured_llm
        except Exception as e:
            logger.error(f"Failed to initialize ComplianceAgent chain: {e}", exc_info=True)
            raise e

    def analyze(self, retrieval_result: RetrievalResult) -> ComplianceAnalysis:
        """Analyze RetrievalResult and compare policy evidence against regulations.

        Args:
            retrieval_result (RetrievalResult): Retrieved policy and regulation evidence.

        Returns:
            ComplianceAnalysis: Validated compliance reasoning and findings.
        """
        logger.info("Compliance analysis started")

        company_policy_list = retrieval_result.company_policy
        regulations_list = retrieval_result.regulations

        logger.info(f"Evidence count: total={len(company_policy_list) + len(regulations_list)}")
        logger.info(f"Company evidence count: {len(company_policy_list)}")
        logger.info(f"Regulation evidence count: {len(regulations_list)}")

        # Check for missing evidence upfront (Requirement 12)
        if not company_policy_list or not regulations_list:
            logger.info("Evidence sufficiency: insufficient. Either company policy or regulation evidence is missing.")
            return ComplianceAnalysis(
                overall_status="insufficient_evidence",
                summary="Relevant company policy or regulation evidence was not available to determine compliance.",
                findings=[],
                confidence=0.20,
                evidence_sufficient=False
            )

        # Build context strings for prompt
        company_policy_str = "\n\n".join(
            f"Document: {ev.filename} (v{ev.document_version}), Page {ev.page_number}, Chunk {ev.chunk_index}\n"
            f"Text: {ev.text}"
            for ev in company_policy_list
        )
        regulations_str = "\n\n".join(
            f"Document: {ev.filename} (v{ev.document_version}), Page {ev.page_number}, Chunk {ev.chunk_index}\n"
            f"Text: {ev.text}"
            for ev in regulations_list
        )

        try:
            # Invoke structured output LLM chain
            result_llm: ComplianceAnalysisLLM = self._chain.invoke({
                "question": retrieval_result.question,
                "company_policy": company_policy_str,
                "regulations": regulations_str
            })

            # Map generated citations to actual retrieved Evidence objects (Requirement 5)
            sanitized_findings = []
            for finding_llm in result_llm.findings:
                validated_evidence = []
                for cite in finding_llm.evidence_citations:
                    # Match by filename and chunk_index
                    matched = False
                    for ev in company_policy_list + regulations_list:
                        if ev.filename == cite.filename and ev.chunk_index == cite.chunk_index:
                            validated_evidence.append(ev)
                            matched = True
                            break
                    if not matched:
                        logger.warning(
                            f"Rejected fabricated evidence citation: filename={cite.filename}, chunk_index={cite.chunk_index}"
                        )

                # Construct the final finding containing full Evidence models
                finding = ComplianceFinding(
                    control=finding_llm.control,
                    status=finding_llm.status,
                    company_requirement=finding_llm.company_requirement,
                    regulatory_requirement=finding_llm.regulatory_requirement,
                    reasoning=finding_llm.reasoning,
                    evidence=validated_evidence
                )
                sanitized_findings.append(finding)

            # Build final verified ComplianceAnalysis response
            result = ComplianceAnalysis(
                overall_status=result_llm.overall_status,
                summary=result_llm.summary,
                findings=sanitized_findings,
                confidence=result_llm.confidence,
                evidence_sufficient=result_llm.evidence_sufficient
            )

            logger.info(f"Compliance analysis completed. Status: {result.overall_status}, sufficiency: {result.evidence_sufficient}")
            return result

        except Exception as e:
            logger.error(f"Compliance analysis chain execution failed: {e}", exc_info=True)
            raise ValueError(f"Compliance analysis failed: {e}")

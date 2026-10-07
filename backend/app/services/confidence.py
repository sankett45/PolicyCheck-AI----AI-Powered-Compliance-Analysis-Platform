from typing import List, Dict, Any, Set
import uuid
from app.models.evidence_models import Evidence
from app.utils.logger import logger


class EvidenceConfidenceEngine:
    """Calculates deterministic confidence scores for retrieved compliance evidence."""

    @staticmethod
    def calculate_confidence(
        company_policy: List[Evidence],
        regulations: List[Evidence]
    ) -> Dict[str, Any]:
        """Calculate a deterministic confidence score and descriptive level for retrieved evidence.

        The score is computed using the following factors:
        1. Average Similarity Score (weight: 0.40)
        2. Cross-Source Presence (weight: 0.20)
        3. Chunk Coverage (weight: 0.15)
        4. Source Diversity (weight: 0.15)
        5. Metadata Completeness (weight: 0.10)

        Returns:
            Dict[str, Any]: Dict containing "confidence" (float) and "level" (str).
        """
        all_chunks = company_policy + regulations
        total_chunks = len(all_chunks)

        if total_chunks == 0:
            logger.info("Confidence calculation: No evidence chunks retrieved. Returning 0.0 confidence.")
            return {"confidence": 0.0, "level": "low"}

        # 1. Average Similarity Score (weight: 0.40)
        sum_scores = sum(max(0.0, c.similarity_score) for c in all_chunks)
        avg_similarity = sum_scores / total_chunks
        score_component = min(1.0, avg_similarity) * 0.40

        # 2. Cross-Source Presence (weight: 0.20)
        has_policy = len(company_policy) > 0
        has_regulation = len(regulations) > 0
        if has_policy and has_regulation:
            cross_source_val = 1.0
        elif has_policy or has_regulation:
            cross_source_val = 0.5
        else:
            cross_source_val = 0.0
        cross_source_component = cross_source_val * 0.20

        # 3. Chunk Coverage (weight: 0.15)
        chunk_coverage_val = min(1.0, total_chunks / 5.0)
        chunk_coverage_component = chunk_coverage_val * 0.15

        # 4. Source Diversity (weight: 0.15)
        unique_docs: Set[uuid.UUID] = {c.document_id for c in all_chunks}
        doc_diversity_val = min(1.0, len(unique_docs) / 3.0)
        doc_diversity_component = doc_diversity_val * 0.15

        # 5. Metadata Completeness (weight: 0.10)
        metadata_score_sum = 0.0
        for chunk in all_chunks:
            fields_checked = 0
            fields_complete = 0

            # document_version check
            fields_checked += 1
            if chunk.document_version and str(chunk.document_version).strip() not in ("", "None"):
                fields_complete += 1

            # filename check
            fields_checked += 1
            if chunk.filename and chunk.filename.strip():
                fields_complete += 1

            # document_type check
            fields_checked += 1
            if chunk.document_type and chunk.document_type.strip():
                fields_complete += 1

            # source check
            fields_checked += 1
            if chunk.source and chunk.source.strip():
                fields_complete += 1

            # page_number check
            fields_checked += 1
            if chunk.page_number is not None:
                fields_complete += 1

            metadata_score_sum += (fields_complete / fields_checked)

        avg_metadata_completeness = metadata_score_sum / total_chunks
        metadata_component = avg_metadata_completeness * 0.10

        # Combine components
        raw_confidence = (
            score_component +
            cross_source_component +
            chunk_coverage_component +
            doc_diversity_component +
            metadata_component
        )
        confidence = round(raw_confidence, 2)

        # Categorize level
        if confidence >= 0.80:
            level = "high"
        elif confidence >= 0.50:
            level = "medium"
        else:
            level = "low"

        logger.info(
            f"Confidence calculation: score={confidence}, level={level} "
            f"(similarity={avg_similarity:.4f}, cross_source={cross_source_val}, "
            f"chunks={total_chunks}, docs={len(unique_docs)}, metadata={avg_metadata_completeness:.4f})"
        )

        return {"confidence": confidence, "level": level}

from app.models.recommendation_models import RecommendationPriority


def risk_level_to_priority(risk_level: str) -> RecommendationPriority:
    """Map a risk level (low, medium, high, critical) to a recommendation priority level.

    Args:
        risk_level (str): The calculated risk level of a finding.

    Returns:
        RecommendationPriority: The mapped priority level.
    """
    cleaned = risk_level.strip().lower()
    if cleaned == "critical":
        return "critical"
    elif cleaned == "high":
        return "high"
    elif cleaned == "medium":
        return "medium"
    else:
        return "low"

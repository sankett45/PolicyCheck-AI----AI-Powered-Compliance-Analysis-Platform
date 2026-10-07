from app.models.risk_models import RiskLevel

# Centralized Risk Threshold Map
# Range keys are inclusive bounds
RISK_THRESHOLDS = [
    {"max_score": 20, "level": "low"},
    {"max_score": 50, "level": "medium"},
    {"max_score": 80, "level": "high"},
    {"max_score": 125, "level": "critical"},
]


def calculate_risk_score(severity: int, likelihood: int, impact: int) -> int:
    """Calculate a deterministic risk score using multiplication of three risk dimensions.

    Args:
        severity (int): Scale 1-5
        likelihood (int): Scale 1-5
        impact (int): Scale 1-5

    Returns:
        int: Score between 1 and 125. Values outside 1-5 bounds are clamped.
    """
    # Enforce constraints strictly in application logic
    sev_clamped = max(1, min(5, severity))
    lik_clamped = max(1, min(5, likelihood))
    imp_clamped = max(1, min(5, impact))

    return sev_clamped * lik_clamped * imp_clamped


def map_score_to_level(score: int) -> RiskLevel:
    """Map a numerical risk score to a string risk level (low, medium, high, critical).

    Args:
        score (int): Score between 1 and 125 (or 0 for no risks).

    Returns:
        RiskLevel: The categorized risk level.
    """
    # If the score is 0, map to low risk directly
    if score <= 0:
        return "low"

    for threshold in RISK_THRESHOLDS:
        if score <= threshold["max_score"]:
            return threshold["level"]

    return "critical"

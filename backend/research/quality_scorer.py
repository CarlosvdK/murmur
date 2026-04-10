"""
Quality scorer for experiment corpus records.

Scores 0.0-1.0 based on methodological rigour.
Used to weight records in ML training and backtesting.
"""

TOP_JOURNALS = [
    "Management Science", "Marketing Science",
    "Journal of Marketing Research", "Journal of Consumer Research",
    "American Economic Review", "Journal of Finance",
    "Journal of Marketing", "Psychological Science",
    "Harvard Business Review",
    "Journal of Personality and Social Psychology",
    "Econometrica", "Review of Economic Studies",
    "Quarterly Journal of Economics", "MIS Quarterly",
    "Journal of Retailing", "Journal of Business Research",
    "Cornell Hospitality Quarterly",
    "International Journal of Hospitality Management",
]


def score_experiment(record: dict) -> float:
    max_score = 100.0
    earned = 0.0

    if record.get("peer_reviewed"):
        earned += 25

    if record.get("had_control_group"):
        earned += 20

    if record.get("was_randomised"):
        earned += 15

    n = record.get("sample_size") or 0
    if n >= 10000:
        earned += 15
    elif n >= 1000:
        earned += 12
    elif n >= 100:
        earned += 8
    elif n >= 30:
        earned += 4

    sig = record.get("statistical_significance", "")
    if sig == "significant":
        earned += 10
    elif sig == "not_significant":
        earned += 5

    if record.get("effect_size_numeric") is not None:
        earned += 10

    if record.get("publication_name") in TOP_JOURNALS:
        earned += 5

    return round(earned / max_score, 3)


def is_usable_for_calibration(record: dict) -> bool:
    return score_experiment(record) >= 0.40


def is_usable_for_backtesting(record: dict) -> bool:
    return score_experiment(record) >= 0.60

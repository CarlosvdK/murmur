"""
Signal Detection -- detects relationship health changes from communication patterns.

Rule-based, deterministic, explainable. No ML.
Runs when new correspondence is processed.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    type: str          # response_time_increasing, formality_increasing, etc
    severity: str      # info, warning, critical
    title: str
    message: str
    recommendation: str


def detect_signals(
    current_signals: dict,
    historical_baseline: Optional[dict] = None,
) -> list[Signal]:
    """Detect relationship health signals from current vs historical patterns.

    If no historical baseline, uses industry defaults.
    """
    signals: list[Signal] = []

    baseline = historical_baseline or {
        "avg_response_hours": 8,
        "formality_level": 5,
        "initiator_ratio": 0.5,
    }

    # 1. Response time increasing
    current_rt = current_signals.get("avg_response_hours")
    baseline_rt = baseline.get("avg_response_hours", 8)
    if current_rt and baseline_rt and current_rt > baseline_rt * 2:
        signals.append(Signal(
            type="response_time_increasing",
            severity="warning",
            title="Response time has increased",
            message=(
                f"Average response time is now {current_rt:.0f} hours, "
                f"compared to a baseline of {baseline_rt:.0f} hours."
            ),
            recommendation="Consider reaching out to check in. A simple personal message can surface if something has changed.",
        ))

    # 2. Formality increasing
    current_formal = current_signals.get("formality_level")
    baseline_formal = baseline.get("formality_level", 5)
    if current_formal and baseline_formal and current_formal > baseline_formal + 2:
        signals.append(Signal(
            type="formality_increasing",
            severity="warning",
            title="Communication becoming more formal",
            message=(
                f"Formality level is now {current_formal}/10, "
                f"up from a baseline of {baseline_formal}/10. "
                "This can signal distance or concern."
            ),
            recommendation="Match their tone but add a personal touch. Ask an open-ended question to understand what has shifted.",
        ))

    # 3. Negative signals detected
    neg_signals = current_signals.get("negative_signals", [])
    if len(neg_signals) >= 2:
        signals.append(Signal(
            type="negative_pattern_detected",
            severity="warning",
            title="Negative patterns detected in communication",
            message=f"Multiple concerning patterns identified: {', '.join(neg_signals[:3])}",
            recommendation="Address these directly in your next conversation. Ignoring them typically makes them worse.",
        ))

    # 4. Low initiation ratio (they never reach out first)
    init_ratio = current_signals.get("initiator_ratio")
    if init_ratio is not None and init_ratio > 0.85:
        signals.append(Signal(
            type="one_sided_communication",
            severity="info",
            title="Communication is mostly one-sided",
            message=(
                f"You initiate {init_ratio*100:.0f}% of conversations. "
                "This may indicate low engagement from their side."
            ),
            recommendation="Try creating a reason for them to reach out to you instead of always initiating.",
        ))

    # 5. Positive signals
    pos_signals = current_signals.get("positive_signals", [])
    if len(pos_signals) >= 2:
        signals.append(Signal(
            type="positive_pattern_detected",
            severity="info",
            title="Positive relationship signals",
            message=f"Encouraging patterns: {', '.join(pos_signals[:3])}",
            recommendation="This relationship is in a good place. Consider deepening the connection or expanding the scope.",
        ))

    logger.info("Signal detection: %d signals found", len(signals))
    return signals

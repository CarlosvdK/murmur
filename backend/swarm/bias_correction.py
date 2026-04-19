"""
Behavioral bias-correction layer.

This module applies a structural, research-grounded correction to the
aggregation result BEFORE it is returned to the user. It is distinct
from ``research_override``: the override is an LLM judgement ("does
research contradict persona consensus"), while this layer is a hard
numerical correction based on tactic class and published effect sizes
from the research corpus.

The layer is conservative and transparent:
- It never silently changes the winner. It adjusts sentiment and
  emits a ``bias_correction`` block attached to the result.
- It cites the tactic class and the research-backed correction size.
- It defers to stronger signals: if the two-shot core turn surfaced
  a large ``gap_size`` per persona, the correction is already
  partially applied in revealed-sentiment data and we scale down
  the hard adjustment to avoid double-counting.

This is where Murphy et al. 2005 (stated-vs-revealed gap ~28%) and
Gui & Toubia 2023 (LLM optimism 20-30%) live in code form. Growing
this module is how the product learns from real outcomes: future
versions fit the correction sizes from backtest-vs-reality data
instead of hard-coding them.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Correction table -- by tactic class
# ---------------------------------------------------------------------------
#
# Each tactic has:
#   stated_to_revealed_shift -- how far, on a -1..+1 sentiment scale,
#     personas' stated sentiment is systematically *more* negative than
#     revealed behaviour. Positive values mean "real users respond better
#     than personas say they will."
#   research_confidence -- how strong the supporting literature is.
#   citations -- short-form citation keys, rendered to the UI.
#
# Values are deliberately conservative. They are priors, not point
# estimates. Future versions should replace these with fitted values from
# the real-outcomes learning loop.

@dataclass
class TacticCorrection:
    tactic: str
    stated_to_revealed_shift: float
    research_confidence: str   # "low" | "medium" | "high"
    citations: list[str] = field(default_factory=list)
    note: str = ""


TACTIC_CORRECTIONS: dict[str, TacticCorrection] = {
    "scarcity_urgency": TacticCorrection(
        tactic="scarcity_urgency",
        stated_to_revealed_shift=+0.18,
        research_confidence="high",
        citations=["Cialdini 2001", "Aggarwal 2011", "Murphy 2005"],
        note=(
            "Personas say urgency messaging annoys them. Published field "
            "tests show urgency consistently lifts conversion 5-20% despite "
            "stated dislike."
        ),
    ),
    "long_copy": TacticCorrection(
        tactic="long_copy",
        stated_to_revealed_shift=+0.22,
        research_confidence="medium",
        citations=["Basecamp long-form 37.5%", "Crazy Egg 363%"],
        note=(
            "Personas prefer short clean pages. Real A/B tests on "
            "higher-consideration purchases (SaaS, info products, tools) "
            "routinely show long-form pages converting substantially better."
        ),
    ),
    "restriction_exclusivity": TacticCorrection(
        tactic="restriction_exclusivity",
        stated_to_revealed_shift=+0.15,
        research_confidence="medium",
        citations=["Iyengar 2000 choice overload", "IKEA forced path"],
        note=(
            "Personas dislike feeling restricted or forced down a path. "
            "Reduced option sets and guided flows tend to lift basket size "
            "and completion rates in field tests."
        ),
    ),
    "default_optout": TacticCorrection(
        tactic="default_optout",
        stated_to_revealed_shift=+0.25,
        research_confidence="high",
        citations=["Johnson & Goldstein 2003", "Thaler & Sunstein 2008"],
        note=(
            "Defaults drive 70-90% of choices in field evidence. Personas "
            "claim they would change the default; most don't."
        ),
    ),
    "personal_tone": TacticCorrection(
        tactic="personal_tone",
        stated_to_revealed_shift=+0.10,
        research_confidence="medium",
        citations=["Obama 2012 'Hey' subject line", "Groove founder emails"],
        note=(
            "Personal / informal tone from a named sender outperforms "
            "corporate tone in email open rates and response rates."
        ),
    ),
    "visual_micro": TacticCorrection(
        tactic="visual_micro",
        stated_to_revealed_shift=+0.05,
        research_confidence="low",
        citations=["Google 41 shades of blue", "Zalora larger images"],
        note=(
            "Personas treat micro-visual changes (colour, image size, "
            "spacing) as irrelevant. Field tests show small but real lift."
        ),
    ),
    "friction_reduction": TacticCorrection(
        tactic="friction_reduction",
        stated_to_revealed_shift=+0.30,
        research_confidence="high",
        citations=["Amazon one-click", "Murphy 2005", "Thaler 2008"],
        note=(
            "One-click, guest checkout, shorter forms, saved payment: the "
            "class with the largest stated-vs-revealed gap. Personas flag "
            "'laziness' concerns; real users overwhelmingly adopt."
        ),
    ),
    "habit_loop": TacticCorrection(
        tactic="habit_loop",
        stated_to_revealed_shift=+0.20,
        research_confidence="high",
        citations=["Duolingo streaks", "Eyal Hooked 2014", "Fogg BJ"],
        note=(
            "Streaks, daily nudges, progress bars, badges. Personas call "
            "them manipulative; real users show 20-40% retention lift."
        ),
    ),
    "social_proof": TacticCorrection(
        tactic="social_proof",
        stated_to_revealed_shift=+0.12,
        research_confidence="medium",
        citations=["Cialdini 2001", "DellaVigna 2009"],
        note=(
            "Testimonials, review counts, 'N others bought this'. Personas "
            "claim immunity; field evidence shows consistent lift, "
            "amplified when choice is visible."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def apply_bias_correction(
    aggregation_result: dict,
    question: str,
    tactic: Optional[str] = None,
    average_stated_sentiment: Optional[float] = None,
    average_revealed_sentiment: Optional[float] = None,
) -> dict:
    """Apply the research-backed bias correction for a detected tactic.

    This NEVER overwrites the aggregation result destructively. It attaches
    a ``bias_correction`` block with:
      - tactic_detected
      - stated_to_revealed_shift (the correction prior)
      - stated_sentiment (input)
      - corrected_sentiment (input plus correction, scaled down if the
        two-shot revealed sentiment already captured part of the gap)
      - research_confidence
      - citations
      - note

    If no tactic is provided or none matches, returns the result unchanged.
    If the two-shot ``average_revealed_sentiment`` is available and differs
    substantially from ``average_stated_sentiment``, the correction is
    scaled down by the magnitude of the gap already observed -- so we
    don't double-count.
    """
    out = dict(aggregation_result)
    if not tactic:
        return out

    correction = TACTIC_CORRECTIONS.get(tactic)
    if correction is None:
        return out

    stated = average_stated_sentiment
    revealed = average_revealed_sentiment
    shift = correction.stated_to_revealed_shift

    # If the two-shot elicitation already captured part of the gap in
    # revealed-sentiment data, shrink the hard correction proportionally.
    # This prevents double-counting.
    scale = 1.0
    gap_observed = None
    if stated is not None and revealed is not None:
        gap_observed = revealed - stated
        if shift > 0:
            # Fraction of the expected shift already accounted for.
            already = max(0.0, min(1.0, gap_observed / shift))
            scale = max(0.0, 1.0 - already)

    effective_shift = shift * scale

    base_sentiment = revealed if revealed is not None else stated
    corrected_sentiment = None
    if base_sentiment is not None:
        corrected_sentiment = max(-1.0, min(1.0, base_sentiment + effective_shift))

    logger.info(
        "bias_correction tactic=%s shift=%.2f scale=%.2f "
        "stated=%s revealed=%s corrected=%s",
        tactic, shift, scale,
        f"{stated:.2f}" if stated is not None else "n/a",
        f"{revealed:.2f}" if revealed is not None else "n/a",
        f"{corrected_sentiment:.2f}" if corrected_sentiment is not None else "n/a",
    )

    out["bias_correction"] = {
        "tactic": correction.tactic,
        "stated_to_revealed_shift_prior": shift,
        "scale_after_two_shot_gap": round(scale, 3),
        "effective_shift": round(effective_shift, 3),
        "stated_sentiment": stated,
        "revealed_sentiment": revealed,
        "corrected_sentiment": (
            round(corrected_sentiment, 3) if corrected_sentiment is not None else None
        ),
        "observed_two_shot_gap": (
            round(gap_observed, 3) if gap_observed is not None else None
        ),
        "research_confidence": correction.research_confidence,
        "citations": correction.citations,
        "note": correction.note,
    }
    return out


def average_sentiments_from_responses(
    responses: list[dict],
) -> tuple[float, Optional[float]]:
    """Compute mean stated sentiment and (if available) mean revealed
    sentiment across a list of persona responses.

    ``stated`` comes from the core-turn ``sentiment`` inside ``core``.
    ``revealed`` comes from the turn-2b ``actual_sentiment``. If no
    revealed sentiments are available returns ``(stated, None)``.
    """
    stated_vals: list[float] = []
    revealed_vals: list[float] = []

    for r in responses:
        core = r.get("core") or {}
        try:
            s = float(core.get("sentiment", r.get("sentiment", 0.0)))
            stated_vals.append(s)
        except (TypeError, ValueError):
            pass

        actual = (r.get("actual") or {}).get("actual_sentiment")
        if actual is None:
            actual = core.get("actual_sentiment")
        try:
            if actual is not None:
                revealed_vals.append(float(actual))
        except (TypeError, ValueError):
            pass

    stated_avg = sum(stated_vals) / len(stated_vals) if stated_vals else 0.0
    revealed_avg = (
        sum(revealed_vals) / len(revealed_vals) if revealed_vals else None
    )
    return stated_avg, revealed_avg

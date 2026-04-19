"""
Research Override -- post-aggregation check for stated vs revealed
preference conflicts.

Runs AFTER the aggregator produces its synthesis. Compares the persona
consensus against published behavioral research (persuasion tactics,
default effects, scarcity studies, etc.) and flags cases where the
research predicts a different outcome than the personas stated.

This module is advisory. It says "research suggests X" -- it never
overrides the aggregator outright.
"""

import json
import logging
import re
from typing import Optional

from anthropic import AsyncAnthropic

from backend.config import get_settings
from research.rag_library import get_domain_insights

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tactic detection patterns
# ---------------------------------------------------------------------------

TACTIC_PATTERNS: dict[str, list[str]] = {
    "scarcity_urgency": [
        r"\burgenc[y]?\b",
        r"\bscarcit[y]?\b",
        r"\bonly\s+\d+\s+left\b",
        r"\blimited\s+time\b",
        r"\bhurr[y]?\b",
        r"\bcountdown\b",
        r"\bdeadline\b",
    ],
    "long_copy": [
        r"\blonger?\s+page\b",
        r"\blong[- ]?form\b",
        r"\bmore\s+detail\b",
        r"\bmore\s+content\b",
        r"\bmore\s+information\b",
        r"\bcomprehensive\b",
        r"\bin[- ]depth\b",
        r"\bdetailed\s+(sales|landing)\s+page\b",
    ],
    "restriction_exclusivity": [
        r"\bremove\s+options?\b",
        r"\bsimplify\s+menu\b",
        r"\bforce\s+path\b",
        r"\bforced\s+path\b",
        r"\bguided\s+(store|path|layout|flow)\b",
        r"\bpaywall\b",
        r"\bmembership\b",
        r"\bexclusive\b",
        r"\blimit\b",
        r"\bremove\s+exit\b",
        r"\bsingle\s+path\b",
    ],
    "default_optout": [
        r"\bdefault\b",
        r"\bopt[- ]?out\b",
        r"\bpre[- ]?select\b",
        r"\bauto[- ]?enroll\b",
        r"\bremove\s+navigation\b",
        r"\bguest\s+checkout\b",
        r"\bsimplify\s+form\b",
        r"\bremove\s+field\b",
    ],
    "personal_tone": [
        r"\bpersonal\b",
        r"\bcasual\b",
        r"\binformal\b",
        r"\bfirst\s+person\b",
        r"\bfounder\b",
        r"\bhuman\b",
        r"\bfriendly\s+tone\b",
    ],
    "visual_micro": [
        r"\bcolor\b",
        r"\bcolour\b",
        r"\bshade\b",
        r"\bhue\b",
        r"\bbutton\s+(color|colour|shade)\b",
        r"\bsize\b",
        r"\bimage\s+size\b",
        r"\blarger\s+(image|photo|product)s?\b",
        r"\bload\s+speed\b",
        r"\bfaster\b",
        r"\bpage\s+speed\b",
        r"\bfont\b",
        r"\bspacing\b",
        r"\blayout\s+tweak\b",
    ],
    # Frictionless purchase / one-click / simplification of checkout or flow.
    # Personas tend to call this "lazy" or "risky" and underweight it; real
    # users overwhelmingly prefer it (Amazon one-click, guest checkout,
    # simplified forms). Murphy et al. 2005 gap is strongest here.
    "friction_reduction": [
        r"\bone[- ]?click\b",
        r"\bsingle[- ]?click\b",
        r"\bquick\s+checkout\b",
        r"\bexpress\s+checkout\b",
        r"\bguest\s+checkout\b",
        r"\bauto[- ]?fill\b",
        r"\bsave(d)?\s+payment\b",
        r"\bstore\s+card\b",
        r"\bremove\s+(step|steps)\b",
        r"\bfewer\s+(step|click|form)s?\b",
        r"\bstreamline(d)?\b",
        r"\bsimplif(y|ied|ication)\b",
        r"\bshorter\s+(form|checkout|signup)\b",
        r"\bskip\s+(step|form|signup)\b",
    ],
    # Habit-loop tactics: streaks, daily reminders, notifications, badges.
    # Personas say notifications are annoying and streaks are manipulative.
    # Real users show 20-40% retention lift (Duolingo, fitness apps).
    "habit_loop": [
        r"\bstreak(s)?\b",
        r"\bdaily\s+(reminder|notification|nudge)\b",
        r"\bpush\s+notification\b",
        r"\bnotification\s+reminder\b",
        r"\breminder\b",
        r"\bnudge\b",
        r"\bbadge(s)?\b",
        r"\bgamif(y|ied|ication)\b",
        r"\bdaily\s+login\s+(reward|bonus)\b",
        r"\bleaderboard\b",
        r"\bprogress\s+bar\b",
    ],
    # Social-proof tactics: "join 10,000 others", testimonials prominently
    # displayed, follower counts. Personas claim immunity; research shows
    # consistent lift (Cialdini).
    "social_proof": [
        r"\bsocial\s+proof\b",
        r"\btestimonial\b",
        r"\breviews?\s+(prominently|on\s+checkout|near\s+cta)\b",
        r"\bjoin\s+\d[\d,]*\s+(other|customer|user)s?\b",
        r"\bas\s+seen\s+(on|in)\b",
        r"\btrust\s+badge\b",
        r"\b\d+[\+,]?\s*(reviews?|stars?|ratings?)\s+displayed\b",
    ],
}

# Pre-compile all patterns for performance
_COMPILED_PATTERNS: dict[str, list[re.Pattern]] = {
    tactic: [re.compile(p, re.IGNORECASE) for p in patterns]
    for tactic, patterns in TACTIC_PATTERNS.items()
}


def _detect_tactic(question: str) -> Optional[str]:
    """Return the first matching tactic type, or None."""
    for tactic, patterns in _COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(question):
                return tactic
    return None


def _no_override(tactic: Optional[str] = None, reason: Optional[str] = None) -> dict:
    """Standard no-override response."""
    out = {
        "override_applied": False,
        "tactic_detected": tactic,
    }
    if reason:
        out["no_override_reason"] = reason
    return out


# Heuristic keywords that suggest a tactic SHOULD have fired but didn't match
# any pattern. Used to log misses so we can grow the taxonomy over time.
_SUSPICIOUS_MISS_KEYWORDS = [
    "notification", "reminder", "streak", "badge", "gamif",
    "checkout", "one-click", "one click", "quick", "express",
    "urgency", "scarcity", "only", "limited",
    "forced", "guided", "remove", "simplif", "streamline",
    "longer", "long-form", "long form", "detailed",
    "color", "colour", "shade", "image", "button",
    "testimonial", "social proof", "review",
    "personal", "founder", "first person",
    "default", "opt-in", "opt-out", "auto-enroll",
]


def _log_suspicious_miss(question: str) -> None:
    """If the question contains a tactic-like keyword but no pattern matched,
    log it loudly so we can extend the taxonomy. This is how we learn where
    the override blind spots are."""
    lower = question.lower()
    hits = [kw for kw in _SUSPICIOUS_MISS_KEYWORDS if kw in lower]
    if hits:
        logger.warning(
            "research_override.suspicious_miss question=%r hits=%s",
            question[:200], hits,
        )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def apply_research_override(
    question: str,
    aggregation_result: dict,
    persona_responses: list[dict],
    business_type: str = "",
) -> dict:
    """Check whether published research contradicts the persona consensus.

    Runs a single Claude API call that compares the aggregation output
    against known behavioral science findings. Returns an advisory
    override dict if a stated-vs-revealed preference conflict is found.

    If no relevant tactic is detected in the question, returns
    immediately with ``{"override_applied": False}`` and makes no API
    call.

    This function never raises. Errors are logged and a no-override
    result is returned so the pipeline continues uninterrupted.
    """
    try:
        # Step 1: detect tactic type
        tactic = _detect_tactic(question)
        if tactic is None:
            # Log when the question smells like a tactic but matched nothing,
            # so we can grow the taxonomy.
            _log_suspicious_miss(question)
            logger.debug(
                "No persuasion tactic detected in question: '%s'",
                question[:80],
            )
            return _no_override(reason="no_tactic_matched")

        logger.info(
            "Tactic '%s' detected in question: '%s'", tactic, question[:80]
        )

        # Step 2: load research
        research_text = get_domain_insights("persuasion_tactics")
        if not research_text:
            logger.warning(
                "persuasion_tactics research not found -- skipping override"
            )
            return _no_override(tactic)

        # Step 3: build the Claude request
        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        summary = aggregation_result.get("summary", "")
        recommendation = aggregation_result.get("recommendation", "")

        user_prompt = (
            f"## Question asked\n{question}\n\n"
            f"## Aggregation summary\n{summary}\n\n"
            f"## Aggregation recommendation\n{recommendation}\n\n"
            f"## Detected tactic type\n{tactic}\n\n"
            f"## Business type\n{business_type or 'unknown'}\n\n"
            f"## Published behavioral research\n{research_text}\n\n"
            "Based on the research above, determine whether the persona "
            "consensus is likely to match actual customer behavior for "
            "this specific tactic type. If published research predicts a "
            "different outcome, produce an override recommendation.\n\n"
            "Return ONLY valid JSON with these fields:\n"
            "- override_applied (bool): should the recommendation be adjusted?\n"
            "- tactic_detected (str): which tactic type was identified\n"
            "- persona_prediction (str): what the personas predicted (1 sentence)\n"
            "- research_prediction (str): what published research predicts (1 sentence)\n"
            '- conflict_level (str): "none", "mild", or "strong"\n'
            "- adjusted_recommendation (str): what the recommendation should be, "
            "incorporating both persona feedback AND research (2-3 sentences). "
            'Use advisory language like "research suggests" not "you must".\n'
            '- research_confidence (str): "high", "medium", or "low"\n'
            "- key_citations (list of str): which studies support the override\n"
            '- predicted_direction (str): what the published research predicts the '
            'real-world outcome will be. One of: "positive" (the change will likely '
            'win / increase the target metric), "negative" (the change will likely '
            'hurt), or "unclear".\n'
            '- predicted_ab_winner (str or null): if this was an A vs B comparison, '
            'which option does the research predict wins? Return "A", "B", '
            '"tie", or null if not applicable.\n\n'
            "If the aggregation already aligns with the research (no conflict), "
            "set override_applied to false and conflict_level to none."
        )

        response = await client.messages.create(
            model=settings.model_name,
            max_tokens=1024,
            system=(
                "You are a behavioral science expert reviewing a customer "
                "simulation. The simulation asked synthetic customers about "
                "a proposed change. Check whether published behavioral "
                "research suggests the actual outcome would differ from what "
                "customers stated."
            ),
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text

        # Parse JSON from the response
        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try extracting from markdown code fence
            if "```" in raw_text:
                json_str = raw_text.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                result = json.loads(json_str.strip())
            else:
                logger.error(
                    "Failed to parse research override JSON: %s",
                    raw_text[:200],
                )
                return _no_override(tactic)

        # If the model says no conflict, return a clean no-override
        if not result.get("override_applied", False):
            logger.info("Research override: no conflict detected for tactic '%s'", tactic)
            return _no_override(tactic)

        # Ensure all expected keys are present with safe defaults
        override = {
            "override_applied": True,
            "tactic_detected": result.get("tactic_detected", tactic),
            "persona_prediction": result.get("persona_prediction", ""),
            "research_prediction": result.get("research_prediction", ""),
            "conflict_level": result.get("conflict_level", "mild"),
            "adjusted_recommendation": result.get("adjusted_recommendation", ""),
            "research_confidence": result.get("research_confidence", "medium"),
            "key_citations": result.get("key_citations", []),
            "predicted_direction": result.get("predicted_direction", "unclear"),
            "predicted_ab_winner": result.get("predicted_ab_winner"),
        }

        logger.info(
            "Research override applied -- tactic=%s, conflict=%s, confidence=%s",
            override["tactic_detected"],
            override["conflict_level"],
            override["research_confidence"],
        )

        return override

    except Exception:
        logger.exception("Research override failed -- returning no-override")
        return _no_override()


# ---------------------------------------------------------------------------
# Promoting a strong override into a winner flip
# ---------------------------------------------------------------------------

def apply_override_to_result(
    aggregation_result: dict,
    override: dict,
) -> dict:
    """When the research override is both STRONG and HIGH-confidence, promote
    it from advisory text into an actual mutation of the aggregation result:

    - Replace ``recommendation`` with the adjusted recommendation (prefixed
      with a note so the UI can surface it).
    - Override ``winner`` with ``predicted_ab_winner`` when present.
    - Record a ``winner_flipped`` flag plus the old winner for transparency.

    Rationale: previously the override was text-only and only appended to
    the recommendation, so the scored ``winner`` field never changed. Real
    failure classes in backtesting (friction-reducing tactics, habit loops,
    urgency) show personas saying one thing and real users doing the
    opposite -- the override should actually flip the prediction in those
    cases, not just annotate it.

    Always returns a dict. Never raises. If the override is weak, mild, or
    missing, returns ``aggregation_result`` unchanged (copied).
    """
    result = dict(aggregation_result)  # shallow copy to avoid aliasing
    if not override or not override.get("override_applied"):
        return result

    conflict = (override.get("conflict_level") or "").lower()
    confidence = (override.get("research_confidence") or "").lower()
    promote = conflict == "strong" and confidence == "high"

    # Always attach the override payload for transparency / UI.
    result["research_override"] = override

    if not promote:
        return result

    adjusted = override.get("adjusted_recommendation", "").strip()
    if adjusted:
        original = result.get("recommendation", "") or ""
        # Prefix the adjusted version so downstream consumers see it first,
        # but preserve the original for auditing.
        result["recommendation"] = (
            f"[Research-adjusted] {adjusted}"
        )
        result["original_recommendation"] = original

    predicted_winner = override.get("predicted_ab_winner")
    if predicted_winner in ("A", "B", "tie"):
        old_winner = result.get("winner")
        if old_winner != predicted_winner:
            result["winner"] = predicted_winner
            result["winner_flipped"] = True
            result["winner_flipped_from"] = old_winner
            result["winner_flip_reason"] = (
                f"Research override: {override.get('tactic_detected')} tactic -- "
                f"published research predicts {predicted_winner} wins despite persona "
                "consensus. This is the stated-vs-revealed preference gap "
                "(Murphy et al. 2005)."
            )
            logger.info(
                "Research override FLIPPED winner %s -> %s (tactic=%s)",
                old_winner, predicted_winner, override.get("tactic_detected"),
            )

    return result

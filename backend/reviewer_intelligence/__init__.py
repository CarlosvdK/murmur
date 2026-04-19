"""
Reviewer Intelligence System -- builds a research-grounded customer
segment distribution from Google Reviews + demographic data + bias corrections.

Entry point: build_reviewer_intelligence()
Never raises. Returns None on failure so the pipeline falls back to freeform generation.
"""

import logging
from typing import Optional, Callable

from backend.models.business import BusinessSnapshot
from backend.reviewer_intelligence.review_signal_extractor import (
    extract_review_signals,
    AggregateReviewSignals,
)
from backend.reviewer_intelligence.bias_corrector import (
    apply_bias_corrections,
    BiasAdjustedSignals,
)
from backend.reviewer_intelligence.silent_majority_estimator import (
    estimate_silent_majority,
)
from backend.reviewer_intelligence.customer_segment_builder import (
    build_segments,
    CustomerSegmentProfile,
)
from backend.reviewer_intelligence.persona_calibrator import (
    calibrate_personas,
    PersonaGenerationManifest,
)
from backend.reviewer_intelligence.demographic_fallback import (
    build_fallback_signals,
)

logger = logging.getLogger(__name__)


async def build_reviewer_intelligence(
    business: BusinessSnapshot,
    persona_count: int = 15,
    on_progress: Optional[Callable[[str], None]] = None,
) -> Optional[PersonaGenerationManifest]:
    """Main entry point. Builds a calibrated persona manifest from review signals.

    Returns None if review data is unavailable or extraction fails.
    The caller should fall back to freeform persona generation.
    """
    try:
        if on_progress:
            on_progress("Analysing your customer base from review patterns...")

        # Step 1: Extract aggregate signals from Google Reviews
        signals = await extract_review_signals(
            business_name=business.name,
            location=business.location,
            on_progress=on_progress,
        )

        if signals is None:
            # Demographic fallback: rather than dropping the manifest entirely
            # (which loses all structured anchoring), synthesise low-confidence
            # signals from business-type + location priors. The resulting
            # manifest is marked confidence="low" and carries an explicit
            # bias warning downstream.
            logger.info(
                "No review signals available -- using demographic fallback for %s",
                business.name,
            )
            if on_progress:
                on_progress("No review data found -- using industry priors for this business type")
            signals = build_fallback_signals(
                business_name=business.name,
                business_type=business.type,
                location=business.location,
            )

        # Step 2: Apply bias corrections
        if on_progress:
            on_progress("Adjusting for review biases (extremity, platform, silent majority)...")

        adjusted = apply_bias_corrections(signals, business_type=business.type)

        # Step 3: Estimate silent majority
        silent = estimate_silent_majority(
            adjusted,
            tourist_ratio=signals.tourist_ratio_estimate,
        )

        # Step 4: Build customer segments
        if on_progress:
            on_progress("Building customer segment distribution...")

        segment_profile = build_segments(adjusted, silent, business, business_type=business.type)

        # Step 5: Calibrate persona manifest
        manifest = calibrate_personas(segment_profile, persona_count)

        if on_progress:
            on_progress(
                f"Customer analysis complete -- {manifest.total_count} personas across "
                f"{len(segment_profile.segments)} segments"
            )

        logger.info(
            "Reviewer intelligence complete: %d segments, %d personas, confidence=%s",
            len(segment_profile.segments),
            manifest.total_count,
            segment_profile.confidence_level,
        )

        return manifest

    except Exception as e:
        logger.exception("Reviewer intelligence failed: %s", e)
        if on_progress:
            on_progress("Customer analysis failed -- using business profile only")
        return None

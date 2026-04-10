"""
Backtest Runner

Takes published A/B test cases, fills out Murmur surveys for each,
runs real simulations through the Claude API, and scores our
predictions against what actually happened.

This produces REAL training data for the ML models, not synthetic.

Usage:
    python -m backend.ml.backtest_runner

    # Or run a single test:
    python -m backend.ml.backtest_runner --test 1
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

from backend.models.business import BusinessSnapshot
from backend.swarm import generate_personas, run_simulation, aggregate_responses
from backend.swarm.caveats import generate_caveats
from backend.impact import estimate_impact
from backend.survey.feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "backtest_results"
RESULTS_DIR.mkdir(exist_ok=True)


# ============================================================
# BACKTEST CASES -- each is a real published A/B test
# ============================================================

BACKTEST_CASES = [
    {
        "id": 1,
        "name": "Booking.com -- Urgency Messaging",
        "source": "Booking.com engineering blog / CXL Institute",
        "real_winner": "with_urgency",
        "real_outcome": "Urgency messaging increased conversions significantly",
        "holdout": False,
        "survey": {
            "name": "City View Hotel",
            "type": "hotel",
            "description": "Small boutique hotel in a European city centre, 25 rooms, mostly business travellers and weekend tourists.",
            "customer_description": "Mix of business travellers (Mon-Thu) and leisure tourists (Fri-Sun). Most book online, compare 3-4 hotels before deciding.",
            "location": "Amsterdam, Netherlands",
            "location_country": "NL",
            "years_open": "3-10",
            "business_role": "convenience",
            "visit_frequency": "occasional",
            "customer_value_drivers": ["convenience", "value"],
            "regular_proportion": "handful",
            "area_demographics": ["tourist", "business"],
            "competitor_count": "six_plus",
            "area_feel": "transactional",
        },
        "question": "Should we show customers a message saying 'Only a few rooms left!' when availability is low?",
        "variant_a": "Show urgency message when few rooms left",
        "variant_b": "No urgency messaging, just show availability normally",
        "expected_winner": "A",
    },
    {
        "id": 2,
        "name": "Netflix -- Artwork Personalization",
        "source": "Netflix Tech Blog 2017",
        "real_winner": "personalized",
        "real_outcome": "Personalized artwork significantly increased engagement",
        "holdout": False,
        "survey": {
            "name": "Local Film Club",
            "type": "other",
            "description": "Small DVD rental and streaming recommendation service for film enthusiasts. Curated collections by genre and mood.",
            "customer_description": "Film buffs aged 25-55 who value curation. Come for recommendations they can't find on mainstream platforms.",
            "location": "London, UK",
            "location_country": "GB",
            "years_open": "1-3",
            "business_role": "destination",
            "visit_frequency": "weekly",
            "customer_value_drivers": ["specific_product", "quality"],
            "regular_proportion": "solid_base",
            "area_demographics": ["residential"],
            "competitor_count": "three_five",
        },
        "question": "Should we customise which cover image we show for each film based on what we know about the customer's taste?",
        "variant_a": None,
        "variant_b": None,
        "expected_winner": "positive",
    },
    {
        "id": 3,
        "name": "HubSpot -- Remove Landing Page Navigation",
        "source": "HubSpot Marketing Blog",
        "real_winner": "remove_nav",
        "real_outcome": "Removing navigation increased conversions by up to 28%",
        "holdout": False,
        "survey": {
            "name": "Green Consulting",
            "type": "accountant",
            "description": "Small sustainability consulting firm offering free initial consultations. Website drives most leads.",
            "customer_description": "Small business owners looking for help with sustainability reporting. Usually comparison shopping between 2-3 consultants.",
            "location": "Dublin, Ireland",
            "location_country": "IE",
            "years_open": "1-3",
            "business_role": "destination",
            "visit_frequency": "occasional",
            "customer_value_drivers": ["quality", "personal_touch"],
            "area_demographics": ["business"],
            "competitor_count": "one_two",
        },
        "question": "On our 'Book a Free Consultation' page, should we remove all other navigation links so customers can only book or leave?",
        "variant_a": "Remove all navigation, only show booking form",
        "variant_b": "Keep full site navigation on the booking page",
        "expected_winner": "A",
    },
    {
        "id": 4,
        "name": "Etsy -- Free Shipping Threshold",
        "source": "Etsy Seller Handbook / earnings calls 2019",
        "real_winner": "free_shipping",
        "real_outcome": "Free shipping items had significantly higher conversion rates",
        "holdout": False,
        "survey": {
            "name": "Hannah's Handmade",
            "type": "other",
            "description": "Small online craft store selling handmade jewellery and home decor. Average order value around $45.",
            "customer_description": "Women 25-45 who value handmade and unique items. Very price-aware on shipping -- often compare total cost including delivery.",
            "location": "Portland, USA",
            "location_country": "US",
            "years_open": "1-3",
            "business_role": "treat",
            "visit_frequency": "occasional",
            "customer_value_drivers": ["specific_product", "quality"],
            "regular_proportion": "handful",
            "area_demographics": ["residential"],
            "competitor_count": "six_plus",
        },
        "question": "Should we offer free shipping on orders over $35, or keep our current flat $5 shipping rate?",
        "variant_a": "Free shipping on orders over $35",
        "variant_b": "Keep flat $5 shipping on all orders",
        "expected_winner": "A",
    },
    {
        "id": 5,
        "name": "Obama Campaign -- Button Text",
        "source": "Optimizely case study / Dan Siroker",
        "real_winner": "learn_more",
        "real_outcome": "'Learn More' outperformed 'Sign Up' by 18.6%",
        "holdout": False,
        "survey": {
            "name": "The Weekly Brew",
            "type": "cafe",
            "description": "Neighbourhood coffee shop with a weekly newsletter about coffee origins and brewing tips.",
            "customer_description": "Coffee enthusiasts aged 25-40, mix of regulars and curious newcomers. Many visit the website before their first visit.",
            "location": "Austin, USA",
            "location_country": "US",
            "years_open": "1-3",
            "business_role": "treat",
            "visit_frequency": "weekly",
            "customer_value_drivers": ["specific_product", "atmosphere"],
            "regular_proportion": "solid_base",
            "area_demographics": ["residential", "student"],
            "competitor_count": "three_five",
        },
        "question": "On our website, should the main button say 'Sign Up for Updates' or 'Learn More About Us'?",
        "variant_a": "Sign Up for Updates",
        "variant_b": "Learn More About Us",
        "expected_winner": "B",
    },
    {
        "id": 6,
        "name": "Airbnb -- Professional Photography",
        "source": "First Round Review / Airbnb growth team",
        "real_winner": "professional_photos",
        "real_outcome": "Listings with professional photos got 2-3x more bookings",
        "holdout": False,
        "survey": {
            "name": "Casa del Sol",
            "type": "hotel",
            "description": "Small vacation rental apartment in a coastal Spanish town. 2 bedrooms, sea view, listed on Airbnb and Booking.com.",
            "customer_description": "Couples and small families looking for a holiday rental. Book 2-3 months ahead, compare photos heavily before booking.",
            "location": "Malaga, Spain",
            "location_country": "ES",
            "years_open": "1-3",
            "business_role": "destination",
            "visit_frequency": "occasional",
            "customer_value_drivers": ["atmosphere", "value"],
            "area_demographics": ["tourist"],
            "competitor_count": "six_plus",
        },
        "question": "Should I invest in professional photos for my rental listing, or are my phone photos good enough?",
        "variant_a": None,
        "variant_b": None,
        "expected_winner": "positive",
    },
    {
        "id": 7,
        "name": "Amazon -- One-Click Checkout",
        "source": "Brad Stone's The Everything Store",
        "real_winner": "one_click",
        "real_outcome": "One-click massively increased purchase completion rates",
        "holdout": False,
        "survey": {
            "name": "The Gadget Shop",
            "type": "electronics",
            "description": "Small online electronics store selling phone accessories, chargers, and small gadgets. Average order under $30.",
            "customer_description": "Tech-savvy 20-35 year olds who buy impulsively when they see something they want. Very impatient with slow checkouts.",
            "location": "Berlin, Germany",
            "location_country": "DE",
            "years_open": "1-3",
            "business_role": "convenience",
            "visit_frequency": "monthly",
            "customer_value_drivers": ["convenience", "value"],
            "regular_proportion": "handful",
            "area_demographics": ["residential", "student"],
            "competitor_count": "six_plus",
        },
        "question": "Should we let returning customers buy with a single click using saved payment info, or keep our current 3-step checkout?",
        "variant_a": "One-click checkout for returning customers",
        "variant_b": "Keep 3-step checkout process",
        "expected_winner": "A",
    },
    # Holdout cases (8, 9, 10) -- we DO run them but don't tune prompts against them
    {
        "id": 8,
        "name": "Basecamp -- Long-Form Landing Page",
        "source": "Signal v. Noise blog",
        "real_winner": "long_form",
        "real_outcome": "Long-form page increased signups by 37.5%",
        "holdout": True,
        "survey": {
            "name": "TaskFlow",
            "type": "other",
            "description": "Small project management SaaS for freelancers and small teams. Monthly subscription, free trial available.",
            "customer_description": "Freelancers and small agency owners who need to organize projects. Usually try 2-3 tools before committing.",
            "location": "Toronto, Canada",
            "location_country": "CA",
            "years_open": "<1",
            "business_role": "daily_need",
            "visit_frequency": "daily",
            "customer_value_drivers": ["convenience", "quality"],
            "area_demographics": ["business"],
            "competitor_count": "six_plus",
        },
        "question": "Should our main page be a short clean design with just our tagline and a 'Get Started' button, or a longer page that explains what we do in detail?",
        "variant_a": "Short and minimal",
        "variant_b": "Long and detailed with feature explanations",
        "expected_winner": "B",
    },
    {
        "id": 9,
        "name": "Walmart -- Page Load Speed",
        "source": "Walmart Labs engineering blog",
        "real_winner": "faster",
        "real_outcome": "Every 1 second improvement = up to 2% more conversions",
        "holdout": True,
        "survey": {
            "name": "Craft Corner",
            "type": "other",
            "description": "Small e-commerce store selling craft supplies. Website is functional but slow, loads in about 5 seconds.",
            "customer_description": "Crafters aged 30-55, patient but increasingly expect fast websites from the Amazon era. Browse a lot before buying.",
            "location": "Manchester, UK",
            "location_country": "GB",
            "years_open": "3-10",
            "business_role": "destination",
            "visit_frequency": "monthly",
            "customer_value_drivers": ["specific_product", "value"],
            "regular_proportion": "solid_base",
            "area_demographics": ["residential"],
            "competitor_count": "three_five",
        },
        "question": "Our website takes 5 seconds to load. If we invested in making it load in 2 seconds, would customers buy more?",
        "variant_a": None,
        "variant_b": None,
        "expected_winner": "positive",
    },
    {
        "id": 10,
        "name": "Groove -- Personal vs Corporate Email",
        "source": "Groove HQ blog (Alex Turnbull)",
        "real_winner": "personal",
        "real_outcome": "Personal emails had 2x higher response rates",
        "holdout": True,
        "survey": {
            "name": "BrightDesk",
            "type": "other",
            "description": "Small customer support SaaS, 500 users. Sends onboarding emails to new signups.",
            "customer_description": "Small business owners who just signed up for a help desk tool. Evaluating during free trial, comparing with 2-3 alternatives.",
            "location": "San Francisco, USA",
            "location_country": "US",
            "years_open": "1-3",
            "business_role": "daily_need",
            "visit_frequency": "daily",
            "customer_value_drivers": ["convenience", "personal_touch"],
            "regular_proportion": "handful",
            "area_demographics": ["business"],
            "competitor_count": "six_plus",
        },
        "question": "Should our customer emails come from me personally (casual tone, my name) or from the company (professional tone, company name)?",
        "variant_a": "Personal tone from owner (Hi, it's Alex...)",
        "variant_b": "Professional corporate tone (Dear valued customer...)",
        "expected_winner": "A",
    },
]


def _score_prediction(case: dict, result: dict) -> dict:
    """Score whether our simulation predicted the right outcome.

    Returns dict with:
    - was_correct: bool
    - confidence: str (from simulation)
    - our_prediction: str (what we predicted)
    - real_outcome: str (what actually happened)
    - reasoning: str (why we scored this way)
    """
    expected = case["expected_winner"]
    summary = (result.get("summary", "") + " " + result.get("recommendation", "")).lower()
    winner = result.get("winner", "")

    # For A/B tests with variants
    if expected in ("A", "B"):
        if winner:
            our_prediction = winner.upper()
            was_correct = our_prediction == expected
            reasoning = f"Predicted winner: {our_prediction}, real winner: {expected}"
        else:
            # No explicit winner, infer from summary
            if expected == "A":
                was_correct = any(w in summary for w in ["option a", "first option", "recommend a", "variant a"])
            else:
                was_correct = any(w in summary for w in ["option b", "second option", "recommend b", "variant b"])
            our_prediction = "A" if any(w in summary for w in ["option a", "first"]) else "B"
            reasoning = f"Inferred from summary: {our_prediction}, real: {expected}"

    # For positive/negative outcome tests (no A/B)
    elif expected == "positive":
        positive_words = ["yes", "should", "recommend", "go ahead", "positive", "benefit", "worth", "invest"]
        negative_words = ["no", "avoid", "risky", "against", "negative", "not worth"]
        pos_count = sum(1 for w in positive_words if w in summary)
        neg_count = sum(1 for w in negative_words if w in summary)
        was_correct = pos_count > neg_count
        our_prediction = "positive" if was_correct else "negative"
        reasoning = f"Positive signals: {pos_count}, negative: {neg_count}"

    else:
        was_correct = False
        our_prediction = "unknown"
        reasoning = "Could not determine prediction"

    return {
        "was_correct": was_correct,
        "confidence": result.get("confidence_score", "unknown"),
        "our_prediction": our_prediction,
        "real_outcome": case["real_outcome"],
        "reasoning": reasoning,
    }


async def run_single_backtest(case: dict, persona_count: int = 15) -> dict:
    """Run a single backtest case through the full simulation pipeline."""
    start = time.monotonic()
    survey = case["survey"]

    # Build business snapshot
    business = BusinessSnapshot(
        name=survey["name"],
        type=survey["type"],
        description=survey["description"],
        customer_description=survey.get("customer_description"),
        location=survey.get("location"),
    )

    logger.info("Running backtest %d: %s", case["id"], case["name"])

    try:
        # Step 1: Generate personas (no context agents for backtesting -- pure survey data)
        personas = await generate_personas(business, persona_count)

        # Step 2: Interview all personas
        responses = await run_simulation(
            personas, business, case["question"],
            case.get("variant_a"), case.get("variant_b"),
        )

        # Step 3: Aggregate
        result = await aggregate_responses(
            business, case["question"], responses,
            case.get("variant_a"), case.get("variant_b"),
        )

        # Step 4: Impact estimate
        impact = estimate_impact(responses, case["question"])

        # Step 5: Caveats
        caveats = generate_caveats(
            business, case["question"], persona_count, len(responses),
            case.get("variant_a"), case.get("variant_b"),
        )

        # Step 6: Score prediction against reality
        score = _score_prediction(case, result)

        elapsed = time.monotonic() - start

        # Extract features for ML training
        extractor = FeatureExtractor()
        features = extractor.extract(survey)

        return {
            "case_id": case["id"],
            "case_name": case["name"],
            "holdout": case.get("holdout", False),
            "was_correct": score["was_correct"],
            "our_prediction": score["our_prediction"],
            "expected_winner": case["expected_winner"],
            "real_outcome": case["real_outcome"],
            "confidence": score["confidence"],
            "reasoning": score["reasoning"],
            "summary": result.get("summary", ""),
            "recommendation": result.get("recommendation", ""),
            "winner": result.get("winner"),
            "persona_count": len(personas),
            "response_count": len(responses),
            "caveat_count": len(caveats),
            "impact_decision": impact.decision,
            "elapsed_seconds": round(elapsed, 1),
            "features": features,
            "feature_names": extractor.feature_names,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        elapsed = time.monotonic() - start
        logger.error("Backtest %d failed: %s", case["id"], e)
        return {
            "case_id": case["id"],
            "case_name": case["name"],
            "holdout": case.get("holdout", False),
            "was_correct": None,
            "error": str(e),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def run_all_backtests(
    persona_count: int = 15,
    only_ids: list[int] = None,
) -> list[dict]:
    """Run all backtest cases and produce a scored report."""
    results = []

    for case in BACKTEST_CASES:
        if only_ids and case["id"] not in only_ids:
            continue

        result = await run_single_backtest(case, persona_count)
        results.append(result)

        # Save incrementally
        _save_results(results)

        # Print live progress
        status = "CORRECT" if result.get("was_correct") else "WRONG" if result.get("was_correct") is False else "ERROR"
        holdout = " [HOLDOUT]" if result.get("holdout") else ""
        print(f"  [{status}] {result['case_name']}{holdout} ({result.get('elapsed_seconds', 0)}s)")

    return results


def _save_results(results: list[dict]):
    """Save results to JSON (incremental)."""
    # Remove non-serializable items
    clean = []
    for r in results:
        c = {k: v for k, v in r.items() if k != "features"}
        clean.append(c)

    path = RESULTS_DIR / f"backtest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(clean, f, indent=2)


def print_report(results: list[dict]):
    """Print a human-readable backtest report."""
    scored = [r for r in results if r.get("was_correct") is not None]
    train_set = [r for r in scored if not r.get("holdout")]
    holdout_set = [r for r in scored if r.get("holdout")]

    train_correct = sum(1 for r in train_set if r["was_correct"])
    holdout_correct = sum(1 for r in holdout_set if r["was_correct"])

    print()
    print("=" * 60)
    print("BACKTEST REPORT")
    print("=" * 60)
    print()
    print(f"{'#':<4} {'Case':<40} {'Result':<10} {'Time':<8}")
    print("-" * 60)
    for r in results:
        if r.get("was_correct") is None:
            status = "ERROR"
        elif r["was_correct"]:
            status = "CORRECT"
        else:
            status = "WRONG"
        holdout = " *" if r.get("holdout") else ""
        print(f"{r['case_id']:<4} {r['case_name'][:38]:<40} {status:<10} {r.get('elapsed_seconds', 0):.0f}s{holdout}")

    print("-" * 60)
    if train_set:
        print(f"Training set accuracy: {train_correct}/{len(train_set)} ({train_correct/len(train_set)*100:.0f}%)")
    if holdout_set:
        print(f"Holdout set accuracy:  {holdout_correct}/{len(holdout_set)} ({holdout_correct/len(holdout_set)*100:.0f}%)")
    if scored:
        total_correct = train_correct + holdout_correct
        print(f"Overall accuracy:      {total_correct}/{len(scored)} ({total_correct/len(scored)*100:.0f}%)")
    print()
    print("* = holdout case (not used for prompt tuning)")
    print("=" * 60)


def get_training_data_from_results(results: list[dict]) -> tuple:
    """Extract ML training data from backtest results.

    Returns (X, y, feature_names) for training the calibration model.
    Only uses non-holdout cases.
    """
    import numpy as np

    train_results = [r for r in results
                     if r.get("was_correct") is not None
                     and not r.get("holdout")
                     and "features" in r]

    if not train_results:
        return np.array([]), np.array([]), []

    feature_names = train_results[0].get("feature_names", [])
    X = []
    y = []

    for r in train_results:
        feat = r["features"]
        vec = [feat.get(name, 0.0) for name in feature_names]
        X.append(vec)
        y.append(1 if r["was_correct"] else 0)

    return np.array(X), np.array(y), feature_names


# CLI entry point
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    only_ids = None
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        if idx + 1 < len(sys.argv):
            only_ids = [int(sys.argv[idx + 1])]

    persona_count = 15
    if "--personas" in sys.argv:
        idx = sys.argv.index("--personas")
        if idx + 1 < len(sys.argv):
            persona_count = int(sys.argv[idx + 1])

    print(f"Running backtests with {persona_count} personas per simulation...")
    print()

    results = asyncio.run(run_all_backtests(persona_count=persona_count, only_ids=only_ids))
    print_report(results)

"""Tests for backend.swarm.caveats -- caveat generator."""

from backend.swarm.caveats import (
    generate_caveats,
    _matches_any,
    RTM_TRIGGER_PATTERNS,
    NOVELTY_PATTERNS,
    ADHERENCE_PATTERNS,
    PRICE_PATTERNS,
    COMPETITION_PATTERNS,
    CHANNEL_PATTERNS,
)
from backend.models.business import BusinessSnapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _caveat_types(caveats):
    return [c.type for c in caveats]


def _make_business(description="A solid local business with great regulars.", customer_description="Loyal locals."):
    return BusinessSnapshot(
        name="Test Biz",
        type="cafe",
        description=description,
        customer_description=customer_description,
    )


# ---------------------------------------------------------------------------
# Baseline caveats (always present)
# ---------------------------------------------------------------------------

class TestBaselineCaveats:
    def test_always_includes_not_causation(self):
        caveats = generate_caveats(_make_business(), "Should I change the menu?", 15, 15)
        assert "not_causation" in _caveat_types(caveats)

    def test_always_includes_self_selection(self):
        caveats = generate_caveats(_make_business(), "Should I change the menu?", 15, 15)
        assert "self_selection" in _caveat_types(caveats)

    def test_always_includes_cherry_pick_note(self):
        caveats = generate_caveats(_make_business(), "Any question at all", 15, 15)
        assert "cherry_pick_note" in _caveat_types(caveats)

    def test_baseline_present_even_for_neutral_question(self):
        caveats = generate_caveats(_make_business(), "Tell me about our customers", 15, 15)
        types = _caveat_types(caveats)
        assert "not_causation" in types
        assert "self_selection" in types


# ---------------------------------------------------------------------------
# RTM detection
# ---------------------------------------------------------------------------

class TestRTMDetection:
    def test_sales_are_down(self):
        assert _matches_any("Our sales are down this quarter", RTM_TRIGGER_PATTERNS)

    def test_terrible_month(self):
        assert _matches_any("We had a terrible month", RTM_TRIGGER_PATTERNS)

    def test_churn_rate_is_up(self):
        assert _matches_any("Our churn is up significantly", RTM_TRIGGER_PATTERNS)

    def test_best_month_ever(self):
        assert _matches_any("We just had our best month ever", RTM_TRIGGER_PATTERNS)

    def test_neutral_no_match(self):
        assert not _matches_any("Should we add a new menu item?", RTM_TRIGGER_PATTERNS)

    def test_rtm_caveat_generated(self):
        caveats = generate_caveats(
            _make_business(), "Our sales are down, should we discount?", 15, 15
        )
        assert "rtm_warning" in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Novelty detection
# ---------------------------------------------------------------------------

class TestNoveltyDetection:
    def test_launch_new_app(self):
        assert _matches_any("Should we launch a new app?", NOVELTY_PATTERNS)

    def test_introduce_loyalty_program(self):
        assert _matches_any("We want to introduce a loyalty program", NOVELTY_PATTERNS)

    def test_launch_new_feature(self):
        assert _matches_any("Should we launch a new feature for dashboards?", NOVELTY_PATTERNS)

    def test_redesign(self):
        assert _matches_any("We are planning a redesign of the storefront", NOVELTY_PATTERNS)

    def test_neutral_no_match(self):
        assert not _matches_any("Should we raise prices 10%?", NOVELTY_PATTERNS)

    def test_novelty_caveat_generated(self):
        caveats = generate_caveats(
            _make_business(), "Should we launch a new loyalty program?", 15, 15
        )
        assert "novelty_effect" in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Adherence detection
# ---------------------------------------------------------------------------

class TestAdherenceDetection:
    def test_would_customers_use_loyalty_card(self):
        assert _matches_any("Would customers use a loyalty card?", ADHERENCE_PATTERNS)

    def test_would_they_subscribe(self):
        assert _matches_any("Would they subscribe to our newsletter?", ADHERENCE_PATTERNS)

    def test_free_trial(self):
        assert _matches_any("Should we offer a free trial?", ADHERENCE_PATTERNS)

    def test_referral_program(self):
        assert _matches_any("Would a referral program work?", ADHERENCE_PATTERNS)

    def test_neutral_no_match(self):
        assert not _matches_any("Should we paint the walls blue?", ADHERENCE_PATTERNS)

    def test_adherence_caveat_generated(self):
        caveats = generate_caveats(
            _make_business(), "Would customers sign up for our loyalty card?", 15, 15
        )
        assert "adherence_gap" in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Price change detection
# ---------------------------------------------------------------------------

class TestPriceDetection:
    def test_raise_prices_15_percent(self):
        assert _matches_any("Should we raise prices 15%?", PRICE_PATTERNS)

    def test_increase_subscription_price(self):
        assert _matches_any("What if we increase the subscription price?", PRICE_PATTERNS)

    def test_discount(self):
        assert _matches_any("Would a 20% discount bring in more customers?", PRICE_PATTERNS)

    def test_free_to_paid(self):
        assert _matches_any("Should we go from free to paid?", PRICE_PATTERNS)

    def test_neutral_no_match(self):
        assert not _matches_any("Should we change our opening hours?", PRICE_PATTERNS)

    def test_price_caveat_generated(self):
        caveats = generate_caveats(
            _make_business(), "What if we raise prices 15%?", 15, 15
        )
        assert "price_sensitivity" in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Competition detection
# ---------------------------------------------------------------------------

class TestCompetitionDetection:
    def test_competitor_launched(self):
        assert _matches_any("A competitor launched a similar product", COMPETITION_PATTERNS)

    def test_losing_customers_to_rival(self):
        assert _matches_any("We are losing customers to a rival cafe", COMPETITION_PATTERNS)

    def test_new_entrant(self):
        assert _matches_any("A new entrant just opened across the street", COMPETITION_PATTERNS)

    def test_neutral_no_match(self):
        assert not _matches_any("Should we add avocado toast?", COMPETITION_PATTERNS)

    def test_competition_caveat_generated(self):
        caveats = generate_caveats(
            _make_business(), "A competitor launched a delivery service, should we match them?", 15, 15
        )
        assert "competitive_context" in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Channel detection
# ---------------------------------------------------------------------------

class TestChannelDetection:
    def test_start_selling_online(self):
        assert _matches_any("Should we open an online store?", CHANNEL_PATTERNS)

    def test_add_delivery_service(self):
        assert _matches_any("Should we add a delivery service?", CHANNEL_PATTERNS)

    def test_marketplace(self):
        assert _matches_any("Should we list on uber eats?", CHANNEL_PATTERNS)

    def test_neutral_no_match(self):
        assert not _matches_any("Should we hire a new barista?", CHANNEL_PATTERNS)

    def test_channel_caveat_generated(self):
        caveats = generate_caveats(
            _make_business(), "Should we open an online store?", 15, 15
        )
        assert "channel_adoption" in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Small sample and high failure rate
# ---------------------------------------------------------------------------

class TestSampleCaveats:
    def test_small_sample_when_under_12(self):
        caveats = generate_caveats(_make_business(), "Any question", 10, 10)
        assert "small_sample" in _caveat_types(caveats)

    def test_no_small_sample_when_15(self):
        caveats = generate_caveats(_make_business(), "Any question", 15, 15)
        assert "small_sample" not in _caveat_types(caveats)

    def test_high_failure_rate(self):
        # 6 out of 15 succeeded = 40% success = 60% failure > 20% threshold
        caveats = generate_caveats(_make_business(), "Any question", 15, 6)
        assert "high_failure_rate" in _caveat_types(caveats)

    def test_no_failure_caveat_when_all_succeed(self):
        caveats = generate_caveats(_make_business(), "Any question", 15, 15)
        assert "high_failure_rate" not in _caveat_types(caveats)


# ---------------------------------------------------------------------------
# Profile quality
# ---------------------------------------------------------------------------

class TestProfileQuality:
    def test_short_description_triggers_caveat(self):
        biz = _make_business(description="A cafe.", customer_description="People.")
        caveats = generate_caveats(biz, "Any question", 15, 15)
        assert "profile_quality" in _caveat_types(caveats)

    def test_long_description_no_caveat(self):
        biz = _make_business(
            description="A neighborhood cafe in Portland serving specialty coffee and pastries to local workers.",
            customer_description="Young professionals and remote workers within walking distance.",
        )
        caveats = generate_caveats(biz, "Any question", 15, 15)
        assert "profile_quality" not in _caveat_types(caveats)

"""Tests for backend.impact.estimator -- mappings, models, and pure functions."""

from backend.impact.estimator import (
    BUSINESS_TYPE_TO_MODEL,
    REVENUE_MODELS,
    SWITCHING_COST_RETENTION_FLOOR,
    ENGAGEMENT_ASYMMETRY,
    DEFAULT_REVENUE_MODEL,
    _detect_revenue_model,
    _sentiment_to_retention,
    _sentiment_to_engagement_change,
    _sentiment_to_visit_change,
    _detect_impact_type,
)


# ---------------------------------------------------------------------------
# BUSINESS_TYPE_TO_MODEL mapping
# ---------------------------------------------------------------------------

class TestBusinessTypeToModel:
    def test_restaurant_is_per_visit(self):
        assert BUSINESS_TYPE_TO_MODEL["restaurant"] == "per_visit"

    def test_saas_is_subscription(self):
        assert BUSINESS_TYPE_TO_MODEL["saas"] == "subscription"

    def test_consulting_is_contract(self):
        assert BUSINESS_TYPE_TO_MODEL["consulting"] == "contract"

    def test_ecommerce_is_ecommerce(self):
        assert BUSINESS_TYPE_TO_MODEL["ecommerce"] == "ecommerce"

    def test_salon_is_per_session(self):
        assert BUSINESS_TYPE_TO_MODEL["salon"] == "per_session"

    def test_coworking_is_membership(self):
        assert BUSINESS_TYPE_TO_MODEL["coworking"] == "membership"

    def test_freelance_is_project(self):
        assert BUSINESS_TYPE_TO_MODEL["freelance"] == "project"

    def test_all_values_are_valid_revenue_models(self):
        for biz_type, model in BUSINESS_TYPE_TO_MODEL.items():
            assert model in REVENUE_MODELS, f"{biz_type} maps to unknown model {model}"


# ---------------------------------------------------------------------------
# REVENUE_MODELS structure
# ---------------------------------------------------------------------------

class TestRevenueModels:
    def test_all_models_have_required_keys(self):
        required = {"label", "formula", "switching_cost", "engagement_metric", "description"}
        for model_key, model in REVENUE_MODELS.items():
            missing = required - set(model.keys())
            assert not missing, f"Model '{model_key}' missing keys: {missing}"

    def test_switching_costs_are_valid(self):
        valid = {"low", "medium", "high"}
        for model_key, model in REVENUE_MODELS.items():
            assert model["switching_cost"] in valid, f"{model_key} has invalid switching_cost"

    def test_seven_models_exist(self):
        assert len(REVENUE_MODELS) == 7


# ---------------------------------------------------------------------------
# SWITCHING_COST_RETENTION_FLOOR
# ---------------------------------------------------------------------------

class TestSwitchingCostRetentionFloor:
    def test_low_is_lowest_floor(self):
        assert SWITCHING_COST_RETENTION_FLOOR["low"] < SWITCHING_COST_RETENTION_FLOOR["medium"]

    def test_high_is_highest_floor(self):
        assert SWITCHING_COST_RETENTION_FLOOR["high"] > SWITCHING_COST_RETENTION_FLOOR["medium"]

    def test_all_floors_between_0_and_1(self):
        for level, floor in SWITCHING_COST_RETENTION_FLOOR.items():
            assert 0 < floor < 1, f"{level} floor {floor} not in (0, 1)"


# ---------------------------------------------------------------------------
# ENGAGEMENT_ASYMMETRY
# ---------------------------------------------------------------------------

class TestEngagementAsymmetry:
    def test_all_revenue_models_have_asymmetry(self):
        for model_key in REVENUE_MODELS:
            assert model_key in ENGAGEMENT_ASYMMETRY, f"Missing asymmetry for {model_key}"

    def test_negative_multiplier_exceeds_positive_cap(self):
        """Negative sentiment should reduce engagement more than positive increases it."""
        for model_key, params in ENGAGEMENT_ASYMMETRY.items():
            assert params["negative_multiplier"] > params["positive_cap"], (
                f"{model_key}: negative_multiplier should exceed positive_cap"
            )

    def test_ecommerce_most_elastic(self):
        ecom = ENGAGEMENT_ASYMMETRY["ecommerce"]
        contract = ENGAGEMENT_ASYMMETRY["contract"]
        assert ecom["negative_multiplier"] > contract["negative_multiplier"]


# ---------------------------------------------------------------------------
# _detect_revenue_model
# ---------------------------------------------------------------------------

class TestDetectRevenueModel:
    def test_exact_match(self):
        assert _detect_revenue_model("restaurant") == "per_visit"

    def test_normalized_match(self):
        assert _detect_revenue_model("Hair Salon") == "per_session"

    def test_unknown_returns_default(self):
        # "alien_spaceship" partially matches "ship" in some keys, so use truly unknown
        assert _detect_revenue_model("zzz_totally_unknown_zzz") == DEFAULT_REVENUE_MODEL

    def test_none_returns_default(self):
        assert _detect_revenue_model(None) == DEFAULT_REVENUE_MODEL

    def test_empty_returns_default(self):
        assert _detect_revenue_model("") == DEFAULT_REVENUE_MODEL


# ---------------------------------------------------------------------------
# _sentiment_to_retention
# ---------------------------------------------------------------------------

class TestSentimentToRetention:
    def test_positive_sentiment_high_retention(self):
        ret = _sentiment_to_retention(0.5, switching_cost="low")
        assert ret > 0.90

    def test_neutral_sentiment_high_retention(self):
        ret = _sentiment_to_retention(0.0, switching_cost="low")
        assert ret > 0.85

    def test_negative_sentiment_lower_retention(self):
        ret_neg = _sentiment_to_retention(-0.8, switching_cost="low")
        ret_pos = _sentiment_to_retention(0.5, switching_cost="low")
        assert ret_neg < ret_pos

    def test_high_switching_cost_raises_floor(self):
        ret_low = _sentiment_to_retention(-1.0, switching_cost="low")
        ret_high = _sentiment_to_retention(-1.0, switching_cost="high")
        assert ret_high > ret_low

    def test_never_exceeds_ceiling(self):
        ret = _sentiment_to_retention(1.0, switching_cost="high")
        assert ret <= 0.98

    def test_never_below_floor(self):
        ret = _sentiment_to_retention(-1.0, switching_cost="low")
        assert ret >= SWITCHING_COST_RETENTION_FLOOR["low"]


# ---------------------------------------------------------------------------
# _sentiment_to_engagement_change
# ---------------------------------------------------------------------------

class TestSentimentToEngagementChange:
    def test_positive_sentiment_positive_change(self):
        change = _sentiment_to_engagement_change(0.5, "per_visit")
        assert change > 0

    def test_negative_sentiment_negative_change(self):
        change = _sentiment_to_engagement_change(-0.5, "per_visit")
        assert change < 0

    def test_neutral_sentiment_zero_change(self):
        change = _sentiment_to_engagement_change(0.0, "per_visit")
        assert change == 0.0

    def test_asymmetry_negative_bigger_magnitude(self):
        pos = _sentiment_to_engagement_change(0.5, "per_visit")
        neg = _sentiment_to_engagement_change(-0.5, "per_visit")
        assert abs(neg) > abs(pos)

    def test_backward_compat_alias(self):
        direct = _sentiment_to_engagement_change(0.3, "per_visit")
        alias = _sentiment_to_visit_change(0.3)
        assert direct == alias


# ---------------------------------------------------------------------------
# _detect_impact_type
# ---------------------------------------------------------------------------

class TestDetectImpactType:
    def test_price_question(self):
        impact_type, _ = _detect_impact_type("Should we raise the price?")
        assert impact_type == "revenue"

    def test_feature_question(self):
        impact_type, _ = _detect_impact_type("Would customers use a new feature?")
        assert impact_type == "adoption"

    def test_satisfaction_question(self):
        impact_type, _ = _detect_impact_type("Should we renovate the dining area?")
        assert impact_type == "satisfaction"

    def test_retention_question(self):
        impact_type, _ = _detect_impact_type("How do we keep customers from leaving?")
        assert impact_type == "retention"

    def test_operational_question(self):
        impact_type, _ = _detect_impact_type("Should we open on Sundays?")
        assert impact_type == "engagement"

    def test_generic_question(self):
        impact_type, _ = _detect_impact_type("What do customers think about us?")
        assert impact_type == "engagement"  # default fallback

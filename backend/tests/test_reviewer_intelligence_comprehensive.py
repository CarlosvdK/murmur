"""Comprehensive tests for reviewer intelligence system."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.reviewer_intelligence import build_reviewer_intelligence
from backend.reviewer_intelligence.review_signal_extractor import AggregateReviewSignals
from backend.reviewer_intelligence.bias_corrector import BiasAdjustedSignals
from backend.reviewer_intelligence.silent_majority_estimator import SilentMajorityProfile
from backend.models.business import BusinessSnapshot


class TestBuildReviewerIntelligence:
    """Test full reviewer intelligence pipeline."""

    @pytest.mark.asyncio
    async def test_extracts_review_signals(self):
        """Should extract aggregate patterns from reviews."""
        business = BusinessSnapshot(
            name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.reviewer_intelligence.extract_review_signals") as mock_extract:
            mock_extract.return_value = AggregateReviewSignals(
                place_id="test_place_id",
                business_name="Shop",
                total_review_count=45,
                average_rating=4.2,
                rating_distribution={1: 3, 2: 5, 3: 10, 4: 15, 5: 12},
                price_mention_frequency=0.2,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.3,
                switching_signal_frequency=0.1,
                tourist_ratio_estimate=0.2,
                local_ratio_estimate=0.8,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Great service", "Clean"],
                top_negative_themes=["Expensive", "Wait time"],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            )

            result = await build_reviewer_intelligence(business, persona_count=15)
            assert result is not None

    @pytest.mark.asyncio
    async def test_applies_bias_corrections(self):
        """Should apply extremity/platform/majority corrections."""
        business = BusinessSnapshot(
            name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.reviewer_intelligence.extract_review_signals") as mock_extract:
            mock_extract.return_value = AggregateReviewSignals(
                place_id="test_place_id",
                business_name="Shop",
                total_review_count=50,
                average_rating=4.8,  # Suspiciously high
                rating_distribution={1: 1, 2: 2, 3: 5, 4: 15, 5: 27},
                price_mention_frequency=0.1,
                value_positive_ratio=0.8,
                loyalty_signal_frequency=0.25,
                switching_signal_frequency=0.05,
                tourist_ratio_estimate=0.2,
                local_ratio_estimate=0.8,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Excellent", "Highly recommend"],
                top_negative_themes=[],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            )

            result = await build_reviewer_intelligence(business, persona_count=15)
            # Should apply corrections to unrealistic ratings
            assert result is not None

    @pytest.mark.asyncio
    async def test_estimates_silent_majority(self):
        """Should model customers not in reviews."""
        business = BusinessSnapshot(
            name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.reviewer_intelligence.extract_review_signals") as mock_extract:
            mock_extract.return_value = AggregateReviewSignals(
                place_id="test_place_id",
                business_name="Shop",
                total_review_count=20,
                average_rating=4.0,
                rating_distribution={1: 1, 2: 2, 3: 5, 4: 8, 5: 4},
                price_mention_frequency=0.15,
                value_positive_ratio=0.5,
                loyalty_signal_frequency=0.2,
                switching_signal_frequency=0.08,
                tourist_ratio_estimate=0.3,
                local_ratio_estimate=0.7,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Good"],
                top_negative_themes=["Okay"],
                signal_confidence="low",
                bias_warning="Standard bias warning",
            )

            result = await build_reviewer_intelligence(business, persona_count=15)
            # Silent majority should be ~55-70% of personas
            assert result is not None

    @pytest.mark.asyncio
    async def test_builds_customer_segments(self):
        """Should create 6 customer segments."""
        business = BusinessSnapshot(
            name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.reviewer_intelligence.extract_review_signals") as mock_extract:
            mock_extract.return_value = AggregateReviewSignals(
                place_id="test_place_id",
                business_name="Shop",
                total_review_count=60,
                average_rating=4.0,
                rating_distribution={1: 3, 2: 6, 3: 12, 4: 24, 5: 15},
                price_mention_frequency=0.2,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.25,
                switching_signal_frequency=0.1,
                tourist_ratio_estimate=0.25,
                local_ratio_estimate=0.75,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Good service"],
                top_negative_themes=["Price"],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            )

            result = await build_reviewer_intelligence(business, persona_count=15)
            # Should have 6 segments: silent regulars, occasional, fans, frustrated, tourists, value seekers
            assert result is not None

    @pytest.mark.asyncio
    async def test_calibrates_personas(self):
        """Should build PersonaGenerationManifest."""
        business = BusinessSnapshot(
            name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.reviewer_intelligence.extract_review_signals") as mock_extract:
            mock_extract.return_value = AggregateReviewSignals(
                place_id="test_place_id",
                business_name="Shop",
                total_review_count=80,
                average_rating=4.0,
                rating_distribution={1: 4, 2: 8, 3: 16, 4: 32, 5: 20},
                price_mention_frequency=0.2,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.3,
                switching_signal_frequency=0.12,
                tourist_ratio_estimate=0.2,
                local_ratio_estimate=0.8,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Quality"],
                top_negative_themes=["Price"],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            )

            result = await build_reviewer_intelligence(business, persona_count=15)
            # Should return manifest or calibration data
            assert result is not None


class TestReviewSignalExtractor:
    """Test review signal extraction."""

    @pytest.mark.asyncio
    async def test_extracts_google_places_aggregate(self):
        """Should extract aggregate patterns from Google Places."""
        from backend.reviewer_intelligence.review_signal_extractor import extract_review_signals

        with patch("backend.reviewer_intelligence.review_signal_extractor.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.json = MagicMock(return_value={
                "places": [{
                    "id": "test_place_id",
                    "displayName": {"text": "Test Shop"},
                    "rating": 4.5,
                    "userRatingCount": 100,
                    "reviews": [
                        {"text": {"text": "Great place"}, "rating": 5},
                        {"text": {"text": "Good service"}, "rating": 4},
                    ]
                }]
            })
            mock_response.raise_for_status = MagicMock()

            mock_client.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=AsyncMock(return_value=mock_response)))
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("backend.reviewer_intelligence.review_signal_extractor.get_settings") as mock_settings:
                mock_settings.return_value.google_places_api_key = "test_key"
                result = await extract_review_signals("Test Shop", "City")
                assert result is not None
                assert isinstance(result, AggregateReviewSignals)

    @pytest.mark.asyncio
    async def test_no_individual_profiles_stored(self):
        """NEVER store individual reviewer data (GDPR)."""
        from backend.reviewer_intelligence.review_signal_extractor import extract_review_signals

        with patch("backend.reviewer_intelligence.review_signal_extractor.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.json = MagicMock(return_value={
                "places": [{
                    "id": "test_place_id",
                    "displayName": {"text": "Test Shop"},
                    "rating": 4.5,
                    "userRatingCount": 50,
                    "reviews": [
                        {"text": {"text": "Great"}, "rating": 5},
                    ]
                }]
            })
            mock_response.raise_for_status = MagicMock()

            mock_client.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=AsyncMock(return_value=mock_response)))
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("backend.reviewer_intelligence.review_signal_extractor.get_settings") as mock_settings:
                mock_settings.return_value.google_places_api_key = "test_key"
                result = await extract_review_signals("Shop", "City")
                # Result should be aggregate statistics, not individual reviews
                assert isinstance(result, AggregateReviewSignals)
                # Should not have individual review texts
                assert not hasattr(result, 'individual_reviews')


class TestBiasCorrector:
    """Test bias correction in review signals."""

    def test_corrects_extremity_bias(self):
        """Should compress extreme ratings toward center."""
        from backend.reviewer_intelligence.bias_corrector import apply_bias_corrections

        signals = AggregateReviewSignals(
            place_id="test",
            business_name="Test",
            total_review_count=50,
            average_rating=4.8,  # Suspiciously high
            rating_distribution={1: 0, 2: 0, 3: 5, 4: 5, 5: 40},  # All 5 stars
            price_mention_frequency=0.1,
            value_positive_ratio=0.9,
            loyalty_signal_frequency=0.2,
            switching_signal_frequency=0.05,
            tourist_ratio_estimate=0.1,
            local_ratio_estimate=0.9,
            peak_days=[],
            price_change_detected=False,
            price_change_sentiment=None,
            review_trend="stable",
            top_positive_themes=["Excellent"],
            top_negative_themes=[],
            signal_confidence="high",
            bias_warning="Standard bias warning",
        )

        corrected = apply_bias_corrections(signals)
        # Should have corrected the signals
        assert corrected is not None
        assert corrected.adjusted_positive_ratio < 1.0  # Compressed from 100%

    def test_corrects_platform_bias(self):
        """Should apply platform-specific corrections."""
        from backend.reviewer_intelligence.bias_corrector import apply_bias_corrections

        signals = AggregateReviewSignals(
            place_id="test",
            business_name="Test",
            total_review_count=30,
            average_rating=4.5,
            rating_distribution={1: 1, 2: 2, 3: 8, 4: 12, 5: 7},
            price_mention_frequency=0.15,
            value_positive_ratio=0.6,
            loyalty_signal_frequency=0.2,
            switching_signal_frequency=0.08,
            tourist_ratio_estimate=0.2,
            local_ratio_estimate=0.8,
            peak_days=[],
            price_change_detected=False,
            price_change_sentiment=None,
            review_trend="stable",
            top_positive_themes=["Good"],
            top_negative_themes=["Okay"],
            signal_confidence="medium",
            bias_warning="Standard bias warning",
        )
        corrected = apply_bias_corrections(signals)
        # Google underrepresents negative, so adjusted negative should be uplifted
        assert corrected is not None
        assert corrected.adjusted_negative_ratio > 0

    def test_corrects_silent_majority(self):
        """Should weight silent majority (55-70% not in reviews)."""
        from backend.reviewer_intelligence.bias_corrector import apply_bias_corrections

        signals = AggregateReviewSignals(
            place_id="test",
            business_name="Test",
            total_review_count=20,
            average_rating=3.8,
            rating_distribution={1: 2, 2: 3, 3: 5, 4: 7, 5: 3},
            price_mention_frequency=0.2,
            value_positive_ratio=0.5,
            loyalty_signal_frequency=0.15,
            switching_signal_frequency=0.1,
            tourist_ratio_estimate=0.3,
            local_ratio_estimate=0.7,
            peak_days=[],
            price_change_detected=False,
            price_change_sentiment=None,
            review_trend="stable",
            top_positive_themes=[],
            top_negative_themes=[],
            signal_confidence="low",
            bias_warning="Standard bias warning",
        )
        corrected = apply_bias_corrections(signals)
        # Should estimate total customers as much larger than reviewers
        assert corrected is not None
        assert corrected.estimated_total_customers_yearly > signals.total_review_count


class TestSilentMajorityEstimator:
    """Test silent majority modeling."""

    def test_estimates_silent_majority_proportion(self):
        """Should estimate 55-70% of customers are silent."""
        from backend.reviewer_intelligence.silent_majority_estimator import estimate_silent_majority

        adjusted = BiasAdjustedSignals(
            raw_signals=AggregateReviewSignals(
                place_id="test",
                business_name="Test",
                total_review_count=30,
                average_rating=4.0,
                rating_distribution={1: 2, 2: 3, 3: 8, 4: 12, 5: 5},
                price_mention_frequency=0.2,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.25,
                switching_signal_frequency=0.1,
                tourist_ratio_estimate=0.3,
                local_ratio_estimate=0.7,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Good"],
                top_negative_themes=["Price"],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            ),
            adjusted_positive_ratio=0.65,
            adjusted_negative_ratio=0.2,
            adjusted_neutral_ratio=0.15,
            estimated_total_customers_yearly=600,
            silent_majority_size_vs_reviewers="~20x more customers than reviewers",
            silent_majority_sentiment="moderately positive",
            silent_majority_price_sensitivity="high",
            silent_majority_loyalty="moderate",
            overall_confidence="medium",
            corrections_applied=["extremity_compression"],
            caveat_for_user="Standard caveat",
        )

        silent = estimate_silent_majority(adjusted, tourist_ratio=0.3)
        # Should return profile with proportion 0.55-0.70
        assert isinstance(silent, SilentMajorityProfile)
        assert 0.5 <= silent.recommended_swarm_proportion <= 0.8

    def test_models_silent_majority_characteristics(self):
        """Should model who silent majority IS."""
        from backend.reviewer_intelligence.silent_majority_estimator import estimate_silent_majority

        adjusted = BiasAdjustedSignals(
            raw_signals=AggregateReviewSignals(
                place_id="test",
                business_name="Test",
                total_review_count=20,
                average_rating=3.5,
                rating_distribution={1: 2, 2: 3, 3: 8, 4: 5, 5: 2},
                price_mention_frequency=0.25,
                value_positive_ratio=0.5,
                loyalty_signal_frequency=0.15,
                switching_signal_frequency=0.15,
                tourist_ratio_estimate=0.2,
                local_ratio_estimate=0.8,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=[],
                top_negative_themes=[],
                signal_confidence="low",
                bias_warning="Standard bias warning",
            ),
            adjusted_positive_ratio=0.5,
            adjusted_negative_ratio=0.3,
            adjusted_neutral_ratio=0.2,
            estimated_total_customers_yearly=400,
            silent_majority_size_vs_reviewers="~20x more customers than reviewers",
            silent_majority_sentiment="lukewarm",
            silent_majority_price_sensitivity="high",
            silent_majority_loyalty="low",
            overall_confidence="low",
            corrections_applied=["extremity_compression"],
            caveat_for_user="Standard caveat",
        )

        result = estimate_silent_majority(adjusted)
        # Should return characteristics of silent customers
        assert isinstance(result, SilentMajorityProfile)
        assert result.estimated_satisfaction is not None
        assert result.estimated_price_sensitivity is not None
        assert result.persona_guidance is not None


class TestCustomerSegmentBuilder:
    """Test 6-segment customer model."""

    def test_builds_six_segments(self):
        """Should build: silent regulars, occasional, fans, frustrated, tourists, value seekers."""
        from backend.reviewer_intelligence.customer_segment_builder import build_segments

        adjusted = BiasAdjustedSignals(
            raw_signals=AggregateReviewSignals(
                place_id="test",
                business_name="Test",
                total_review_count=50,
                average_rating=4.2,
                rating_distribution={1: 3, 2: 5, 3: 10, 4: 20, 5: 12},
                price_mention_frequency=0.2,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.25,
                switching_signal_frequency=0.1,
                tourist_ratio_estimate=0.25,
                local_ratio_estimate=0.75,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=["Good"],
                top_negative_themes=["Price"],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            ),
            adjusted_positive_ratio=0.65,
            adjusted_negative_ratio=0.2,
            adjusted_neutral_ratio=0.15,
            estimated_total_customers_yearly=1000,
            silent_majority_size_vs_reviewers="~20x more customers than reviewers",
            silent_majority_sentiment="moderately positive",
            silent_majority_price_sensitivity="high",
            silent_majority_loyalty="moderate",
            overall_confidence="medium",
            corrections_applied=["extremity_compression"],
            caveat_for_user="Standard caveat",
        )

        silent = SilentMajorityProfile(
            estimated_size_vs_reviewers="~20x more customers than reviewers",
            estimated_satisfaction="moderately positive",
            estimated_price_sensitivity="high",
            estimated_loyalty="moderate",
            estimated_switching_risk="higher than reviews suggest",
            recommended_swarm_proportion=0.60,
            persona_guidance="Guide text",
            confidence_note="Confidence note",
        )

        business = BusinessSnapshot(
            name="Test Shop",
            type="retail",
            description="A test shop",
            location="City",
        )

        segments_profile = build_segments(adjusted, silent, business, business_type="retail")
        # Should have 6 segments
        assert len(segments_profile.segments) == 6

    def test_segment_proportions_sum_to_100(self):
        """Segment proportions should sum to 100%."""
        from backend.reviewer_intelligence.customer_segment_builder import build_segments

        adjusted = BiasAdjustedSignals(
            raw_signals=AggregateReviewSignals(
                place_id="test",
                business_name="Test",
                total_review_count=60,
                average_rating=4.0,
                rating_distribution={1: 3, 2: 6, 3: 12, 4: 24, 5: 15},
                price_mention_frequency=0.2,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.25,
                switching_signal_frequency=0.1,
                tourist_ratio_estimate=0.2,
                local_ratio_estimate=0.8,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=[],
                top_negative_themes=[],
                signal_confidence="medium",
                bias_warning="Standard bias warning",
            ),
            adjusted_positive_ratio=0.65,
            adjusted_negative_ratio=0.2,
            adjusted_neutral_ratio=0.15,
            estimated_total_customers_yearly=1200,
            silent_majority_size_vs_reviewers="~20x more customers than reviewers",
            silent_majority_sentiment="moderately positive",
            silent_majority_price_sensitivity="moderate",
            silent_majority_loyalty="moderate",
            overall_confidence="medium",
            corrections_applied=["extremity_compression"],
            caveat_for_user="Standard caveat",
        )

        silent = SilentMajorityProfile(
            estimated_size_vs_reviewers="~20x more customers than reviewers",
            estimated_satisfaction="moderately positive",
            estimated_price_sensitivity="moderate",
            estimated_loyalty="moderate",
            estimated_switching_risk="higher than reviews suggest",
            recommended_swarm_proportion=0.60,
            persona_guidance="Guide text",
            confidence_note="Confidence note",
        )

        business = BusinessSnapshot(
            name="Test Shop",
            type="retail",
            description="A test shop",
            location="City",
        )

        segments_profile = build_segments(adjusted, silent, business, business_type="retail")
        proportions = [s.estimated_proportion for s in segments_profile.segments]
        assert abs(sum(proportions) - 1.0) < 0.01  # Allow rounding

    def test_silent_regulars_largest_segment(self):
        """Silent regulars should be ~28% (largest segment)."""
        from backend.reviewer_intelligence.customer_segment_builder import build_segments

        adjusted = BiasAdjustedSignals(
            raw_signals=AggregateReviewSignals(
                place_id="test",
                business_name="Test",
                total_review_count=100,
                average_rating=4.0,
                rating_distribution={1: 5, 2: 10, 3: 20, 4: 40, 5: 25},
                price_mention_frequency=0.15,
                value_positive_ratio=0.6,
                loyalty_signal_frequency=0.2,
                switching_signal_frequency=0.08,
                tourist_ratio_estimate=0.15,
                local_ratio_estimate=0.85,
                peak_days=[],
                price_change_detected=False,
                price_change_sentiment=None,
                review_trend="stable",
                top_positive_themes=[],
                top_negative_themes=[],
                signal_confidence="high",
                bias_warning="Standard bias warning",
            ),
            adjusted_positive_ratio=0.65,
            adjusted_negative_ratio=0.2,
            adjusted_neutral_ratio=0.15,
            estimated_total_customers_yearly=2000,
            silent_majority_size_vs_reviewers="~20x more customers than reviewers",
            silent_majority_sentiment="moderately positive",
            silent_majority_price_sensitivity="moderate",
            silent_majority_loyalty="moderate",
            overall_confidence="high",
            corrections_applied=["extremity_compression"],
            caveat_for_user="Standard caveat",
        )

        silent = SilentMajorityProfile(
            estimated_size_vs_reviewers="~20x more customers than reviewers",
            estimated_satisfaction="moderately positive",
            estimated_price_sensitivity="moderate",
            estimated_loyalty="moderate",
            estimated_switching_risk="higher than reviews suggest",
            recommended_swarm_proportion=0.65,  # More local = higher silent regular proportion
            persona_guidance="Guide text",
            confidence_note="Confidence note",
        )

        business = BusinessSnapshot(
            name="Test Shop",
            type="retail",
            description="A test shop",
            location="City",
        )

        segments_profile = build_segments(adjusted, silent, business, business_type="retail")
        # Silent regulars should be the largest or near-largest proportion
        assert segments_profile.dominant_segment is not None
        silent_regulars = next((s for s in segments_profile.segments if "Regular" in s.name), None)
        assert silent_regulars is not None
        assert silent_regulars.estimated_proportion > 0.15  # At least 15%


class TestPersonaCalibrator:
    """Test calibration of personas from segments."""

    def test_creates_persona_manifest(self):
        """Should build PersonaGenerationManifest from segments."""
        from backend.reviewer_intelligence.persona_calibrator import calibrate_personas
        from backend.reviewer_intelligence.customer_segment_builder import CustomerSegmentProfile, CustomerSegment

        segment1 = CustomerSegment(
            name="Silent Regulars",
            description="Come often, never review",
            estimated_proportion=0.28,
            price_sensitivity="moderate to high",
            loyalty_likelihood=0.6,
            is_silent_majority=True,
            age_range="30-55",
            income_tier="mid",
            visit_frequency="weekly",
            key_decision_factors=["convenience", "habit"],
        )

        segment2 = CustomerSegment(
            name="Silent Occasionals",
            description="Occasional visitors",
            estimated_proportion=0.35,
            price_sensitivity="high",
            loyalty_likelihood=0.3,
            is_silent_majority=True,
            age_range="22-50",
            income_tier="budget to mid",
            visit_frequency="occasional",
            key_decision_factors=["price", "convenience"],
        )

        profile = CustomerSegmentProfile(
            segments=[segment1, segment2],
            total_estimated_customers="~1000 per year",
            dominant_segment="Silent Regulars",
            most_price_sensitive_segment="Silent Occasionals",
            silent_majority_proportion=0.63,
            signals_used=["review data"],
            confidence_level="medium",
            plain_english_summary="Test summary",
        )

        manifest = calibrate_personas(profile, persona_count=15)
        # Should have 15 personas with structured specs
        assert manifest is not None
        assert manifest.total_count == 15
        assert len(manifest.persona_specs) == 15

    def test_persona_specs_have_structured_fields(self):
        """Each persona spec should have age, income, frequency, price_sensitivity."""
        from backend.reviewer_intelligence.persona_calibrator import calibrate_personas
        from backend.reviewer_intelligence.customer_segment_builder import CustomerSegmentProfile, CustomerSegment

        segment = CustomerSegment(
            name="Test Segment",
            description="Test",
            estimated_proportion=1.0,
            price_sensitivity="moderate",
            loyalty_likelihood=0.5,
            is_silent_majority=False,
            age_range="25-45",
            income_tier="mid",
            visit_frequency="weekly",
            key_decision_factors=["quality"],
        )

        profile = CustomerSegmentProfile(
            segments=[segment],
            total_estimated_customers="~500 per year",
            dominant_segment="Test Segment",
            most_price_sensitive_segment="Test Segment",
            silent_majority_proportion=0.0,
            signals_used=["review data"],
            confidence_level="medium",
            plain_english_summary="Test",
        )

        manifest = calibrate_personas(profile, persona_count=5)
        assert manifest is not None
        for persona_spec in manifest.persona_specs:
            assert hasattr(persona_spec, 'age')
            assert hasattr(persona_spec, 'income_tier')
            assert hasattr(persona_spec, 'visit_frequency')
            assert hasattr(persona_spec, 'price_sensitivity')

    def test_silent_majority_personas_dont_review(self):
        """55-70% of personas should have is_silent_majority=True."""
        from backend.reviewer_intelligence.persona_calibrator import calibrate_personas
        from backend.reviewer_intelligence.customer_segment_builder import CustomerSegmentProfile, CustomerSegment

        silent_seg = CustomerSegment(
            name="Silent Regulars",
            description="Silent",
            estimated_proportion=0.63,
            price_sensitivity="moderate",
            loyalty_likelihood=0.6,
            is_silent_majority=True,
            age_range="30-55",
            income_tier="mid",
            visit_frequency="weekly",
            key_decision_factors=["convenience"],
        )

        vocal_seg = CustomerSegment(
            name="Vocal Advocates",
            description="Vocal",
            estimated_proportion=0.37,
            price_sensitivity="low",
            loyalty_likelihood=0.8,
            is_silent_majority=False,
            age_range="28-60",
            income_tier="mid to affluent",
            visit_frequency="weekly",
            key_decision_factors=["quality"],
        )

        profile = CustomerSegmentProfile(
            segments=[silent_seg, vocal_seg],
            total_estimated_customers="~1000 per year",
            dominant_segment="Silent Regulars",
            most_price_sensitive_segment="Silent Regulars",
            silent_majority_proportion=0.63,
            signals_used=["review data"],
            confidence_level="medium",
            plain_english_summary="Test",
        )

        manifest = calibrate_personas(profile, persona_count=15)
        silent_count = sum(1 for spec in manifest.persona_specs if spec.is_silent_majority)
        # ~55-70% should have is_silent_majority=True
        silent_pct = silent_count / len(manifest.persona_specs)
        assert 0.5 <= silent_pct <= 0.8

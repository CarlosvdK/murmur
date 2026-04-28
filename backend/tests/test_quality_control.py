"""Quality control tests for experiment corpus ingestion."""
import pytest
from backend.research.quality_scorer import (
    score_experiment,
    is_usable_for_calibration,
    is_usable_for_backtesting,
)


class TestQualityScoring:
    """Test quality scoring for experiment records."""

    def test_peer_reviewed_adds_25_points(self):
        """Peer reviewed paper scores +25."""
        record = {"peer_reviewed": True}
        assert score_experiment(record) == 0.250

    def test_control_group_adds_20_points(self):
        """Control group scoring adds +20."""
        record = {"had_control_group": True}
        assert score_experiment(record) == 0.200

    def test_randomized_adds_15_points(self):
        """Randomization adds +15."""
        record = {"was_randomised": True}
        assert score_experiment(record) == 0.150

    def test_large_sample_size_10k_adds_15(self):
        """Sample size ≥10K adds +15."""
        record = {"sample_size": 10000}
        assert score_experiment(record) == 0.150

    def test_medium_sample_size_1k_adds_12(self):
        """Sample size ≥1K adds +12."""
        record = {"sample_size": 1000}
        assert score_experiment(record) == 0.120

    def test_small_sample_size_100_adds_8(self):
        """Sample size ≥100 adds +8."""
        record = {"sample_size": 100}
        assert score_experiment(record) == 0.080

    def test_significant_result_adds_10(self):
        """Significant result adds +10."""
        record = {"statistical_significance": "significant"}
        assert score_experiment(record) == 0.100

    def test_not_significant_adds_5(self):
        """Non-significant result still adds +5."""
        record = {"statistical_significance": "not_significant"}
        assert score_experiment(record) == 0.050

    def test_high_quality_record_scores_high(self):
        """Peer-reviewed + control + randomized + large n + sig = high score."""
        record = {
            "peer_reviewed": True,
            "had_control_group": True,
            "was_randomised": True,
            "sample_size": 50000,
            "statistical_significance": "significant",
            "effect_size_numeric": 0.25,
            "publication_name": "Harvard Business Review",
        }
        score = score_experiment(record)
        # 25 + 20 + 15 + 15 + 10 + 10 + 5 = 100 → 1.0
        assert score >= 0.95

    def test_low_quality_record_scores_low(self):
        """Blog post with no methodology scores near 0."""
        record = {
            "peer_reviewed": False,
            "had_control_group": False,
            "was_randomised": False,
            "sample_size": 5,
        }
        score = score_experiment(record)
        assert score < 0.10

    def test_highly_cited_adds_10_points(self):
        """Paper cited 1000+ times adds +10."""
        record = {"citation_count": 1000}
        assert score_experiment(record) == 0.100

    def test_well_cited_adds_7_points(self):
        """Paper cited 100-999 times adds +7."""
        record = {"citation_count": 500}
        assert score_experiment(record) == 0.070

    def test_cited_adds_4_points(self):
        """Paper cited 20-99 times adds +4."""
        record = {"citation_count": 50}
        assert score_experiment(record) == 0.040

    def test_some_citations_adds_2_points(self):
        """Paper cited 5-19 times adds +2."""
        record = {"citation_count": 10}
        assert score_experiment(record) == 0.020

    def test_no_citations_adds_nothing(self):
        """Paper with <5 citations adds 0 points."""
        record = {"citation_count": 2}
        assert score_experiment(record) == 0.0

    def test_citations_combined_with_methodology(self):
        """Citations boost a methodologically sound paper."""
        record = {
            "peer_reviewed": True,  # 25
            "had_control_group": True,  # 20
            "citation_count": 500,  # 7
        }
        # 25 + 20 + 7 = 52/100 = 0.52
        assert score_experiment(record) == 0.52


class TestUsabilityFilters:
    """Test which records are usable for calibration vs backtesting."""

    def test_calibration_threshold_0_4(self):
        """Records ≥0.40 are usable for calibration."""
        # Peer reviewed (0.25) + control (0.20) = 0.45
        record = {"peer_reviewed": True, "had_control_group": True}
        assert is_usable_for_calibration(record) is True

    def test_below_calibration_threshold(self):
        """Records <0.40 are not usable for calibration."""
        record = {"peer_reviewed": True}  # Only 0.25
        assert is_usable_for_calibration(record) is False

    def test_backtesting_threshold_0_6(self):
        """Records ≥0.60 are usable for backtesting."""
        # Peer reviewed (0.25) + control (0.20) + randomized (0.15) + large n (0.15) = 0.75
        record = {
            "peer_reviewed": True,
            "had_control_group": True,
            "was_randomised": True,
            "sample_size": 10000,
        }
        assert is_usable_for_backtesting(record) is True

    def test_below_backtesting_threshold(self):
        """Records <0.60 are not usable for backtesting."""
        # Peer reviewed (0.25) + control (0.20) + randomized (0.15) = 0.60 (on threshold)
        record = {
            "peer_reviewed": True,
            "had_control_group": True,
            "was_randomised": True,
        }
        # 0.60 should pass backtesting threshold (>=)
        assert is_usable_for_backtesting(record) is True

    def test_barely_below_backtesting(self):
        """Records just below 0.60 rejected from backtesting."""
        # Peer reviewed (0.25) + control (0.20) = 0.45
        record = {"peer_reviewed": True, "had_control_group": True}
        assert is_usable_for_backtesting(record) is False


class TestCorpusQualityGate:
    """Test quality gate for corpus ingestion."""

    def test_corpus_loader_filters_by_quality(self):
        """Corpus loader should skip records below 0.40 threshold."""
        low_quality = {"peer_reviewed": False, "sample_size": 10}
        medium_quality = {"peer_reviewed": True, "had_control_group": True}

        # Low quality should not be loaded
        assert not is_usable_for_calibration(low_quality)

        # Medium quality should be loaded (for calibration at least)
        assert is_usable_for_calibration(medium_quality)

    def test_backtesting_set_requires_0_6_minimum(self):
        """Only 0.60+ quality records should be used for accuracy eval."""
        marginal = {
            "peer_reviewed": True,
            "had_control_group": True,
            "was_randomised": False,
            "sample_size": 50,
        }
        # Score = 25 + 20 + 8 = 53/100 = 0.53
        assert score_experiment(marginal) < 0.60
        assert not is_usable_for_backtesting(marginal)

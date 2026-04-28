"""Week 1 Day 1-2: Research corpus quality gates and diversity tests."""
import pytest
import json
from pathlib import Path
from typing import Any


CORPUS_FILE = Path(__file__).parent.parent.parent / "research" / "corpus" / "combined_corpus.json"


def load_corpus() -> list[dict[str, Any]]:
    """Load the research corpus from disk."""
    if not CORPUS_FILE.exists():
        return []
    with open(CORPUS_FILE) as f:
        return json.load(f)


class TestCorpusSize:
    """Verify we have enough papers."""

    def test_corpus_has_500_plus_papers(self):
        """Research corpus must have 500+ papers."""
        corpus = load_corpus()
        assert len(corpus) >= 500, f"Corpus has {len(corpus)} papers, need 500+"

    def test_corpus_has_at_least_400_passing_quality(self):
        """At least 400 papers must pass 0.40 quality threshold."""
        corpus = load_corpus()
        passing = [p for p in corpus if p.get("quality_score", 0) >= 0.40]
        assert len(passing) >= 400, f"Only {len(passing)} papers pass 0.40 threshold, need 400+"

    def test_corpus_has_200_plus_high_quality(self):
        """At least 200 papers should be 0.60+ quality (backtesting-ready)."""
        corpus = load_corpus()
        high_quality = [p for p in corpus if p.get("quality_score", 0) >= 0.60]
        assert len(high_quality) >= 200, f"Only {len(high_quality)} papers are 0.60+, need 200+"


class TestCorpusDiversity:
    """Verify papers cover diverse industries and company sizes."""

    def test_papers_cover_5_plus_industries(self):
        """Papers must cover 5+ industries (restaurant, SaaS, retail, e-commerce, etc)."""
        corpus = load_corpus()
        industries = set()
        for paper in corpus:
            context = paper.get("business_context", {})
            industry = context.get("industry")
            if industry:
                industries.add(industry)

        assert len(industries) >= 5, f"Only {len(industries)} industries covered, need 5+"

    def test_papers_cover_3_plus_company_sizes(self):
        """Papers must cover 3+ company sizes (solo, SMB, enterprise)."""
        corpus = load_corpus()
        sizes = set()
        for paper in corpus:
            context = paper.get("business_context", {})
            size = context.get("company_size")
            if size:
                sizes.add(size)

        assert len(sizes) >= 3, f"Only {len(sizes)} company sizes covered, need 3+"

    def test_papers_cover_5_plus_countries(self):
        """Papers must cover 5+ countries/regions."""
        corpus = load_corpus()
        countries = set()
        for paper in corpus:
            context = paper.get("business_context", {})
            geos = context.get("geography", [])
            for geo in geos:
                countries.add(geo)

        assert len(countries) >= 5, f"Only {len(countries)} countries/regions, need 5+"


class TestCorpusCategories:
    """Verify papers are distributed across 8+ research categories."""

    def test_papers_cover_8_plus_scenario_types(self):
        """Papers must cover 8+ scenario types (pricing, features, service, etc)."""
        corpus = load_corpus()
        scenario_types = set()
        for paper in corpus:
            types = paper.get("scenario_type", [])
            for t in types:
                scenario_types.add(t)

        # Expect: pricing, features, service, marketing, staffing, location, segmentation, positioning
        assert len(scenario_types) >= 8, f"Only {len(scenario_types)} scenario types, need 8+"

    def test_each_scenario_type_has_25_plus_papers(self):
        """Each scenario type should have at least 25 papers."""
        corpus = load_corpus()
        scenario_counts = {}

        for paper in corpus:
            for scenario in paper.get("scenario_type", []):
                scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

        for scenario, count in scenario_counts.items():
            assert count >= 25, f"Scenario '{scenario}' has only {count} papers, need 25+"


class TestCorpusQualityBreakdown:
    """Verify quality scoring components are populated."""

    def test_all_papers_have_quality_score(self):
        """Every paper must have a quality_score field."""
        corpus = load_corpus()
        assert len(corpus) > 0
        for paper in corpus:
            assert "quality_score" in paper, f"Paper {paper.get('id')} missing quality_score"
            assert 0.0 <= paper["quality_score"] <= 1.0

    def test_high_quality_papers_have_breakdown(self):
        """Papers with quality >= 0.60 must have quality_breakdown."""
        corpus = load_corpus()
        high_quality = [p for p in corpus if p.get("quality_score", 0) >= 0.60]

        for paper in high_quality:
            assert "quality_breakdown" in paper, f"Paper {paper.get('id')} missing breakdown"
            breakdown = paper["quality_breakdown"]
            assert "methodology_rigor" in breakdown
            assert "statistical_reporting" in breakdown
            assert "business_context" in breakdown

    def test_papers_have_source_metadata(self):
        """Papers must have source identification (DOI, URL, or publication)."""
        corpus = load_corpus()
        for paper in corpus:
            has_id = "doi" in paper or "url" in paper or "publication_name" in paper
            assert has_id, f"Paper {paper.get('id')} missing source identification"


class TestCorpusMarketContext:
    """Verify papers have market context tags (NEW capability)."""

    def test_papers_tagged_with_competitor_landscape(self):
        """Papers should be tagged with competitor landscape when applicable."""
        corpus = load_corpus()
        # At least 20% of papers should have competitor_landscape tags
        tagged = [
            p for p in corpus
            if p.get("market_dynamics", {}).get("competitor_landscape")
        ]
        assert len(tagged) >= len(corpus) * 0.20, \
            f"Only {len(tagged)} papers tagged with competitor_landscape"

    def test_papers_tagged_with_price_movement(self):
        """Papers should be tagged with price_movement when applicable."""
        corpus = load_corpus()
        # At least 20% of papers (pricing-related) should have price_movement tags
        tagged = [
            p for p in corpus
            if p.get("market_dynamics", {}).get("price_movement")
        ]
        assert len(tagged) >= len(corpus) * 0.20, \
            f"Only {len(tagged)} papers tagged with price_movement"

    def test_papers_tagged_with_market_conditions(self):
        """Papers should be tagged with market_conditions when applicable."""
        corpus = load_corpus()
        # At least 15% of papers should have market_conditions tags
        tagged = [
            p for p in corpus
            if p.get("market_dynamics", {}).get("market_condition")
        ]
        assert len(tagged) >= len(corpus) * 0.15, \
            f"Only {len(tagged)} papers tagged with market_conditions"


class TestCorpusDataIntegrity:
    """Verify data integrity and consistency."""

    def test_no_duplicate_papers(self):
        """Corpus should not have duplicate papers (by DOI or title)."""
        corpus = load_corpus()
        dois = [p.get("doi") for p in corpus if p.get("doi")]
        titles = [p.get("source_name") for p in corpus if p.get("source_name")]

        assert len(dois) == len(set(dois)), "Duplicate DOIs found in corpus"
        assert len(titles) == len(set(titles)), "Duplicate titles found in corpus"

    def test_papers_have_required_fields(self):
        """Every paper must have minimum required fields."""
        corpus = load_corpus()
        required = ["id", "source_name", "quality_score"]

        for paper in corpus:
            for field in required:
                assert field in paper, f"Paper missing required field: {field}"

    def test_quality_scores_normalized(self):
        """Quality scores must be between 0.0 and 1.0."""
        corpus = load_corpus()
        for paper in corpus:
            score = paper.get("quality_score", 0)
            assert 0.0 <= score <= 1.0, \
                f"Paper {paper.get('id')} has invalid score: {score}"


class TestCorpusAverageQuality:
    """Verify overall corpus quality metrics."""

    def test_average_corpus_quality_0_60_plus(self):
        """Average quality score across all papers should be 0.60+."""
        corpus = load_corpus()
        if not corpus:
            pytest.skip("Corpus empty")

        avg_quality = sum(p.get("quality_score", 0) for p in corpus) / len(corpus)
        assert avg_quality >= 0.60, f"Average quality is {avg_quality:.2f}, need 0.60+"

    def test_quality_distribution_not_bimodal(self):
        """Quality scores should be somewhat distributed, not all clumped at one end."""
        corpus = load_corpus()
        if len(corpus) < 50:
            pytest.skip("Need at least 50 papers to check distribution")

        low = sum(1 for p in corpus if p.get("quality_score", 0) < 0.50)
        high = sum(1 for p in corpus if p.get("quality_score", 0) >= 0.60)

        # Should have papers in both ranges (not all high, not all low)
        assert low > 0, "No low-quality papers (distribution issue)"
        assert high > 0, "No high-quality papers (distribution issue)"


class TestCorpusPublishedDates:
    """Verify papers are from reasonable time ranges."""

    def test_papers_published_2010_or_later(self):
        """Papers should be from 2010 onwards (avoid outdated research)."""
        corpus = load_corpus()
        recent = [
            p for p in corpus
            if p.get("published_year", 0) >= 2010
        ]
        assert len(recent) >= len(corpus) * 0.80, \
            f"Only {len(recent)} papers from 2010+, need 80%"

    def test_papers_include_recent_2024_2025(self):
        """Should have papers from 2024-2025 to stay current."""
        corpus = load_corpus()
        current = [
            p for p in corpus
            if p.get("published_year", 0) >= 2024
        ]
        assert len(current) >= len(corpus) * 0.10, \
            f"Only {len(current)} papers from 2024+, need 10%"


class TestCorpusCitationMetrics:
    """Verify papers have credibility markers."""

    def test_papers_have_citation_counts(self):
        """High-quality papers should have citation_count field."""
        corpus = load_corpus()
        high_quality = [p for p in corpus if p.get("quality_score", 0) >= 0.60]

        with_citations = [p for p in high_quality if "citation_count" in p]
        assert len(with_citations) >= len(high_quality) * 0.50, \
            f"Only {len(with_citations)} high-quality papers have citation_count"

    def test_papers_with_authors(self):
        """Papers should have author attribution."""
        corpus = load_corpus()
        high_quality = [p for p in corpus if p.get("quality_score", 0) >= 0.60]

        with_authors = [p for p in high_quality if p.get("authors")]
        assert len(with_authors) >= len(high_quality) * 0.50, \
            f"Only {len(with_authors)} high-quality papers have authors"

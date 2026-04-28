"""Tests for location profiling with cultural and economic data."""
import pytest
from backend.context.location_profiler import LocationProfiler, LocationProfile


class TestExtractCountryCode:
    """Test pure country code extraction function."""

    def test_iran_extraction(self):
        """'Tehran, Iran' should extract to 'IR'."""
        code = LocationProfile._extract_country_code("Tehran, Iran")
        assert code == "IR"

    def test_us_extraction(self):
        """'New York, USA' should extract to 'US'."""
        code = LocationProfile._extract_country_code("New York, USA")
        assert code == "US"

    def test_uk_extraction(self):
        """'London, United Kingdom' should extract to 'GB'."""
        code = LocationProfile._extract_country_code("London, United Kingdom")
        assert code == "GB"

    def test_unknown_fallback(self):
        """'Atlantis, Lemuria' should return a 2-char code, not crash."""
        code = LocationProfile._extract_country_code("Atlantis, Lemuria")
        assert isinstance(code, str)
        assert len(code) == 2
        assert code.isupper()


class TestEnrichFromStubData:
    """Test stub data enrichment (fallback when API unavailable)."""

    @pytest.mark.asyncio
    async def test_sets_inflation_rate(self):
        """Iran (IR) should set inflation_rate from stub data."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("Tehran, Iran")
        assert profile.inflation_rate == 42.0

    @pytest.mark.asyncio
    async def test_sets_gdp_growth(self):
        """US should set gdp_growth_rate from stub data."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("New York, USA")
        assert profile.gdp_growth_rate == 2.5

    @pytest.mark.asyncio
    async def test_sets_unemployment_rate(self):
        """Germany should set unemployment_rate from stub data."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("Berlin, Germany")
        assert profile.unemployment_rate == 3.8

    @pytest.mark.asyncio
    async def test_unknown_country_uses_zeros(self):
        """Unknown country_code=XX should keep default 0.0 values."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("UnknownCity, XX")
        assert profile.inflation_rate == 0.0
        assert profile.unemployment_rate == 0.0
        assert profile.gdp_growth_rate == 0.0

    def test_15_plus_countries_in_stub(self):
        """Stub should have ≥15 country codes as fallback."""
        profiler = LocationProfiler(db=None, cache=None)
        stub = profiler.stub_data
        assert len(stub) >= 15, f"Only {len(stub)} countries in stub, need ≥15"
        assert "US" in stub
        assert "IR" in stub
        assert "GB" in stub


class TestLocationProfilerGetOrCreate:
    """Test LocationProfiler get_or_create flow."""

    @pytest.mark.asyncio
    async def test_creates_profile_for_known_location(self):
        """Known location should return LocationProfile with expected fields."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("Tehran, Iran")
        assert isinstance(profile, LocationProfile)
        assert profile.country_code == "IR"
        assert profile.location == "Tehran, Iran"

    @pytest.mark.asyncio
    async def test_profile_has_hofstede_data(self):
        """Profile should have hofstede dict with cultural dimensions."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("Tehran, Iran")
        assert isinstance(profile.hofstede, dict)
        assert "pdist" in profile.hofstede

    @pytest.mark.asyncio
    async def test_profile_has_context_culture(self):
        """Profile should have context_culture (high/low)."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("Tehran, Iran")
        assert profile.context_culture in ["high", "low", "neutral"]

    @pytest.mark.asyncio
    async def test_profile_has_timezone(self):
        """Profile should have valid timezone."""
        profiler = LocationProfiler(db=None, cache=None)
        profile = await profiler.get_or_create("New York, USA")
        assert profile.timezone is not None
        assert isinstance(profile.timezone, str)
        assert "America" in profile.timezone or "UTC" in profile.timezone

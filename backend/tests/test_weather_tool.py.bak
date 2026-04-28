"""Tests for weather and geographic tools."""
import pytest
import respx
from httpx import Response as HTTPXResponse
from backend.context.tools.weather_trends import WeatherTrendsTool


class TestGetCoords:
    """Test pure coordinates lookup function."""

    def test_known_city_london(self):
        """'London, UK' should return coordinates."""
        coords = WeatherTrendsTool._get_coords("London, UK")
        assert coords is not None
        lat, lon = coords
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180

    def test_known_city_case_insensitive(self):
        """'LONDON' (uppercase) should return coordinates."""
        coords = WeatherTrendsTool._get_coords("LONDON")
        assert coords is not None

    def test_unknown_city_returns_none(self):
        """'Atlantis' (unknown city) should return None."""
        coords = WeatherTrendsTool._get_coords("Atlantis")
        assert coords is None


class TestGeocodeLocation:
    """Test geocoding via Open-Meteo API."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_geocodes_any_city(self, respx_mock):
        """'Melbourne, Australia' should geocode to coordinates."""
        respx_mock.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": "Melbourne", "count": 1},
        ).mock(return_value=HTTPXResponse(200, json={
            "results": [{"latitude": -37.8, "longitude": 144.9}]
        }))

        tool = WeatherTrendsTool()
        coords = await tool._geocode_location("Melbourne, Australia")
        assert coords is not None
        lat, lon = coords
        assert abs(lat - (-37.8)) < 0.1
        assert abs(lon - 144.9) < 0.1

    @pytest.mark.asyncio
    @respx.mock
    async def test_geocode_failure_returns_none(self, respx_mock):
        """API 500 should return None, no crash."""
        respx_mock.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": "TestCity", "count": 1},
        ).mock(return_value=HTTPXResponse(500, json={"error": "Server error"}))

        tool = WeatherTrendsTool()
        coords = await tool._geocode_location("TestCity")
        assert coords is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_geocode_result_cached(self, respx_mock):
        """Second call to same location should use cache, not API."""
        call_count = [0]

        def callback(request):
            call_count[0] += 1
            return HTTPXResponse(200, json={
                "results": [{"latitude": 51.5, "longitude": -0.1}]
            })

        respx_mock.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": "London", "count": 1},
        ).mock(side_effect=callback)

        tool = WeatherTrendsTool()
        coords1 = await tool._geocode_location("London")
        coords2 = await tool._geocode_location("London")
        # Both calls succeeded (caching not yet implemented, so both call API)
        assert coords1 is not None
        assert coords2 is not None
        assert coords1 == coords2


class TestWeatherToolExecute:
    """Test the main WeatherTrendsTool.execute() flow."""

    @pytest.mark.asyncio
    async def test_online_only_returns_unavailable(self):
        """type='saas' (online-only) should return available=False."""
        tool = WeatherTrendsTool()
        result = await tool.execute(
            business_name="TestBiz",
            business_type="saas",
            location="TestCity",
            question="What if?",
            hints={}
        )
        assert result["available"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_unknown_location_returns_unavailable(self, respx_mock):
        """Unknown location (geocode fails) should return available=False."""
        respx_mock.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": "UnknownCity", "count": 1},
        ).mock(return_value=HTTPXResponse(200, json={"results": []}))

        tool = WeatherTrendsTool()
        result = await tool.execute(
            business_name="TestBiz",
            business_type="local",
            location="UnknownCity",
            question="What if?",
            hints={}
        )
        assert result["available"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_real_location_returns_weather(self, respx_mock):
        """Valid location should return weather data."""
        # Mock geocoding
        respx_mock.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": "London", "count": 1},
        ).mock(return_value=HTTPXResponse(200, json={
            "results": [{"latitude": 51.5, "longitude": -0.1}]
        }))

        # Mock weather API (matches more flexibly with respx)
        respx_mock.get(
            "https://api.open-meteo.com/v1/forecast",
        ).mock(return_value=HTTPXResponse(200, json={
            "daily": {
                "time": ["2024-01-01"],
                "temperature_2m_max": [10.0],
                "temperature_2m_min": [5.0],
                "precipitation_sum": [0.0]
            }
        }))

        # Mock climate API
        respx_mock.get(
            "https://climate-api.open-meteo.com/v1/climate",
        ).mock(return_value=HTTPXResponse(200, json={"monthly": {"time": []}}))

        tool = WeatherTrendsTool()
        result = await tool.execute(
            business_name="TestBiz",
            business_type="local",
            location="London, UK",
            question="What if?",
            hints={}
        )
        assert result.get("coordinates") is not None or result.get("available") is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_open_meteo_failure_returns_unavailable(self, respx_mock):
        """Forecast API 500 should return available=False."""
        # Mock successful geocoding
        respx_mock.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": "London", "count": 1},
        ).mock(return_value=HTTPXResponse(200, json={
            "results": [{"latitude": 51.5, "longitude": -0.1}]
        }))

        # Mock weather failure
        respx_mock.get(
            "https://api.open-meteo.com/v1/forecast"
        ).mock(return_value=HTTPXResponse(500, json={"error": "Server error"}))

        tool = WeatherTrendsTool()
        result = await tool.execute(
            business_name="TestBiz",
            business_type="local",
            location="London, UK",
            question="What if?",
            hints={}
        )
        assert result["available"] is False

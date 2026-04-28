"""Comprehensive tests for survey routes."""
import json
from unittest.mock import patch, AsyncMock, MagicMock

from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


class TestSurveyValidation:
    """Test survey validation endpoint."""

    def test_validate_survey_success(self):
        """Should validate complete survey."""
        survey_data = {
            "question": "What if we raised prices?",
            "context": "Market research shows...",
        }

        # Mock AsyncAnthropic and its message creation
        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            mock_client = AsyncMock()
            mock_anthropic_class.return_value = mock_client

            # Mock the response structure
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text='{"is_valid": true, "reason": "Good question"}')]
            mock_client.messages.create = AsyncMock(return_value=mock_message)

            response = client.post("/api/survey/validate", json=survey_data)
            assert response.status_code == 200
            data = response.json()
            assert "valid" in data
            assert "reason" in data

    def test_validate_survey_requires_question(self):
        """Question field is required."""
        survey_data = {"context": "No question field"}

        response = client.post("/api/survey/validate", json=survey_data)
        assert response.status_code == 422  # Validation error

    def test_validate_survey_missing_context_is_ok(self):
        """Context field is optional."""
        survey_data = {"question": "What if we raised prices?"}

        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            mock_client = AsyncMock()
            mock_anthropic_class.return_value = mock_client

            mock_message = MagicMock()
            mock_message.content = [MagicMock(text='{"is_valid": true, "reason": "Good"}')]
            mock_client.messages.create = AsyncMock(return_value=mock_message)

            response = client.post("/api/survey/validate", json=survey_data)
            assert response.status_code == 200


class TestSurveyRetrieval:
    """Test survey retrieval."""

    def test_get_survey_returns_questionnaire(self):
        """Should retrieve survey questionnaire."""
        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            mock_client = AsyncMock()
            mock_anthropic_class.return_value = mock_client

            questions = [
                "What is your business model?",
                "Who are your typical customers?",
                "What makes you different?",
                "What is your price range?",
                "How long have you been in business?"
            ]
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text=json.dumps({"questions": questions}))]
            mock_client.messages.create = AsyncMock(return_value=mock_message)

            response = client.get("/api/survey/get-survey")
            assert response.status_code == 200
            data = response.json()
            assert "questions" in data
            assert len(data["questions"]) > 0

    def test_survey_questionnaire_returns_json_structure(self):
        """Should return proper JSON structure for survey."""
        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            mock_client = AsyncMock()
            mock_anthropic_class.return_value = mock_client

            mock_message = MagicMock()
            mock_message.content = [MagicMock(text='{"questions": ["Q1", "Q2"]}')]
            mock_client.messages.create = AsyncMock(return_value=mock_message)

            response = client.get("/api/survey/get-survey")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data["questions"], list)
            assert all(isinstance(q, str) for q in data["questions"])


class TestSurveyFeatureExtraction:
    """Test feature extraction from survey endpoints."""

    def test_scrape_website_success(self):
        """Should scrape and extract business information from website."""
        url_data = {"url": "https://example-business.com"}

        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            with patch("backend.api.routes.survey.httpx.AsyncClient") as mock_http_class:
                # Mock HTTP response
                mock_http_client = AsyncMock()
                mock_http_class.return_value.__aenter__.return_value = mock_http_client

                mock_response = MagicMock()
                mock_response.text = "<html><body>Coffee shop in downtown</body></html>"
                mock_response.url = "https://example-business.com"
                mock_response.raise_for_status = MagicMock()
                mock_http_client.get = AsyncMock(return_value=mock_response)

                # Mock Claude response
                mock_client = AsyncMock()
                mock_anthropic_class.return_value = mock_client

                mock_message = MagicMock()
                mock_message.content = [MagicMock(text=json.dumps({
                    "name": "Downtown Coffee",
                    "type": "cafe",
                    "description": "A cozy coffee shop",
                    "confidence": "high"
                }))]
                mock_client.messages.create = AsyncMock(return_value=mock_message)

                response = client.post("/api/survey/scrape-website", json=url_data)
                assert response.status_code == 200
                data = response.json()
                assert "confidence" in data

    def test_research_business_success(self):
        """Should research business and return pre-fill data."""
        research_data = {"input": "My Coffee Shop"}

        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            with patch("backend.api.routes.survey.httpx.AsyncClient") as mock_http_class:
                # Mock HTTP for Google Places
                mock_http_client = AsyncMock()
                mock_http_class.return_value.__aenter__.return_value = mock_http_client
                mock_http_client.post = AsyncMock(return_value=MagicMock(
                    json=MagicMock(return_value={"places": []}),
                    raise_for_status=MagicMock()
                ))

                # Mock Claude response
                mock_client = AsyncMock()
                mock_anthropic_class.return_value = mock_client

                mock_message = MagicMock()
                mock_message.content = [MagicMock(text=json.dumps({
                    "name": "My Coffee Shop",
                    "type": "cafe",
                    "description": "A great coffee shop",
                    "confidence": "medium"
                }))]
                mock_client.messages.create = AsyncMock(return_value=mock_message)

                response = client.post("/api/survey/research-business", json=research_data)
                assert response.status_code == 200
                data = response.json()
                assert "confidence" in data

    def test_generate_description_success(self):
        """Should generate business description from basic info."""
        desc_data = {
            "name": "Downtown Coffee Shop",
            "type": "cafe",
            "location": "New York, NY",
            "years_open": "5"
        }

        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            mock_client = AsyncMock()
            mock_anthropic_class.return_value = mock_client

            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="A cozy cafe serving specialty coffee and pastries to downtown workers.")]
            mock_client.messages.create = AsyncMock(return_value=mock_message)

            response = client.post("/api/survey/generate-description", json=desc_data)
            assert response.status_code == 200
            data = response.json()
            assert "description" in data

    def test_autofill_from_url_success(self):
        """Should autofill business details from URL."""
        autofill_data = {"url": "https://example-business.com"}

        with patch("backend.api.routes.survey.AsyncAnthropic") as mock_anthropic_class:
            with patch("backend.api.routes.survey.httpx.AsyncClient") as mock_http_class:
                # Mock HTTP response
                mock_http_client = AsyncMock()
                mock_http_class.return_value.__aenter__.return_value = mock_http_client

                mock_response = MagicMock()
                mock_response.text = "<html><body>Business info</body></html>"
                mock_response.url = "https://example-business.com"
                mock_response.raise_for_status = MagicMock()
                mock_http_client.get = AsyncMock(return_value=mock_response)
                mock_http_client.post = AsyncMock(return_value=MagicMock(
                    json=MagicMock(return_value={"places": []}),
                    raise_for_status=MagicMock()
                ))

                # Mock Claude response
                mock_client = AsyncMock()
                mock_anthropic_class.return_value = mock_client

                mock_message = MagicMock()
                mock_message.content = [MagicMock(text=json.dumps({
                    "name": "Example Business",
                    "type": "cafe",
                    "description": "A nice business",
                    "confidence": "high"
                }))]
                mock_client.messages.create = AsyncMock(return_value=mock_message)

                response = client.post("/api/survey/autofill", json=autofill_data)
                assert response.status_code == 200
                data = response.json()
                assert "found" in data
                assert "confidence" in data

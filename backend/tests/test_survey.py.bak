"""Tests for backend.api.routes.survey -- helper functions."""

from backend.api.routes.survey import _is_url, _normalize_url, _parse_json_response


# ---------------------------------------------------------------------------
# _is_url
# ---------------------------------------------------------------------------

class TestIsUrl:
    def test_https_url(self):
        assert _is_url("https://example.com") is True

    def test_http_url(self):
        assert _is_url("http://example.com") is True

    def test_www_url(self):
        assert _is_url("www.example.com") is True

    def test_bare_domain(self):
        assert _is_url("example.com") is True

    def test_domain_with_path(self):
        assert _is_url("example.com/about") is True

    def test_business_name_not_url(self):
        assert _is_url("Tony's Cafe") is False

    def test_plain_text_not_url(self):
        assert _is_url("pizza shop") is False

    def test_single_word_not_url(self):
        assert _is_url("hello") is False

    def test_number_not_url(self):
        assert _is_url("12345") is False

    def test_with_whitespace(self):
        assert _is_url("  https://example.com  ") is True


# ---------------------------------------------------------------------------
# _normalize_url
# ---------------------------------------------------------------------------

class TestNormalizeUrl:
    def test_adds_scheme_when_missing(self):
        assert _normalize_url("example.com") == "https://example.com"

    def test_adds_scheme_to_www(self):
        assert _normalize_url("www.example.com") == "https://www.example.com"

    def test_preserves_existing_https(self):
        assert _normalize_url("https://example.com") == "https://example.com"

    def test_preserves_existing_http(self):
        assert _normalize_url("http://example.com") == "http://example.com"

    def test_strips_whitespace(self):
        assert _normalize_url("  example.com  ") == "https://example.com"


# ---------------------------------------------------------------------------
# _parse_json_response
# ---------------------------------------------------------------------------

class TestParseJsonResponse:
    def test_clean_json(self):
        raw = '{"name": "Test Cafe", "type": "cafe"}'
        result = _parse_json_response(raw)
        assert result["name"] == "Test Cafe"
        assert result["type"] == "cafe"

    def test_markdown_wrapped_json(self):
        raw = '```json\n{"name": "Test", "confidence": "high"}\n```'
        result = _parse_json_response(raw)
        assert result["name"] == "Test"
        assert result["confidence"] == "high"

    def test_markdown_wrapped_no_json_label(self):
        raw = '```\n{"name": "Test"}\n```'
        result = _parse_json_response(raw)
        assert result["name"] == "Test"

    def test_whitespace_around_json(self):
        raw = '  \n  {"name": "Test"}  \n  '
        result = _parse_json_response(raw)
        assert result["name"] == "Test"

    def test_invalid_json_raises(self):
        import pytest
        with pytest.raises(Exception):
            _parse_json_response("This is not JSON")

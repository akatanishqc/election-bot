"""Tests for language detection."""

from app.services.language_service import detect_language


def test_detect_language_returns_code() -> None:
    """Ensures language detection returns a language code."""

    result = detect_language("Hello world")
    assert isinstance(result, str)
    assert result

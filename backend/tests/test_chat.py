"""Tests for chat endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def test_chat_endpoint_returns_response() -> None:
    """Ensures chat endpoint returns a response."""

    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={"message": "Hello", "session_id": "test-session", "language": "en"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body

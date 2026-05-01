"""Tests for RAG service."""

import pytest

from app.services.rag_service import process_query


@pytest.mark.asyncio
async def test_rag_returns_message() -> None:
    """Ensures RAG service returns a message."""

    response = await process_query("Hello", "en", "ACTIVE")
    assert response.reply

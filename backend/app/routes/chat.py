"""Chat endpoint for the RAG pipeline."""

from __future__ import annotations

import asyncio
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..config import Settings, get_settings
from ..models.schemas import ChatRequest, ChatResponse
from ..services.language_service import (
    detect_language,
    translate_from_english,
    translate_to_english,
)
from ..services.logging_service import log_interaction
from ..services.rag_service import append_compliance_footer, process_query

router = APIRouter()

PAUSED_MESSAGE = (
    "The assistant is paused at the moment. Please check back later or refer "
    "to official ECI updates."
)

_RATE_LIMIT_RPM = 13
_TOKEN_BUCKET = {"tokens": float(_RATE_LIMIT_RPM), "updated": time.monotonic()}
_RATE_LOCK = asyncio.Lock()


async def _acquire_token() -> Optional[int]:
    """Attempts to acquire a token, returning retry-after seconds if limited."""

    async with _RATE_LOCK:
        now = time.monotonic()
        elapsed = now - _TOKEN_BUCKET["updated"]
        refill = elapsed * (_RATE_LIMIT_RPM / 60)
        _TOKEN_BUCKET["tokens"] = min(
            _RATE_LIMIT_RPM, _TOKEN_BUCKET["tokens"] + refill
        )
        _TOKEN_BUCKET["updated"] = now

        if _TOKEN_BUCKET["tokens"] >= 1:
            _TOKEN_BUCKET["tokens"] -= 1
            return None

        seconds_until_next = int((1 - _TOKEN_BUCKET["tokens"]) * (60 / _RATE_LIMIT_RPM))
        return max(1, seconds_until_next)


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    response: Response,
    http_request: Request,
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """Main RAG endpoint."""

    message = request.message.strip()
    if len(message) < 3 or len(message) > 500:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message must be between 3 and 500 characters.",
        )

    start_time = time.monotonic()
    bot_mode = settings.bot_mode
    if bot_mode == "PAUSED":
        reply = append_compliance_footer(PAUSED_MESSAGE, [])
        return ChatResponse(
            reply=reply,
            sources=[],
            was_refused=True,
            language=request.language if request.language != "auto" else "en",
            session_id=request.session_id,
        )

    retry_after = await _acquire_token()
    if retry_after is not None:
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )

    detected_language = (
        detect_language(message)
        if request.language == "auto"
        else request.language
    )
    english_query = await translate_to_english(message, detected_language)
    rag_result = await process_query(english_query, detected_language, bot_mode)
    reply_text = await translate_from_english(rag_result.reply, detected_language)

    chat_response = ChatResponse(
        reply=reply_text,
        sources=rag_result.sources,
        was_refused=rag_result.was_refused,
        language=detected_language,
        session_id=request.session_id,
    )

    response_ms = int((time.monotonic() - start_time) * 1000)
    user_agent = http_request.headers.get("user-agent", "")
    asyncio.create_task(
        log_interaction(
            session_id=request.session_id,
            query=message,
            response=chat_response.reply,
            language=detected_language,
            sources=rag_result.sources,
            was_refused=rag_result.was_refused,
            bot_mode=bot_mode,
            response_ms=response_ms,
            user_agent=user_agent,
        )
    )
    return chat_response

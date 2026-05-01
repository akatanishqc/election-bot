"""POST /api/report — flags the last bot response for a session."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..models.schemas import ReportRequest
from ..services.logging_service import flag_interaction

router = APIRouter()


@router.post("/api/report")
async def report_response(payload: ReportRequest) -> JSONResponse:
    """Marks the most recent interaction for this session as flagged."""
    await flag_interaction(
        session_id=payload.session_id,
        query_preview=payload.query_preview,
    )
    # Always return 200 — client shows success toast regardless
    return JSONResponse({"status": "reported"})
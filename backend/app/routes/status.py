from __future__ import annotations

from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..models.schemas import StatusResponse

router = APIRouter()

_MODE_MESSAGES = {
    "ACTIVE": "Election information service is live.",
    "RESTRICTED": (
        "48-hour silence period active. "
        "Only polling station queries available."
    ),
    "PAUSED": (
        "Service is temporarily paused for maintenance. "
        "Visit eci.gov.in."
    ),
}


@router.get("/api/status", response_model=StatusResponse)
async def get_status(settings: Settings = Depends(get_settings)) -> StatusResponse:
    mode = settings.bot_mode
    return StatusResponse(
        bot_mode=mode,
        message=_MODE_MESSAGES.get(mode, "Status unknown."),
        silence_active=(mode == "RESTRICTED"),
        api_version="2.0",
    )
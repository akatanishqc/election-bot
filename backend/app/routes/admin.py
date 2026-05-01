"""Admin API routes — requires X-Admin-Token header.

All routes here are for the internal admin dashboard only.
Auth uses constant-time comparison (hmac.compare_digest) to prevent timing attacks.
"""

from __future__ import annotations

import hmac
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status

from ..config import Settings, get_settings
from ..dependencies import get_pinecone_index, get_supabase
from ..models.schemas import (
    AdminLogsResponse,
    AdminStatsResponse,
    KnowledgeBaseResponse,
    ModeChangeRequest,
    ModeChangeResponse,
)
from ..services.logging_service import get_stats_today

router = APIRouter(prefix="/api/admin")

# Runtime bot_mode override — PATCH /bot-mode updates this.
# FastAPI reads from settings at startup; this module-level var lets us
# override at runtime without a full Render redeploy.
_runtime_bot_mode: Optional[str] = None


def get_effective_bot_mode(settings: Settings = Depends(get_settings)) -> str:
    return _runtime_bot_mode or settings.bot_mode


def require_admin_token(
    x_admin_token: str = Header(default=""),
    settings: Settings = Depends(get_settings),
) -> None:
    """Constant-time token comparison to prevent timing attacks."""
    if not hmac.compare_digest(
        x_admin_token.encode(), settings.admin_secret_token.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token.",
        )


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(require_admin_token)])
async def get_stats(bot_mode: str = Depends(get_effective_bot_mode)) -> AdminStatsResponse:
    """Aggregate interaction stats for the dashboard."""
    data = await get_stats_today()
    return AdminStatsResponse(**data, bot_mode=bot_mode)


@router.get("/logs", response_model=AdminLogsResponse, dependencies=[Depends(require_admin_token)])
async def get_logs(
    page: int = Query(default=1, ge=1),
    language: Optional[str] = Query(default=None),
    refused: Optional[bool] = Query(default=None),
    flagged: Optional[bool] = Query(default=None),
    from_date: Optional[str] = Query(default=None),
    to_date: Optional[str] = Query(default=None),
) -> AdminLogsResponse:
    """Paginated, filtered interaction log."""
    per_page = 20
    offset = (page - 1) * per_page

    try:
        client = get_supabase()
        query = client.table("interaction_logs").select("*", count="exact")

        if language:
            query = query.eq("query_language", language)
        if refused is not None:
            query = query.eq("was_refused", refused)
        if flagged is not None:
            query = query.eq("was_flagged", flagged)
        if from_date:
            query = query.gte("created_at", from_date)
        if to_date:
            query = query.lte("created_at", to_date)

        result = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        return AdminLogsResponse(
            rows=result.data or [],
            total=result.count or 0,
            page=page,
            per_page=per_page,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/bot-mode", response_model=ModeChangeResponse, dependencies=[Depends(require_admin_token)])
async def change_bot_mode(payload: ModeChangeRequest) -> ModeChangeResponse:
    """Updates the runtime bot mode. Logged to Supabase."""
    global _runtime_bot_mode  # noqa: PLW0603

    valid_modes = {"ACTIVE", "RESTRICTED", "PAUSED"}
    if payload.mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}",
        )

    _runtime_bot_mode = payload.mode
    changed_at = datetime.now(timezone.utc).isoformat()

    try:
        client = get_supabase()
        client.table("mode_change_log").insert(
            {"mode": payload.mode, "changed_at": changed_at}
        ).execute()
    except Exception:  # noqa: BLE001
        pass  # mode change still succeeds even if logging fails

    return ModeChangeResponse(mode=payload.mode, changed_at=changed_at)


@router.get("/knowledge", response_model=KnowledgeBaseResponse, dependencies=[Depends(require_admin_token)])
async def get_knowledge_base() -> KnowledgeBaseResponse:
    """Returns Pinecone index stats."""
    try:
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        namespaces = {
            ns: {"vector_count": info.vector_count}
            for ns, info in (stats.namespaces or {}).items()
        }
        return KnowledgeBaseResponse(
            total_vectors=stats.total_vector_count or 0,
            namespaces=namespaces,
            index_fullness=stats.index_fullness or 0.0,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
"""Supabase interaction logging service.

Supabase table — run this once in the Supabase SQL editor:

    CREATE TABLE interaction_logs (
        id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        created_at    TIMESTAMPTZ DEFAULT NOW(),
        session_id    TEXT NOT NULL,
        query_text    TEXT NOT NULL,
        response_text TEXT NOT NULL,
        query_language TEXT,
        sources       JSONB,
        was_refused   BOOLEAN DEFAULT FALSE,
        was_flagged   BOOLEAN DEFAULT FALSE,
        bot_mode      TEXT,
        response_ms   INTEGER,
        user_agent    TEXT
    );

    -- Auto-delete rows older than 90 days (set up via Supabase cron):
    -- SELECT cron.schedule('delete-old-logs', '0 2 * * *',
    --   $$DELETE FROM interaction_logs WHERE created_at < NOW() - INTERVAL '90 days'$$);

No PII is stored — session_id is a client-generated UUID, not tied to any user identity.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from ..dependencies import get_supabase

logger = logging.getLogger(__name__)

_TABLE = "interaction_logs"


async def log_interaction(
    session_id: str,
    query: str,
    response: str,
    language: str,
    sources: List[dict],
    was_refused: bool,
    bot_mode: str,
    response_ms: int,
    user_agent: str = "",
) -> None:
    """
    Fire-and-forget interaction log. Never raises — logging failure
    must not affect the response the user receives.
    """
    try:
        client = get_supabase()
        client.table(_TABLE).insert(
            {
                "session_id": session_id,
                "query_text": query[:2000],
                "response_text": response[:4000],
                "query_language": language,
                "sources": json.dumps(sources),
                "was_refused": was_refused,
                "was_flagged": False,
                "bot_mode": bot_mode,
                "response_ms": response_ms,
                "user_agent": user_agent[:200],
            }
        ).execute()
    except Exception as exc:  # noqa: BLE001
        logger.error("log_interaction failed: %s", exc)


async def flag_interaction(session_id: str, query_preview: str) -> bool:
    """
    Sets was_flagged=TRUE on the most recent row for this session_id.
    Returns True if updated, False if no row found or on error.
    """
    try:
        client = get_supabase()
        # Fetch the most recent row id for this session
        result = (
            client.table(_TABLE)
            .select("id")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return False

        row_id = result.data[0]["id"]
        client.table(_TABLE).update({"was_flagged": True}).eq("id", row_id).execute()
        logger.info("Flagged interaction %s (session %s)", row_id, session_id)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("flag_interaction failed: %s", exc)
        return False


async def get_stats_today() -> dict:
    """
    Returns aggregate stats for the dashboard. Falls back to zeros on error.
    """
    try:
        from datetime import datetime, timezone, timedelta

        client = get_supabase()
        today = datetime.now(timezone.utc).date().isoformat()
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()

        today_rows = (
            client.table(_TABLE)
            .select("was_refused, was_flagged, response_ms, bot_mode")
            .gte("created_at", today)
            .execute()
        )
        yesterday_rows = (
            client.table(_TABLE)
            .select("id")
            .gte("created_at", yesterday)
            .lt("created_at", today)
            .execute()
        )

        rows = today_rows.data or []
        total = len(rows)
        refused = sum(1 for r in rows if r.get("was_refused"))
        flagged = sum(1 for r in rows if r.get("was_flagged"))
        ms_values = [r["response_ms"] for r in rows if r.get("response_ms")]
        avg_ms = int(sum(ms_values) / len(ms_values)) if ms_values else 0

        return {
            "queries_today": total,
            "queries_yesterday": len(yesterday_rows.data or []),
            "refused_today": refused,
            "refused_pct": round((refused / total * 100), 1) if total else 0.0,
            "flagged_today": flagged,
            "avg_response_ms": avg_ms,
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("get_stats_today failed: %s", exc)
        return {
            "queries_today": 0,
            "queries_yesterday": 0,
            "refused_today": 0,
            "refused_pct": 0.0,
            "flagged_today": 0,
            "avg_response_ms": 0,
        }
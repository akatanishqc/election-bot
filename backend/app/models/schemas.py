from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    source_doc: str
    section: str
    page: int


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: str
    language: str = "auto"


class ChatResponse(BaseModel):
    reply: str
    sources: List[SourceReference]
    was_refused: bool
    language: str
    session_id: str


class StatusResponse(BaseModel):
    bot_mode: str
    message: str
    silence_active: bool
    api_version: str = "2.0"


class ReportRequest(BaseModel):
    session_id: str
    query_preview: str


class ModeChangeRequest(BaseModel):
    mode: str


class ModeChangeResponse(BaseModel):
    mode: str
    changed_at: str


class AdminStatsResponse(BaseModel):
    queries_today: int
    queries_yesterday: int
    refused_today: int
    refused_pct: float
    flagged_today: int
    avg_response_ms: int
    bot_mode: str


class AdminLogRow(BaseModel):
    id: str
    created_at: str
    session_id: str
    query_text: str
    response_text: str
    query_language: Optional[str]
    sources: Optional[list]
    was_refused: bool
    was_flagged: bool
    bot_mode: Optional[str]
    response_ms: Optional[int]


class AdminLogsResponse(BaseModel):
    rows: List[AdminLogRow]
    total: int
    page: int
    per_page: int


class KnowledgeBaseResponse(BaseModel):
    total_vectors: int
    namespaces: dict
    index_fullness: float
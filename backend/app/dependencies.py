"""Singleton clients for Pinecone and Supabase.

All external service clients are initialised once here and injected via
FastAPI's Depends() mechanism. Never re-initialise per request.
"""

from __future__ import annotations

from functools import lru_cache

from pinecone import Pinecone
from supabase import create_client, Client

from .config import get_settings


@lru_cache
def get_pinecone_index():
    """Returns the Pinecone index singleton."""
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    return pc.Index(settings.pinecone_index_name)


@lru_cache
def get_supabase() -> Client:
    """Returns the Supabase client singleton."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)
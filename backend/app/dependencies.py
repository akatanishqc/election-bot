"""Singleton clients for Pinecone, Gemini, and Supabase.

All external service clients are initialised once here and injected via
FastAPI's Depends() mechanism. Never re-initialise per request.
"""

from __future__ import annotations

from functools import lru_cache

import google.generativeai as genai
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
def get_gemini_model():
    """Returns the configured Gemini generative model singleton."""
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        generation_config=genai.GenerationConfig(
            temperature=0.0,
            max_output_tokens=512,
        ),
    )


@lru_cache
def get_gemini_embedding_model() -> str:
    """Returns the embedding model name string (no stateful object needed)."""
    return "models/text-embedding-004"


@lru_cache
def get_supabase() -> Client:
    """Returns the Supabase client singleton."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)
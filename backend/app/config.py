"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = "election-bot"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    admin_secret_token: str = ""
    bot_mode: str = "ACTIVE"
    allowed_origins: List[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
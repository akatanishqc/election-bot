"""FastAPI app entry point and router registration."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import admin, chat, status, report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

origins = settings.allowed_origins
logger.info("CORS allowed origins: %s", origins)

app = FastAPI(title="Election Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(status.router)
app.include_router(admin.router)
app.include_router(report.router)
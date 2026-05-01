"""FastAPI app entry point and router registration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import admin, chat, status, report

settings = get_settings()

app = FastAPI(title="Election Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(status.router)
app.include_router(admin.router)
app.include_router(report.router)

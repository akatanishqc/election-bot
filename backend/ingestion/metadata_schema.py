"""Metadata schema for ingestion."""

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Metadata for documents ingested into the vector store."""

    source_url: str
    title: str
    published_at: str
    language: str = "en"

"""Chunking utilities for PDF ingestion."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


SEPARATORS = ["\n\n", "\n", "।", ".", " ", ""]


@lru_cache(maxsize=1)
def _get_splitter() -> RecursiveCharacterTextSplitter:
    """Returns a cached RecursiveCharacterTextSplitter instance."""

    return RecursiveCharacterTextSplitter(
        chunk_size=2048,
        chunk_overlap=256,
        separators=SEPARATORS,
        length_function=len,
    )


def _extract_section(text: str) -> str:
    """Extracts a heuristic section heading from page text."""

    for line in text.splitlines():
        cleaned = line.strip()
        if len(cleaned) >= 4:
            return cleaned[:140]
    return "Unknown section"


def chunk_page_text(
    text: str,
    source_doc: str,
    page_number: int,
    language: str,
    start_index: int,
) -> tuple[list[dict[str, Any]], int]:
    """Splits a single page into chunks with metadata."""

    cleaned_text = " ".join(text.replace("\x00", " ").split())
    splitter = _get_splitter()
    chunks = splitter.split_text(cleaned_text)
    section = _extract_section(text)

    results: list[dict[str, Any]] = []
    chunk_index = start_index

    for chunk in chunks:
        metadata = {
            "source_doc": source_doc,
            "section": section,
            "page": page_number,
            "language": language,
            "char_count": len(chunk),
            "chunk_index": chunk_index,
        }
        results.append({"text": chunk, "metadata": metadata})
        chunk_index += 1

    return results, chunk_index

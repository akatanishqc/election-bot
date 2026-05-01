"""PDF ingestion pipeline for local vector indexing."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.generativeai import configure, embed_content
from langdetect import detect
from pinecone import Pinecone
from pypdf import PdfReader

from chunker import chunk_page_text


SUPPORTED_LANGUAGES = {"en", "hi", "ta", "bn", "te", "ml", "as"}
NAMESPACE = "eci_docs"
EMBED_MODEL = "models/text-embedding-004"
EMBED_TASK = "RETRIEVAL_DOCUMENT"


def _slugify_filename(filename: str) -> str:
    """Normalizes a filename for vector IDs."""

    stem = Path(filename).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "doc"


def _detect_language(text: str) -> str:
    """Detects language code, defaulting to English."""

    try:
        detected = detect(text)
    except Exception:
        return "en"

    return detected if detected in SUPPORTED_LANGUAGES else "en"


def _embed_with_retry(text: str) -> list[float]:
    """Embeds text with retry logic for rate limits."""

    delays = [2, 4, 8]
    last_error: Exception | None = None

    for delay in delays:
        try:
            result = embed_content(
                model=EMBED_MODEL,
                content=text,
                task_type=EMBED_TASK,
            )
            return result["embedding"]
        except Exception as exc:
            last_error = exc
            if "429" in str(exc):
                time.sleep(delay)
                continue
            raise

    raise RuntimeError("Embedding failed after retries") from last_error


def _append_failed_chunk(payload: dict[str, Any]) -> None:
    """Appends a failed chunk payload to the retry log."""

    failed_path = Path(__file__).parent / "failed_chunks.jsonl"
    with failed_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _load_pinecone_index() -> Any:
    """Initializes the Pinecone index client."""

    api_key = os.getenv("PINECONE_API_KEY", "")
    index_name = os.getenv("PINECONE_INDEX_NAME", "")
    if not api_key or not index_name:
        raise RuntimeError("Missing Pinecone configuration.")

    client = Pinecone(api_key=api_key)
    return client.Index(index_name)


def _filter_existing_ids(index: Any, ids: list[str]) -> set[str]:
    """Returns IDs already present in Pinecone."""

    if not ids:
        return set()
    result = index.fetch(ids=ids, namespace=NAMESPACE)
    return set(result.get("vectors", {}).keys())


def _ingest_pdf(
    pdf_path: Path,
    index: Any,
    incremental: bool,
) -> dict[str, Any]:
    """Processes a single PDF document."""

    source_doc = pdf_path.name
    slug = _slugify_filename(source_doc)
    errors = 0
    chunks: list[dict[str, Any]] = []
    chunk_index = 0

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            errors += 1
            print(f"[WARN] Failed to extract page {page_number} in {source_doc}")
            continue

        if not text.strip():
            continue

        language = _detect_language(text)
        page_chunks, chunk_index = chunk_page_text(
            text=text,
            source_doc=source_doc,
            page_number=page_number,
            language=language,
            start_index=chunk_index,
        )
        chunks.extend(page_chunks)

    vectors_upserted = 0

    for start in range(0, len(chunks), 100):
        batch = chunks[start : start + 100]
        batch_ids = [f"{slug}_{item['metadata']['chunk_index']}" for item in batch]

        if incremental:
            existing = _filter_existing_ids(index, batch_ids)
        else:
            existing = set()

        vectors = []
        for item, vector_id in zip(batch, batch_ids):
            if vector_id in existing:
                continue

            try:
                embedding = _embed_with_retry(item["text"])
            except Exception as exc:
                errors += 1
                print(f"[WARN] Embedding failed for {vector_id}: {exc}")
                continue

            metadata = dict(item["metadata"])
            metadata["text"] = item["text"]
            vectors.append({"id": vector_id, "values": embedding, "metadata": metadata})

        if not vectors:
            continue

        try:
            index.upsert(vectors=vectors, namespace=NAMESPACE)
            vectors_upserted += len(vectors)
        except Exception as exc:
            errors += len(vectors)
            print(f"[WARN] Pinecone upsert failed: {exc}")
            for vector in vectors:
                _append_failed_chunk(
                    {
                        "id": vector["id"],
                        "text": vector["metadata"].get("text", ""),
                        "metadata": vector["metadata"],
                        "error": str(exc),
                    }
                )

    return {
        "document": source_doc,
        "pages": total_pages,
        "chunks": len(chunks),
        "vectors": vectors_upserted,
        "errors": errors,
    }


def main() -> int:
    """Runs the PDF ingestion CLI."""

    parser = argparse.ArgumentParser(description="Ingest ECI PDFs into Pinecone.")
    parser.add_argument("--docs", required=True, help="Path to PDF directory.")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Skip already ingested vectors.",
    )
    args = parser.parse_args()

    load_dotenv()
    configure(api_key=os.getenv("GEMINI_API_KEY", ""))

    docs_path = Path(args.docs)
    if not docs_path.exists():
        raise RuntimeError("Documents path does not exist.")

    index = _load_pinecone_index()
    pdf_files = sorted(docs_path.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found.")
        return 0

    results = []
    for pdf_file in pdf_files:
        result = _ingest_pdf(pdf_file, index, args.incremental)
        results.append(result)

    print("| Document | Pages | Chunks | Vectors Upserted | Errors |")
    print("| --- | --- | --- | --- | --- |")
    for row in results:
        print(
            f"| {row['document']} | {row['pages']} | {row['chunks']} "
            f"| {row['vectors']} | {row['errors']} |"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

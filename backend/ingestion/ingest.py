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
from langdetect import detect
from pinecone import Pinecone
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from chunker import chunk_page_text

SUPPORTED_LANGUAGES = {"en", "hi", "ta", "bn", "te", "ml", "as"}
NAMESPACE = "eci_docs"

_embed_model: SentenceTransformer | None = None


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        print("Loading embedding model...")
        _embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("Model loaded.")
    return _embed_model


def _slugify_filename(filename: str) -> str:
    stem = Path(filename).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "doc"


def _detect_language(text: str) -> str:
    try:
        detected = detect(text)
    except Exception:
        return "en"
    return detected if detected in SUPPORTED_LANGUAGES else "en"


def _embed_text(text: str) -> list[float]:
    model = _get_embed_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def _append_failed_chunk(payload: dict[str, Any]) -> None:
    failed_path = Path(__file__).parent / "failed_chunks.jsonl"
    with failed_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _load_pinecone_index() -> Any:
    api_key = os.getenv("PINECONE_API_KEY", "")
    index_name = os.getenv("PINECONE_INDEX_NAME", "")
    if not api_key or not index_name:
        raise RuntimeError("Missing Pinecone configuration.")
    client = Pinecone(api_key=api_key)
    return client.Index(index_name)


def _filter_existing_ids(index: Any, ids: list[str]) -> set[str]:
    if not ids:
        return set()
    result = index.fetch(ids=ids, namespace=NAMESPACE)
    return set(result.get("vectors", {}).keys())


def _ingest_pdf(pdf_path: Path, index: Any, incremental: bool) -> dict[str, Any]:
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
        batch = chunks[start: start + 100]
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
                embedding = _embed_text(item["text"])
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
            print(f"  Upserted {vectors_upserted} vectors so far...")
        except Exception as exc:
            errors += len(vectors)
            print(f"[WARN] Pinecone upsert failed: {exc}")
            for vector in vectors:
                _append_failed_chunk({
                    "id": vector["id"],
                    "text": vector["metadata"].get("text", ""),
                    "metadata": vector["metadata"],
                    "error": str(exc),
                })

    return {
        "document": source_doc,
        "pages": total_pages,
        "chunks": len(chunks),
        "vectors": vectors_upserted,
        "errors": errors,
    }


def main() -> int:
    print("DEBUG: main() started", flush=True)
    parser = argparse.ArgumentParser(description="Ingest ECI PDFs into Pinecone.")
    parser.add_argument("--docs", required=True, help="Path to PDF directory.")
    parser.add_argument("--incremental", action="store_true",
                        help="Skip already ingested vectors.")
    args = parser.parse_args()
    print(f"DEBUG: args parsed, docs={args.docs}", flush=True)
    load_dotenv()

    docs_path = Path(args.docs)
    if not docs_path.exists():
        raise RuntimeError("Documents path does not exist.")

    index = _load_pinecone_index()
    pdf_files = sorted(docs_path.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found.")
        return 0

    print(f"Found {len(pdf_files)} PDF(s). Starting ingestion...\n")
    results = []
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        result = _ingest_pdf(pdf_file, index, args.incremental)
        results.append(result)
        print(f"  Done: {result['vectors']} vectors, {result['errors']} errors\n")

    print("\n| Document | Pages | Chunks | Vectors Upserted | Errors |")
    print("| --- | --- | --- | --- | --- |")
    for row in results:
        print(f"| {row['document']} | {row['pages']} | {row['chunks']} "
              f"| {row['vectors']} | {row['errors']} |")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
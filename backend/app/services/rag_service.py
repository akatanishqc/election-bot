"""RAG query pipeline: embed → retrieve → generate → format."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import List

import httpx

from ..dependencies import get_pinecone_index
from ..prompts.system_prompt import (
    COMPLIANCE_FOOTER,
    FULL_SYSTEM_PROMPT,
    PAUSED_MESSAGE,
    REFUSAL_MESSAGE,
    RESTRICTED_SYSTEM_PROMPT,
)

SIMILARITY_THRESHOLD = 0.75
TOP_K = 5
PINECONE_NAMESPACE = "eci_docs"

HF_API_URL = "https://api-inference.huggingface.co/models"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHAT_MODEL = "deepseek-ai/DeepSeek-V3"


@dataclass
class RagResult:
    reply: str
    sources: List[dict] = field(default_factory=list)
    was_refused: bool = False


def _get_hf_headers() -> dict:
    return {"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY', '')}"}


async def process_query(query: str, language: str, bot_mode: str) -> RagResult:
    if bot_mode == "PAUSED":
        return RagResult(reply=PAUSED_MESSAGE, was_refused=True)

    query_embedding = await _embed_query(query)
    chunks = await retrieve_context(query_embedding)

    above_threshold = [c for c in chunks if c["score"] >= SIMILARITY_THRESHOLD]
    if not above_threshold:
        return RagResult(reply=REFUSAL_MESSAGE, was_refused=True)

    context_str = build_context_string(above_threshold)
    raw_reply = await call_llm(context_str, query, bot_mode)

    sources = [
        {"source_doc": c["source_doc"], "section": c["section"], "page": c["page"]}
        for c in above_threshold
    ]
    reply_with_footer = append_compliance_footer(raw_reply, sources)
    return RagResult(reply=reply_with_footer, sources=sources, was_refused=False)


async def _embed_query(query: str) -> List[float]:
    """Generates embedding using HuggingFace feature-extraction pipeline."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2",
            headers=_get_hf_headers(),
            json={"inputs": query},
        )
        response.raise_for_status()
        result = response.json()
        # Returns nested list — flatten if needed
        if isinstance(result[0], list):
            return result[0]
        return result


async def retrieve_context(query_embedding: List[float]) -> List[dict]:
    index = get_pinecone_index()
    loop = asyncio.get_event_loop()

    response = await loop.run_in_executor(
        None,
        lambda: index.query(
            vector=query_embedding,
            top_k=TOP_K,
            namespace=PINECONE_NAMESPACE,
            include_metadata=True,
        ),
    )

    chunks = []
    for match in response.matches:
        meta = match.metadata or {}
        chunks.append({
            "text": meta.get("text", ""),
            "score": match.score,
            "source_doc": meta.get("source_doc", "ECI Document"),
            "section": meta.get("section", ""),
            "page": meta.get("page", 0),
        })
    return sorted(chunks, key=lambda c: c["score"], reverse=True)


def build_context_string(chunks: List[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        header = (
            f"[Context {i} | Source: {chunk['source_doc']}, "
            f"Section: {chunk['section']}, Page: {chunk['page']}]"
        )
        parts.append(f"{header}\n{chunk['text']}")
    return "\n\n".join(parts)


async def call_llm(context: str, query: str, bot_mode: str) -> str:
    """Calls DeepSeek-V3 via HuggingFace Inference API."""
    system_prompt = (
        RESTRICTED_SYSTEM_PROMPT if bot_mode == "RESTRICTED" else FULL_SYSTEM_PROMPT
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"[CONTEXT]\n{context}\n\n"
        f"[USER QUERY]\n{query}"
    )

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{HF_API_URL}/{CHAT_MODEL}",
            headers=_get_hf_headers(),
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": 0.1,
                    "return_full_text": False,
                }
            },
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "").strip()
        return str(result).strip()


def append_compliance_footer(response: str, sources: List[dict]) -> str:
    if not sources:
        source_str = "ECI official documents"
    else:
        parts = [
            f"{s['source_doc']}, p.{s['page']}"
            for s in sources
            if s.get("source_doc")
        ]
        source_str = " | ".join(parts) if parts else "ECI official documents"

    footer = COMPLIANCE_FOOTER.format(sources=source_str)
    return f"{response}{footer}"
"""RAG query pipeline: embed → retrieve → generate → format."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import List

import google.generativeai as genai

from ..dependencies import get_gemini_model, get_pinecone_index
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


@dataclass
class RagResult:
    reply: str
    sources: List[dict] = field(default_factory=list)
    was_refused: bool = False


async def process_query(query: str, language: str, bot_mode: str) -> RagResult:
    """
    Main entry point. Embeds the query, retrieves context from Pinecone,
    calls Gemini, and returns a structured result.
    """
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
    """Generates a query embedding using text-embedding-004."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="RETRIEVAL_QUERY",
        ),
    )
    return result["embedding"]


async def retrieve_context(query_embedding: List[float]) -> List[dict]:
    """
    Queries Pinecone for the top-K most similar chunks.
    Returns list of dicts sorted by score descending.
    """
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
        chunks.append(
            {
                "text": meta.get("text", ""),
                "score": match.score,
                "source_doc": meta.get("source_doc", "ECI Document"),
                "section": meta.get("section", ""),
                "page": meta.get("page", 0),
            }
        )
    return sorted(chunks, key=lambda c: c["score"], reverse=True)


def build_context_string(chunks: List[dict]) -> str:
    """Formats retrieved chunks into a labelled context block for the LLM."""
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        header = (
            f"[Context {i} | Source: {chunk['source_doc']}, "
            f"Section: {chunk['section']}, Page: {chunk['page']}]"
        )
        parts.append(f"{header}\n{chunk['text']}")
    return "\n\n".join(parts)


async def call_llm(context: str, query: str, bot_mode: str) -> str:
    """
    Calls Gemini 2.5 Flash-Lite with the appropriate system prompt.
    temperature=0.0 is set at model init in dependencies.py.
    """
    system_prompt = (
        RESTRICTED_SYSTEM_PROMPT if bot_mode == "RESTRICTED" else FULL_SYSTEM_PROMPT
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"[CONTEXT]\n{context}\n\n"
        f"[USER QUERY]\n{query}"
    )

    model = get_gemini_model()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: model.generate_content(full_prompt),
    )
    return response.text.strip()


def append_compliance_footer(response: str, sources: List[dict]) -> str:
    """Appends the mandatory ECI compliance footer to every response."""
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
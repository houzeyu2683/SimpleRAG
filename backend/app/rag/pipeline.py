from __future__ import annotations
from collections.abc import AsyncGenerator
from dataclasses import dataclass

import httpx
import structlog

from app.core.config import get_settings
from app.rag.embedder.local_embedder import embed_query
from app.rag.embedder.sparse_embedder import embed_sparse_query
from app.rag.generator.ollama_client import stream_chat
from app.rag.generator.prompt_builder import build_messages
from app.rag.retriever.qdrant_retriever import search
from app.rag.retriever.reranker import rerank

log = structlog.get_logger()
settings = get_settings()


@dataclass
class Citation:
    file_id: str
    page: int
    snippet: str
    score: float
    chunk_type: str


@dataclass
class RAGEvent:
    type: str  # "token" | "citations" | "done" | "error"
    data: str | list[dict] | None = None


async def query_stream(
    query: str,
    collection_name: str,
    file_id: str | None = None,
    history: list[dict] | None = None,
) -> AsyncGenerator[RAGEvent, None]:
    # 1. Embed query — dense (bge-m3) + sparse (BM25)
    query_vector = embed_query(query)
    query_sparse = embed_sparse_query(query)

    # 2. Hybrid retrieve from Qdrant (dense + BM25 → RRF fusion)
    hits = search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_sparse=query_sparse,
        top_k=settings.rag_retrieval_top_k,
        file_id=file_id,
    )

    if not hits:
        yield RAGEvent(type="error", data="No relevant documents found.")
        return

    # 3. Rerank
    reranked = rerank(query, hits, top_n=settings.rag_rerank_top_n)

    # 4. Emit citations
    citations = [
        {
            "file_id": h["file_id"],
            "page": h["page"],
            "snippet": h["text"][:300],
            "score": round(h["score"], 4),
            "chunk_type": h["chunk_type"],
            "preview_url": f"/api/v1/documents/{h['file_id']}/page?page={h['page']}",
        }
        for h in reranked
    ]
    yield RAGEvent(type="citations", data=citations)

    # 5. Build prompt and stream LLM response
    messages = build_messages(query, reranked, history=history)
    try:
        async for token in stream_chat(messages):
            yield RAGEvent(type="token", data=token)
    except httpx.TimeoutException:
        log.warning("rag.pipeline.llm_timeout", query=query[:60])
        yield RAGEvent(type="error", data="LLM response timed out. Please try again.")
        return
    except httpx.HTTPStatusError as exc:
        log.error("rag.pipeline.llm_http_error", status=exc.response.status_code)
        yield RAGEvent(type="error", data=f"LLM service error ({exc.response.status_code}). Please try again.")
        return
    except Exception as exc:
        log.error("rag.pipeline.llm_error", error=str(exc))
        yield RAGEvent(type="error", data="Unexpected LLM error. Please try again.")
        return

    yield RAGEvent(type="done")
    log.info("rag.pipeline.done", query=query[:60], citations=len(citations))

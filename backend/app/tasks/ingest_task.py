from __future__ import annotations
import json
from pathlib import Path

import redis
import structlog
from sqlalchemy import create_engine, text

from app.core.config import get_settings
from app.tasks.celery_app import celery_app

log = structlog.get_logger()
settings = get_settings()

# Sync engine for Celery worker (aiomysql → pymysql)
_sync_db_url = settings.database_url.replace("mysql+aiomysql://", "mysql+pymysql://")
_sync_engine = create_engine(_sync_db_url, pool_pre_ping=True, pool_size=2)


def _publish(r: redis.Redis, user_id: int, event: dict) -> None:
    r.publish(f"ingest:{user_id}", json.dumps(event))


def _get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def _db_update(
    file_id: str,
    status: str,
    page_count: int | None = None,
    chunk_count: int | None = None,
    error_message: str | None = None,
) -> None:
    sets = ["status = :status"]
    params: dict = {"status": status, "file_id": file_id}
    if page_count is not None:
        sets.append("page_count = :page_count")
        params["page_count"] = page_count
    if chunk_count is not None:
        sets.append("chunk_count = :chunk_count")
        params["chunk_count"] = chunk_count
    if error_message is not None:
        sets.append("error_message = :error_message")
        params["error_message"] = error_message[:500]

    sql = text(f"UPDATE documents SET {', '.join(sets)} WHERE id = :file_id")
    with _sync_engine.begin() as conn:
        conn.execute(sql, params)


@celery_app.task(bind=True, name="app.tasks.ingest_task.ingest_document")
def ingest_document(
    self,
    file_id: str,
    pdf_path: str,
    collection_name: str,
    user_id: int,
) -> dict:
    from app.rag.parser.pdf_parser import parse_pdf
    from app.rag.parser.chunker import chunk_parsed_document
    from app.rag.embedder.local_embedder import embed_texts
    from app.rag.embedder.sparse_embedder import embed_sparse
    from app.rag.retriever.qdrant_retriever import upsert_chunks

    r = _get_redis()

    def update_status(status: str, detail: str = "") -> None:
        _publish(r, user_id, {"file_id": file_id, "status": status, "detail": detail})
        _db_update(file_id, status=status)
        log.info("ingest.status", file_id=file_id, status=status)

    try:
        # ── 1. Parsing ────────────────────────────────────────────────────────
        update_status("parsing")
        data_dir = Path(settings.data_dir)
        parse_result = parse_pdf(Path(pdf_path), file_id, data_dir)

        # ── 2. Chunking ───────────────────────────────────────────────────────
        update_status("chunking")
        chunks = chunk_parsed_document(parse_result.chunks, file_id, collection_name)

        if not chunks:
            _db_update(file_id, status="failed", error_message="No text content found")
            _publish(r, user_id, {"file_id": file_id, "status": "failed", "detail": "No text content found"})
            return {"status": "failed", "file_id": file_id}

        # ── 3. Embedding ──────────────────────────────────────────────────────
        update_status("embedding")
        texts = [c.text for c in chunks]
        dense_embeddings = embed_texts(texts, batch_size=64)
        sparse_embeddings = embed_sparse(texts)

        # ── 4. Upsert to Qdrant ───────────────────────────────────────────────
        update_status("indexing")
        upsert_chunks(collection_name, chunks, dense_embeddings, sparse_embeddings)

        # ── 5. Done ───────────────────────────────────────────────────────────
        _db_update(
            file_id,
            status="done",
            page_count=parse_result.page_count,
            chunk_count=len(chunks),
        )
        _publish(r, user_id, {
            "file_id": file_id,
            "status": "done",
            "detail": f"Indexed {len(chunks)} chunks from {parse_result.page_count} pages",
        })
        log.info("ingest.done", file_id=file_id, chunks=len(chunks), pages=parse_result.page_count)
        return {
            "status": "done",
            "file_id": file_id,
            "chunk_count": len(chunks),
            "page_count": parse_result.page_count,
        }

    except Exception as exc:
        log.exception("ingest.failed", file_id=file_id, error=str(exc))
        _db_update(file_id, status="failed", error_message=str(exc)[:500])
        _publish(r, user_id, {"file_id": file_id, "status": "failed", "detail": str(exc)})
        raise self.retry(exc=exc, countdown=0, max_retries=0)

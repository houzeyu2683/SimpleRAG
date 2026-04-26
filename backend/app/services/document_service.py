from __future__ import annotations
import shutil
import uuid
from pathlib import Path

import aiofiles
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.document import Document, DocumentStatus
from app.rag.retriever.qdrant_retriever import delete_by_file_id

log = structlog.get_logger()
settings = get_settings()


async def save_upload(file_bytes: bytes, filename: str) -> tuple[str, Path]:
    file_id = str(uuid.uuid4())
    dest_dir = Path(settings.upload_dir) / file_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    async with aiofiles.open(dest, "wb") as f:
        await f.write(file_bytes)
    return file_id, dest


async def create_document(
    db: AsyncSession,
    file_id: str,
    filename: str,
    collection_id: int,
    owner_id: int,
) -> Document:
    doc = Document(
        id=file_id,
        filename=filename,
        collection_id=collection_id,
        owner_id=owner_id,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.flush()
    return doc


async def trigger_ingest(
    file_id: str,
    pdf_path: Path,
    collection_name: str,
    user_id: int,
) -> None:
    from app.tasks.ingest_task import ingest_document
    ingest_document.apply_async(
        kwargs={
            "file_id": file_id,
            "pdf_path": str(pdf_path),
            "collection_name": collection_name,
            "user_id": user_id,
        },
        queue="ingest",
    )
    log.info("ingest.triggered", file_id=file_id)


async def get_document(db: AsyncSession, file_id: str) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == file_id))
    return result.scalar_one_or_none()


async def list_documents(
    db: AsyncSession,
    collection_id: int | None = None,
    owner_id: int | None = None,
) -> list[Document]:
    query = select(Document)
    if collection_id:
        query = query.where(Document.collection_id == collection_id)
    if owner_id:
        query = query.where(Document.owner_id == owner_id)
    result = await db.execute(query.order_by(Document.created_at.desc()))
    return list(result.scalars().all())


async def delete_document(
    db: AsyncSession, file_id: str, collection_name: str
) -> None:
    doc = await get_document(db, file_id)
    if not doc:
        raise ValueError("Document not found")

    # Remove vectors from Qdrant
    delete_by_file_id(collection_name, file_id)

    # Remove files from disk
    upload_path = Path(settings.upload_dir) / file_id
    if upload_path.exists():
        shutil.rmtree(upload_path)

    data_path = Path(settings.data_dir) / file_id
    if data_path.exists():
        shutil.rmtree(data_path)

    await db.delete(doc)
    await db.flush()
    log.info("document.deleted", file_id=file_id)

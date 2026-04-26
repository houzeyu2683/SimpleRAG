from __future__ import annotations
from pathlib import Path

import fitz
import structlog
from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import CurrentUser, DbDep, MediaUser
from app.schemas.document import DocumentResponse, DocumentStatusResponse
from app.services import collection_service, document_service

log = structlog.get_logger()
router = APIRouter()

_ALLOWED_MIME = {"application/pdf"}
_MAX_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    collection_id: int,
    current_user: CurrentUser,
    db: DbDep,
):
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF files are accepted")

    content = await file.read()
    if len(content) > _MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 50 MB)")

    collection = await collection_service.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    file_id, pdf_path = await document_service.save_upload(content, file.filename or "upload.pdf")
    doc = await document_service.create_document(db, file_id, file.filename or "upload.pdf", collection_id, current_user.id)

    await document_service.trigger_ingest(
        file_id=file_id,
        pdf_path=pdf_path,
        collection_name=collection.qdrant_collection,
        user_id=current_user.id,
    )

    log.info("document.uploaded", file_id=file_id, filename=file.filename)
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: CurrentUser,
    db: DbDep,
    collection_id: int | None = Query(None),
):
    docs = await document_service.list_documents(
        db,
        collection_id=collection_id,
        owner_id=None if current_user.role.name == "admin" else current_user.id,
    )
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{file_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(file_id: str, _: CurrentUser, db: DbDep):
    doc = await document_service.get_document(db, file_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentStatusResponse(
        id=doc.id,
        status=doc.status,
        page_count=doc.page_count,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
    )


@router.get("/{file_id}/page")
async def get_document_page(
    file_id: str,
    page: int = Query(1, ge=1),
    _: MediaUser = None,
    db: DbDep = None,
):
    """Render a PDF page as PNG and return it."""
    from app.core.config import get_settings
    settings = get_settings()

    doc_record = await document_service.get_document(db, file_id)
    if not doc_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    upload_dir = Path(settings.upload_dir) / file_id
    pdf_files = list(upload_dir.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF file not found")

    try:
        with fitz.open(str(pdf_files[0])) as doc:
            if page < 1 or page > len(doc):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid page number")
            fitz_page = doc[page - 1]
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for readability
            pix = fitz_page.get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("page.render.failed", file_id=file_id, page=page, error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to render page")

    return Response(content=png_bytes, media_type="image/png")


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(file_id: str, current_user: CurrentUser, db: DbDep):
    doc = await document_service.get_document(db, file_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if doc.owner_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your document")

    collection = await collection_service.get_collection(db, doc.collection_id)
    qdrant_name = collection.qdrant_collection if collection else ""

    try:
        await document_service.delete_document(db, file_id, qdrant_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    collection_id: int
    owner_id: int
    page_count: int | None
    chunk_count: int | None
    status: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    id: str
    status: str
    page_count: int | None
    chunk_count: int | None
    error_message: str | None


class SearchRequest(BaseModel):
    query: str
    collection_name: str
    file_id: str | None = None
    top_k: int = 5


class SearchResult(BaseModel):
    text: str
    file_id: str
    page: int
    chunk_type: str
    score: float
    preview_url: str

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    title: str = "New Chat"
    collection_id: int


class SessionResponse(BaseModel):
    id: int
    title: str
    collection_id: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CitationSchema(BaseModel):
    citation_id: str
    file_id: str
    page: int
    snippet: str
    score: float
    chunk_type: str
    preview_url: str


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    citations: list[CitationSchema] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    content: str

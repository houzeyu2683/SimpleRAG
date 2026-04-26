from __future__ import annotations
import json
import uuid

import structlog
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DbDep
from app.rag.pipeline import query_stream
from app.schemas.chat import (
    CitationSchema,
    CreateSessionRequest,
    MessageResponse,
    SendMessageRequest,
    SessionResponse,
)
from app.services import chat_service, collection_service

log = structlog.get_logger()
router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(req: CreateSessionRequest, current_user: CurrentUser, db: DbDep):
    collection = await collection_service.get_collection(db, req.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    session = await chat_service.create_session(db, req.title, req.collection_id, current_user.id)
    return SessionResponse.model_validate(session)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(current_user: CurrentUser, db: DbDep):
    sessions = await chat_service.list_sessions(db, current_user.id)
    return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(session_id: int, current_user: CurrentUser, db: DbDep):
    session = await chat_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    return [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            citations=chat_service.parse_citations(m),
            created_at=m.created_at,
        )
        for m in session.messages
    ]


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    req: SendMessageRequest,
    current_user: CurrentUser,
    db: DbDep,
):
    session = await chat_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")

    collection = await collection_service.get_collection(db, session.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    # Persist user message
    await chat_service.save_message(db, session_id, "user", req.content)
    history = chat_service.build_history(session.messages)

    async def event_stream():
        full_response = []
        collected_citations: list[dict] = []

        async for event in query_stream(
            query=req.content,
            collection_name=collection.qdrant_collection,
            history=history,
        ):
            if event.type == "citations":
                citations = event.data or []
                collected_citations = [
                    {
                        "citation_id": str(uuid.uuid4()),
                        "file_id": c["file_id"],
                        "page": c["page"],
                        "snippet": c["snippet"],
                        "score": c["score"],
                        "chunk_type": c["chunk_type"],
                        "preview_url": c["preview_url"],
                    }
                    for c in citations
                ]
                payload = json.dumps({"type": "citations", "data": collected_citations})
                yield f"data: {payload}\n\n"

            elif event.type == "token":
                full_response.append(event.data)
                payload = json.dumps({"type": "token", "data": event.data})
                yield f"data: {payload}\n\n"

            elif event.type == "done":
                # Persist assistant message
                full_text = "".join(full_response)
                await chat_service.save_message(
                    db, session_id, "assistant", full_text, collected_citations or None
                )
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            elif event.type == "error":
                payload = json.dumps({"type": "error", "data": event.data})
                yield f"data: {payload}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: int, current_user: CurrentUser, db: DbDep):
    session = await chat_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.owner_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    await chat_service.delete_session(db, session_id)

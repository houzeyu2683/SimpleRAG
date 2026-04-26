from __future__ import annotations
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_session import ChatMessage, ChatSession


async def create_session(
    db: AsyncSession, title: str, collection_id: int, owner_id: int
) -> ChatSession:
    session = ChatSession(title=title, collection_id=collection_id, owner_id=owner_id)
    db.add(session)
    await db.flush()
    return session


async def list_sessions(db: AsyncSession, owner_id: int) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.owner_id == owner_id)
        .order_by(ChatSession.created_at.desc())
    )
    return list(result.scalars().all())


async def get_session(db: AsyncSession, session_id: int) -> ChatSession | None:
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, session_id: int) -> None:
    session = await get_session(db, session_id)
    if session:
        await db.delete(session)
        await db.flush()


async def save_message(
    db: AsyncSession,
    session_id: int,
    role: str,
    content: str,
    citations: list[dict] | None = None,
) -> ChatMessage:
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        citations=json.dumps(citations) if citations else None,
    )
    db.add(msg)
    await db.flush()
    return msg


def build_history(
    messages: list[ChatMessage],
    max_turns: int = 6,
    max_chars: int = 6000,
) -> list[dict]:
    """
    Return the most recent N turn-pairs as Ollama chat history.
    Also caps total character count to avoid exceeding LLM context window.
    """
    # Take last max_turns * 2 messages (each turn = user + assistant)
    recent = messages[-(max_turns * 2):]
    history = [{"role": m.role, "content": m.content} for m in recent]

    # Trim from the front if total chars exceed budget
    while history:
        total = sum(len(h["content"]) for h in history)
        if total <= max_chars:
            break
        history = history[2:]  # drop oldest turn-pair

    return history


def parse_citations(msg: ChatMessage) -> list[dict] | None:
    if not msg.citations:
        return None
    try:
        return json.loads(msg.citations)
    except json.JSONDecodeError:
        return None

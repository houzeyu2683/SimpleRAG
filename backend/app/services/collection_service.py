from __future__ import annotations
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.collection import Collection
from app.rag.retriever.qdrant_retriever import ensure_collection, delete_by_file_id, get_client


def _to_qdrant_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:60] or "collection"


async def create_collection(
    db: AsyncSession, name: str, description: str | None, owner_id: int
) -> Collection:
    qdrant_name = _to_qdrant_name(name)

    existing = await db.execute(
        select(Collection).where(Collection.qdrant_collection == qdrant_name)
    )
    if existing.scalar_one_or_none():
        raise ValueError(f"Collection '{name}' already exists")

    collection = Collection(
        name=name,
        description=description,
        qdrant_collection=qdrant_name,
        owner_id=owner_id,
    )
    db.add(collection)
    await db.flush()
    ensure_collection(qdrant_name)
    return collection


async def list_collections(db: AsyncSession) -> list[Collection]:
    result = await db.execute(select(Collection).options(selectinload(Collection.owner)))
    return list(result.scalars().all())


async def get_collection(db: AsyncSession, collection_id: int) -> Collection | None:
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    return result.scalar_one_or_none()


async def delete_collection(db: AsyncSession, collection_id: int) -> None:
    collection = await get_collection(db, collection_id)
    if not collection:
        raise ValueError("Collection not found")

    client = get_client()
    existing = {c.name for c in client.get_collections().collections}
    if collection.qdrant_collection in existing:
        client.delete_collection(collection.qdrant_collection)

    await db.delete(collection)
    await db.flush()

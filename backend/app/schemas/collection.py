from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class CreateCollectionRequest(BaseModel):
    name: str
    description: str | None = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    qdrant_collection: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
